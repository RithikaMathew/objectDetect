"""Regression tests use saved evidence; no inference or synthetic metric scale."""
import copy
import json
import shutil
from pathlib import Path
import numpy as np
import pytest
from pipeline import generate_near_miss_report as report
from pipeline.manual_occlusion_metrics import (manual_samples, observed_method, with_velocity,
                                               metrics_for, interpolate_method, filtered_method)
from clearance_metrics import collision_ttc, diagnose_pair

ROOT = Path(__file__).resolve().parents[1]

@pytest.fixture(scope='module')
def generated(tmp_path_factory):
    out=tmp_path_factory.mktemp('near_miss')
    shutil.copytree(ROOT/'reports/near_miss/inputs',out/'inputs')
    report.build_report(ROOT,out,json.loads((ROOT/'pipeline/near_miss_screening.json').read_text()))
    return out


def test_unique_real_candidates_survive_geometry_failure(generated):
    events=report.read(generated/'event_metrics.csv')
    assert {e['event_id'] for e in events} == {'white_suv','dark_car','pedestrian_car'}
    assert len(events)==3
    pairs=report.read(generated/'pair_eligibility.csv')
    assert [int(r['simultaneous_samples']) for r in pairs]==[58,98]
    for r in pairs:
        assert r['alongside_samples']=='0' and r['supported_samples']=='0'
        assert 'failed_alongside_gate' in r['rejection_reasons']
        assert 'outside_calibration_support' in r['rejection_reasons']
        assert r['same_direction_samples']==r['simultaneous_samples']


def test_false_wheel_and_no_car_are_excluded(generated):
    ex=report.read(generated/'excluded_candidates.csv')
    assert any(r['vehicle_id']=='21' and r['decision']=='excluded_false_object' for r in ex)
    assert any(r['clip_id']=='colonial_125311' and r['decision']=='not_a_pass_in_reviewed_interval' for r in ex)
    assert all('21' not in r['object_ids'] for r in report.read(generated/'event_metrics.csv'))


def test_metrics_nulls_have_reasons_and_units(generated):
    for e in report.read(generated/'event_metrics.csv'):
        assert e['min_clearance_m']=='' and e['ttc_s']=='' and e['pet_s']==''
        assert json.loads(e['null_reason'])['min_clearance_m'].startswith('not_calibrated')
        assert float(e['min_image_gap_px'])>0 and e['image_gap_method']
        assert e['reviewed_classification'] in {'indeterminate','potential_conflict','not_conflict','confirmed_under_defined_protocol'}


def test_historical_pet_was_coverage_not_seconds(generated):
    rows=report.read(generated/'historical_reproduction.csv');obs=rows[0]
    assert obs['samples']=='5'
    assert float(obs['coverage_fraction']) == pytest.approx(5/17)
    assert obs['pet_s']==''
    cv=next(r for r in rows if r['method']=='constant_velocity')
    assert float(cv['min_ttc_s']) == pytest.approx(.37452971299897336)
    event=report.read(generated/'event_metrics.csv')[-1]
    assert event['historical_pet_s']=='.294' and event['reproduced_surrogate_pet_s']==''
    assert float(event['reproduced_surrogate_ttc_s'])==pytest.approx(.3718037100975292)


def test_reconstruction_reproducible_from_exported_positions(generated):
    rr=[r for r in report.read(generated/'reconstruction_inputs.csv') if r['method']=='constant_velocity']
    axis=np.array(json.loads((generated/'run_config.json').read_text())['road_axis'])
    basis=np.column_stack((axis,[-axis[1],axis[0]]));ttcs=[]
    for r in rr:
        rel=np.array([float(r['car_x_unvalidated'])-float(r['subject_x_unvalidated']),float(r['car_y_unvalidated'])-float(r['subject_y_unvalidated'])])@basis
        vel=np.array([float(r['car_vx_unvalidated'])-float(r['subject_vx_unvalidated']),float(r['car_vy_unvalidated'])-float(r['subject_vy_unvalidated'])])@basis
        t=collision_ttc(rel,vel,(np.array([.7,.6])+[4.5,1.8])/2)
        if t is not None:ttcs.append(t)
    assert min(ttcs)==pytest.approx(.3718037100975292)
    assert all('observed' not in r['observation_status'] for r in rr)


def test_occlusion_is_loss_not_no_vehicle_and_correct_namespace(generated):
    loss=report.read(generated/'occlusion_observations.csv')
    assert any(r['car68_status']=='observed' for r in loss)
    assert any(r['car68_status']=='not_observable_automatic_track_lost' for r in loss)
    comparisons=report.read(generated/'manual_auto_comparison.csv')
    assert sum(r['automatic_same_frame']=='True' for r in comparisons)==3
    assert all(r['same_frame_point_difference_px']=='' for r in comparisons if r['automatic_same_frame']=='False')
    event=report.read(generated/'event_metrics.csv')[-1]
    assert 'car 68 sensitive' in event['object_ids']


def test_no_endpoint_clamping_or_fake_observation():
    sample=[dict(frame=i+1,t=i*.05,xy=np.array([float(i),0.]),pixel=np.array([i,0]),inside=False) for i in range(8)]
    targets=sample+[dict(sample[-1],frame=30,t=2.)]
    result=filtered_method(sample,targets,False)
    assert result and max(r['t'] for r in result)<=sample[-1]['t']
    assert all(r['observation_status']=='interpolated_filtered' for r in result)
    result=interpolate_method(sample,targets,'constant_velocity')
    assert result[-1]['observation_status']=='extrapolated_through_occlusion_model_fit'


def test_frame_time_alignment_preserves_original_click_time():
    rows=[dict(object='car',frame=str(f),clip_seconds=str((f-1)/30+.01),x_px='1',y_px='2') for f in (1,2,3)]
    samples=manual_samples(rows,np.eye(3),30)
    assert samples[0]['t']==0 and samples[0]['click_time_s']==.01


def test_parallel_non_collision_course_has_no_ttc():
    assert collision_ttc(np.array([10.,4.]),np.array([-3.,0.]),np.array([3.,1.])) is None
    assert collision_ttc(np.array([10.,0.]),np.array([-3.,0.]),np.array([3.,1.])) == pytest.approx(7/3)


def test_thresholds_only_change_screening():
    event=dict(event_id='test',ttc_s=.4,pet_s=None,min_clearance_m=None,min_image_gap_px=6,reviewed_classification='indeterminate')
    original=copy.deepcopy(event)
    assert 'ttc_s_below' not in report.screening(event,{'ttc_s':.3})
    assert 'ttc_s_below_0.5' in report.screening(event,{'ttc_s':.5})
    assert event==original


def test_sensitivity_is_conditional_and_missing_values_survive(generated):
    rows=report.read(generated/'sensitivity_metrics.csv')
    assert len(rows)==80
    cv=[float(r['min_ttc_s']) for r in rows if r['method']=='constant_velocity']
    assert min(cv)==pytest.approx(.34769660340290454)
    assert max(cv)==pytest.approx(.3981078045921077)
    assert any(r['pet_s']=='' for r in rows)
    # Zero is legitimate modelled simultaneous occupancy under changed assumptions.
    assert any(r['pet_s']=='0.0' and r['scenario']!='baseline' for r in rows)


def test_evidence_hashes_and_schema(generated):
    provenance=report.read(generated/'provenance.csv')
    assert all(r['unchanged']=='True' and report.digest(ROOT/r['path'])==r['sha256'] for r in provenance)
    assert set(report.FIELDS).issubset(report.read(generated/'event_metrics.csv')[0])
    assert (generated/'PROFESSOR_RESULTS.md').read_text().startswith('# Colonial')
