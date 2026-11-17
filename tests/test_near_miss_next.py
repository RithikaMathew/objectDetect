import copy
import json
from pathlib import Path
import re
import subprocess
import pytest
from pipeline import near_miss_next as nxt

ROOT=Path(__file__).resolve().parents[1]

@pytest.fixture(scope='module')
def package(tmp_path_factory):
    out=tmp_path_factory.mktemp('near_miss_next')
    nxt.build(ROOT,out)
    data=json.loads((out/'review_data.json').read_text())
    return out,data


def test_unique_events_existing_evidence_and_negative_controls(package):
    out,data=package
    assert len(data['events'])==3
    assert [e['metrics']['synchronized_observed_count'] for e in data['events'][:2]]==[58,98]
    a=data['annotations']['events']
    assert [r['selected_min_edge_gap_px'] for r in nxt.read(out/'event_metrics.csv')]==['6.0','20.0','']
    assert sum(len(e['edges']) for e in a)==6
    assert not any(e['occupancy'] for e in a)
    assert len(nxt.read(out/'negative_controls.csv'))==2
    assert all(e['metrics']['review_label'] in ('indeterminate','potential_conflict') for e in data['events'])


def test_pts_audited_without_absolute_clock_correction(package):
    out,data=package
    audit=nxt.read(out/'timing_audit.csv')
    assert all(r['nonpositive_intervals']=='0' for r in audit)
    assert all(r['intervals_above_1_5_median']=='0' for r in audit)
    for e in data['events']:
        assert e['pts'][0]==0
        assert e['metrics']['absolute_clock_status'].startswith('unresolved')
        assert all(e['pts'][r['frame']-1]==r['t_s'] for r in e['subject'])


def test_coverage_denominators_and_unknown_visibility(package):
    out,data=package
    for e in data['events']:
        m=e['metrics'];assert m['expected_frame_count']==m['analysis_last_frame']-m['analysis_first_frame']+1
        assert m['synchronized_observed_pct']==pytest.approx(100*m['synchronized_observed_count']/m['expected_frame_count'])
        assert m['verified_visible_frame_count'] is None
    ped=data['events'][-1]
    assert ped['metrics']['car_last_observed_frame']==1395
    assert ped['metrics']['car_namespace']=='sensitive'
    assert ped['car_missing_spans']
    assert any(r['last_frame']==1411 for r in ped['car_missing_spans'])


def test_conditional_ttc_recomputed_and_physical_metrics_missing(package):
    _,data=package
    for e in data['events']:
        assert e['metrics']['physical_clearance_m'] is None
        assert e['metrics']['physical_ttc_s'] is None
        assert e['metrics']['pet_s'] is None
    m=data['events'][-1]['metrics']
    assert m['conditional_ttc_s']==pytest.approx(.371804,abs=3e-6)
    assert m['historical_conditional_ttc_s']==pytest.approx(.3718037100975292)
    assert m['pet_eligibility']=='not_observable'


def fixture_annotation(e):
    a=dict(event_id=e['event_id'],source_sha256=e['source_sha256'],reviewer='synthetic test only',notes='',edges=[],footprints=[],zone=dict(points=[[1,1],[40,1],[40,40],[1,40]],physical_identity_confirmed=True,justification='Synthetic physical zone assumption'),occupancy={})
    for k,lo,hi in [('pedestrian_exit',1380,1381),('car_entry',1390,1391)]:a['occupancy'][k]=dict(frame_low=lo,frame_high=hi,boundary_supported=True,visibility='visible',notes='Synthetic neighboring-frame evidence')
    return a


def test_pet_formula_coverage_independence_and_js_parity(package):
    _,data=package;e=data['events'][-1];a=fixture_annotation(e);r=nxt.reviewed_pet(e,a)
    assert r['pet_eligibility']=='supported_interval'
    assert r['pet_lower_s']==pytest.approx(e['pts'][1389]-e['pts'][1380])
    a['coverage_fraction']=5/17
    assert nxt.reviewed_pet(e,a)==r
    code="const E=require('./pipeline/near_miss_validation_engine.js');const x=JSON.parse(require('fs').readFileSync(0,'utf8'));process.stdout.write(JSON.stringify(E.pet(x.event,x.annotation)));"
    result=subprocess.run(['node','-e',code],input=json.dumps(dict(event=e,annotation=a)),text=True,capture_output=True,check=True,cwd=ROOT)
    assert json.loads(result.stdout)==r


def test_pet_missing_overlap_and_uncertain_bounds(package):
    _,data=package;e=data['events'][-1];a=fixture_annotation(e)
    a['zone']['physical_identity_confirmed']=False;assert nxt.reviewed_pet(e,a)['pet_s'] is None
    a=fixture_annotation(e);a['occupancy']['pedestrian_exit'],a['occupancy']['car_entry']=a['occupancy']['car_entry'],a['occupancy']['pedestrian_exit']
    assert nxt.reviewed_pet(e,a)['pet_eligibility']=='temporal_overlap'
    a=fixture_annotation(e);a['occupancy']['car_entry'].update(frame_low=1380,frame_high=1382)
    assert nxt.reviewed_pet(e,a)['pet_eligibility']=='order_uncertain'
    a=fixture_annotation(e);a['occupancy']['car_entry'].update(boundary_supported=False)
    assert nxt.reviewed_pet(e,a)['pet_eligibility']=='not_observable'


def test_annotation_import_regenerates_same_supported_intervals(tmp_path,package):
    _,data=package;e=copy.deepcopy(data['events'][-1]);a=fixture_annotation(e)
    source=tmp_path/'synthetic_review.json';source.write_text(json.dumps(dict(schema_version=1,events=[a])))
    config=tmp_path/'screening.json';config.write_text(json.dumps(dict(adopted_ttc_s=1.5,adopted_pet_s=.5)))
    out=tmp_path/'reviewed';nxt.build(ROOT,out,source,config)
    rows=nxt.read(out/'event_metrics.csv');ped=rows[-1]
    expected=nxt.reviewed_pet(e,a)
    assert float(ped['pet_lower_s'])==pytest.approx(expected['pet_lower_s'])
    assert ped['review_label']=='potential_conflict' and ped['physical_clearance_m']==''
    assert ped['conditional_ttc_screen_flag']=='True' and ped['supported_pet_screen_flag']=='True'
    assert [r['selected_min_edge_gap_px'] for r in rows[:2]]==['6.0','20.0']


def test_no_model_grid_pet_or_probabilities_in_new_exports(package):
    out,_=package
    rows=nxt.read(out/'conditional_scenarios.csv')
    assert len(rows)==70
    assert all(r['pet_s']=='' and r['eligible_physical_ttc']=='False' for r in rows)
    sweep=nxt.read(out/'threshold_sweep.csv')
    assert all(r['unique_event_denominator']=='3' and r['review_labels_changed']=='False' for r in sweep)
    assert all(r['eligible_metric_denominator']=='0' for r in sweep)


def test_offline_self_contained_assets_and_provenance(package):
    out,_=package;text=(out/'review_validation.html').read_text()
    assert text.count('data:video/mp4;base64,')==3
    assert '__ENGINE__' not in text and '__REVIEW_DATA__' not in text
    assert not re.search(r'<script[^>]+src=',text)
    assert all(r['unchanged']=='True' and nxt.digest(ROOT/r['path'])==r['sha256'] for r in nxt.read(out/'provenance.csv'))
    assert json.loads((out/'build_manifest.json').read_text())['source_files_unchanged']


def test_wrong_source_annotation_rejected(package):
    _,data=package;a=copy.deepcopy(data['annotations']);a['events'][0]['source_sha256']='incorrect'
    with pytest.raises(ValueError,match='hash mismatch'):nxt.validate_annotations(a,data['events'])


def test_capture_time_ambiguity_is_preserved(package):
    out,_=package
    rows=nxt.read(out/'annotation_alignment_audit.csv')
    mismatched=[r for r in rows if r['frame_delta']!='0']
    assert any(r['saved_frame']=='1382' and r['playback_time_decoded_frame']=='1381' for r in mismatched)


def test_physical_screen_threshold_is_rejected(tmp_path):
    cfg=tmp_path/'bad.json';cfg.write_text(json.dumps(dict(physical_clearance_m=1)))
    with pytest.raises(ValueError,match='physical scale unverified'):nxt.build(ROOT,tmp_path/'out',config_path=cfg)
