import csv
import json
from pathlib import Path
import tempfile
import unittest
from eval_truth import match,load_identity_map
from labelled_lane_speed import zone_label,motion,speed_inventory,compare_speeds
from speed_gates import measure
from rf_person_review import score_frame,evaluate


class LabelledValidationTests(unittest.TestCase):
    def test_time_overlap_never_implies_verified_identity(self):
        truth=[dict(id='p1',s=600,e=614,c='pedestrian')]
        tracks=[dict(id='barricade',f=0,l=615,counted=1,lab='pedestrian'),dict(id='person',f=600,l=613,counted=1,lab='pedestrian')]
        self.assertEqual(match(truth,tracks)[0][0][1],'FOUND')
        self.assertEqual(match(truth,tracks,{})[0][0][1],'UNVERIFIED')
        result,extra=match(truth,tracks,{'p1':'person'})
        self.assertEqual(result[0][2]['id'],'person');self.assertEqual(extra[0]['id'],'barricade')

    def test_identity_approval_needs_full_review_and_evidence(self):
        with tempfile.TemporaryDirectory()as td:
            p=Path(td)/'review.csv'
            p.write_text('run,clip,truth_id,track_id,decision,full_track_reviewed,reviewer,evidence\nb4,night,p1,1,approved,,me,looks right\n')
            with self.assertRaises(ValueError):load_identity_map(p)

    def test_zones_scale_and_overlap_are_not_forced_to_a_lane(self):
        z=dict(ref_size=[100,100],bike=[[0,0],[50,0],[50,100],[0,100]],road=[[40,0],[100,0],[100,100],[40,100]])
        self.assertEqual(zone_label((20,50),z,[200,200]),'bike_lane')
        self.assertEqual(zone_label((90,50),z,[200,200]),'overlap')
        self.assertEqual(zone_label((220,50),z,[200,200]),'outside_frame')

    def test_image_motion_is_not_silently_converted_to_mph(self):
        samples=[dict(frame=str(i+1),foot_x=str(i*2),foot_y='10',box_h='20')for i in range(20)]
        r=motion(samples,10)
        self.assertGreater(r['body_heights_per_s'],0)
        self.assertEqual(r['mph'],'')

    def test_known_distance_crossing_speed_and_missing_crossing(self):
        samples=[dict(frame=str(i+1),foot_x=str(i),foot_y='5')for i in range(101)]
        with tempfile.TemporaryDirectory()as td:
            p=Path(td)/'gates.json';p.write_text(json.dumps(dict(site='Colonial North',recording_date='2019-07-10',
                ref_size=[100,100],reviewer='test',measurement_source='synthetic independent measurement',
                gates=[dict(facility='sidewalk',length_feet=30,line_a=[[20,0],[20,10]],line_b=[[80,0],[80,10]])])))
            r=measure(samples,10,p,[100,100]);self.assertAlmostEqual(r['mph'],3.409,places=3)
            self.assertEqual(measure(samples[:30],10,p,[100,100])['mph'],'')

    def test_real_workbook_colonial_records_deduplicated(self):
        path=Path(__file__).resolve().parents[4]/'Bike Lane Study Counts/bicyclist speeds.xlsx'
        if not path.exists():self.skipTest('Local source workbook unavailable')
        r=speed_inventory(path)
        self.assertEqual(len(r['unique_colonial_records']),23)
        self.assertEqual(sum('e-bike'in row['notes']for row in r['unique_colonial_records']),1)

    def test_speed_error_requires_identity_and_measured_mph(self):
        with tempfile.TemporaryDirectory()as td:
            p=Path(td)/'links.csv';p.write_text('clip,truth_id,record_number,facility,reviewer,evidence\nnight,n2,51,Bike Lane,me,verified matching original record\n')
            people=[dict(clip='night',truth_id='n2',identity_verified=0,speed_mph=12,metric_speed_facility='bike_lane')]
            refs=[dict(record_number='51',facility='Bike Lane',source_mph=10)]
            pairs,metrics=compare_speeds(people,refs,p)
            self.assertEqual(metrics['pairs'],0);self.assertIsNone(metrics['mae_mph'])
            people[0]['identity_verified']=1
            pairs,metrics=compare_speeds(people,refs,p)
            self.assertEqual(metrics['pairs'],1);self.assertEqual(metrics['mae_mph'],2)

    def test_detector_boxes_are_one_to_one_not_recovered_people(self):
        truth=[[0,0,10,10]];proposals=[dict(box=[0,0,10,10]),dict(box=[0,0,10,10])]
        self.assertEqual(score_frame(truth,proposals),(1,1,0))
        self.assertEqual(score_frame([],proposals),(0,2,0))

    def test_unreviewed_frame_is_never_assumed_empty(self):
        with tempfile.TemporaryDirectory()as td:
            p=Path(td);(p/'manifest.json').write_text(json.dumps(dict(frames=[dict(id='night:1',width=100,height=100,rf=[],dino=[])])))
            review=p/'review.json';review.write_text(json.dumps(dict(protocol='all_visible_person_boxes_v1',frames={'night:1':dict(reviewed=False,boxes=[])})))
            with self.assertRaises(ValueError):evaluate(p,review,p/'out.md')


if __name__=='__main__':unittest.main()
