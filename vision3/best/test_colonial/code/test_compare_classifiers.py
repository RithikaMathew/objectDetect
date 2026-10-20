import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from compare_classifiers import compare


class ClassifierComparisonTests(unittest.TestCase):
    def test_paired_sample_uses_raw_audit_and_keeps_rejected_people(self):
        root=Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory()as td,contextlib.redirect_stdout(io.StringIO()):
            out=Path(td)/'comparison';rows=compare(root,'b4_combo_static5',out)
            summary=json.loads((out/'summary.json').read_text())
            self.assertEqual((summary['included'],summary['detector_correct'],summary['xclip_correct']),(21,16,14))
            n5=next(r for r in rows if r['truth_id']=='n5')
            self.assertEqual(n5['track_counted'],0);self.assertEqual(n5['included'],1)
            h1=next(r for r in rows if r['truth_id']=='h1')
            self.assertEqual(h1['xclip_label'],'cyclist')  # Raw X-CLIP, not the post-rule tracks.csv field.
            self.assertEqual(h1['xclip_correct'],0);self.assertEqual(h1['detector_correct'],1)
            self.assertEqual(sum(r['truth_raw_class']=='motorcycle'for r in rows),1)

    def test_empty_identity_approvals_do_not_become_accuracy(self):
        root=Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory()as td,contextlib.redirect_stdout(io.StringIO()):
            d=Path(td);identity=d/'identity.csv'
            identity.write_text('run,clip,truth_id,track_id,decision,full_track_reviewed,reviewer,evidence\n')
            rows=compare(root,'b4_combo_static5',d/'comparison',identity)
            self.assertEqual(sum(r['included']for r in rows),0)
            self.assertIn('not evaluated',(d/'comparison/RESULTS.md').read_text())
            self.assertEqual(len(rows),21)


if __name__=='__main__':unittest.main()
