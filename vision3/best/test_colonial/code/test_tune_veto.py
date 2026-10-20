import copy
import unittest
from pathlib import Path
from tune_veto import load_clip,replay,choose

class VetoReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=load_clip(Path(__file__).resolve().parents[1],'b4_combo_static5','night')

    def setup_case(self):
        d=self.data
        a=copy.deepcopy(d['audit']['12']);s=copy.deepcopy(d['stats']['12']);t=copy.deepcopy(d['raw']['12']);p=copy.deepcopy(d['log']['params'])
        a.update(xclip_label='BICYCLIST',det_cyclist_pct='10',speed_heights_per_s='1',speed_span_s='3',net_px='100')
        return a,s,t,p

    def test_veto_boundary_is_strict(self):
        a,s,t,p=self.setup_case();a['det_cyclist_pct']='15'
        self.assertEqual(replay(a,s,t,p,29.97,480,15)[0],'BICYCLIST')
        self.assertEqual(replay(a,s,t,p,29.97,480,20)[0],'PEDESTRIAN')

    def test_motion_rule_runs_after_veto(self):
        a,s,t,p=self.setup_case();a.update(speed_heights_per_s='.5',direction='moving_left')
        self.assertEqual(replay(a,s,t,p,29.97,480,None)[0],'PEDESTRIAN')

    def test_veto_requires_twenty_detector_observations(self):
        a,s,t,p=self.setup_case();s['frames']='19'
        self.assertEqual(replay(a,s,t,p,29.97,480,15)[0],'BICYCLIST')

    def test_short_exception_depends_on_night_and_final_class(self):
        a,s,t,p=self.setup_case();s['frames']='36';a.update(det_cyclist_pct='95',weighted_bicyclist='.95')
        self.assertEqual(replay(a,s,t,p,29.97,480,15),('BICYCLIST',1))
        a['night_track']='0'
        self.assertEqual(replay(a,s,t,p,29.97,480,15)[1],0)
        a.update(night_track='1',det_cyclist_pct='10')
        self.assertEqual(replay(a,s,t,p,29.97,480,15),('PEDESTRIAN',0))

    def test_tie_keeps_current_threshold(self):
        rows=[dict(threshold=t,correct=9,total=11,unmatched_counted=0) for t in (None,5,15,30)]
        self.assertEqual(choose(rows,15),15)
        rows[-1]['correct']=10
        self.assertEqual(choose(rows,15),30)

    def test_empty_approved_subset_cannot_select_threshold(self):
        with self.assertRaises(ValueError):
            choose([dict(threshold=15,correct=0,total=0,unmatched_counted=0)],15)

if __name__=='__main__':
    unittest.main()
