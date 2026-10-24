import csv
import json
from pathlib import Path
import tempfile
import unittest
from lane_use_report import summarize_track,report,merge,facility
from site_zone_setup import page,zone_key
from study_batch import select,build_plan

ROOT=Path(__file__).resolve().parents[1]

class SiteLaneReports(unittest.TestCase):
    def samples(self,xs):return [dict(track_id='1',frame=i+1,foot_x=x,foot_y=5,coasted=0)for i,x in enumerate(xs)]
    def zones(self):return dict(ref_size=[100,100],site='Test',road=[[0,0],[40,0],[40,100],[0,100]],sidewalk=[[50,0],[99,0],[99,99],[50,99]])

    def test_unknown_camera_stays_unassigned(self):
        self.assertEqual(summarize_track(self.samples([10]*4),None,[100,100])[0],'unassigned')

    def test_real_lane_change_is_not_double_counted_as_two_people(self):
        label,n,fractions=summarize_track(self.samples([10,10,60,60]),self.zones(),[100,100])
        self.assertEqual(label,'uncertain');self.assertEqual(fractions,{'road':.5,'sidewalk':.5})

    def test_same_facility_extra_regions_do_not_create_false_overlap(self):
        z=self.zones();z['extra_regions']=[dict(facility='road',polygon=z['road'])]
        self.assertEqual(facility((10,5),z,[100,100]),'road')
        z['bike']=z['road'];self.assertEqual(facility((10,5),z,[100,100]),'overlap')

    def csv(self,path,rows):
        with path.open('w',newline='')as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

    def test_person_vehicle_counts_and_site_ledger_preserve_namespaces(self):
        with tempfile.TemporaryDirectory()as td:
            d=Path(td);self.csv(d/'tracks.csv',[dict(track_id='1',label='PEDESTRIAN',counted=1)])
            self.csv(d/'people.csv',self.samples([60]*4))
            self.csv(d/'vehicles.csv',[{**r,'label':'car','counted':1}for r in self.samples([10]*4)])
            log=dict(tracks_csv=str(d/'tracks.csv'),trajectories_csv=str(d/'people.csv'),vehicle_trajectories_csv=str(d/'vehicles.csv'),
                     clip_start_clock='2019-08-28 12:00:00',fps=10,resolution=[100,100],video_path='/raw/test.mp4',params={'run':'test'},final_counts={'bicyclists':0,'pedestrians':1,'vehicles':1})
            (d/'log.json').write_text(json.dumps(log));(d/'zones.json').write_text(json.dumps(self.zones()))
            report(d/'log.json',d/'one',d/'zones.json','Test');merge([d/'one'],d/'merged')
            with(d/'merged/counts_by_site_user_lane.csv').open()as f:rows=list(csv.DictReader(f))
            self.assertEqual({(r['user_type'],r['facility'],r['predicted_count'])for r in rows},{('pedestrian','sidewalk','1'),('car','road','1')})
            with(d/'merged/all_tracks.csv').open()as f:tracks=list(csv.DictReader(f))
            self.assertEqual(len(tracks),2);self.assertEqual({r['object_kind']for r in tracks},{'person','vehicle'})

    def test_new_site_pilot_and_zone_file_required(self):
        row=dict(site='Pine Hills BL E',study_date='2019-08-28',video='/raw/Standard_SCU8OG_2019-08-28_0000.013.mp4',archive_path='x',clock='2019-08-28 12:00:00',clock_status='inferred',fps=30,duration_seconds=3600,probe_status='readable_metadata_not_full_decode')
        self.assertEqual(select([row],'pilot','Pine Hills BL E'),[row])
        with self.assertRaises(ValueError):build_plan(ROOT,'test',[row],require_zones=True)
        self.assertEqual(build_plan(ROOT,'test',[row])['tasks'][0]['env']['ZONES_JSON'],'/nonexistent_zones.json')

    def test_generated_editor_embeds_camera_and_supports_import(self):
        h=page('Pine Hills BL E','2019-08-28','/raw/test.mp4',1,'data:image/jpeg;base64,',720,480)
        self.assertNotIn('METADATA',h);self.assertIn('extra_regions',h);self.assertIn('Import previous zones JSON',h)
        self.assertNotEqual(zone_key('A/B'),zone_key('A B'))

if __name__=='__main__':unittest.main()
