"""CPU checks for COCO category mapping and safe submission defaults."""
import contextlib
import io
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import numpy as np
import rfdetr_audit as rf


class RFDETRAuditTests(unittest.TestCase):
    def test_sparse_coco_ids_keep_people_bikes_motorcycles(self):
        d = SimpleNamespace(class_id=np.array([1,2,3,4,90]),
                            xyxy=np.arange(20).reshape(5,4), confidence=np.array([.9,.8,.7,.6,.5]))
        result = rf.selected_proposals(d, {1:'person',2:'bicycle',3:'car',4:'motorcycle',90:'toothbrush'})
        self.assertEqual(result['text_labels'], ['person','bicycle','motorcycle'])
        np.testing.assert_array_equal(result['boxes'], d.xyxy[[0,1,3]])
        np.testing.assert_array_equal(result['scores'], d.confidence[[0,1,3]])

    def test_dry_run_does_not_submit_or_create_logs(self):
        with tempfile.TemporaryDirectory() as td, patch('sys.argv', ['rfdetr_audit.py','--root',td]), \
                patch.object(rf.subprocess, 'run') as run, contextlib.redirect_stdout(io.StringIO()):
            rf.main()
            run.assert_not_called()
            self.assertFalse((Path(td)/'logs').exists())

    def test_tiled_default_has_separate_output_tag(self):
        with tempfile.TemporaryDirectory() as td, patch('sys.argv', ['rfdetr_audit.py','--root',td,'--tiled']), \
                patch.object(rf.subprocess, 'run') as run, contextlib.redirect_stdout(io.StringIO()) as output:
            rf.main()
            run.assert_not_called()
            self.assertIn('rfdetr_tiled_oct19',output.getvalue())
            self.assertIn('tiled=True',output.getvalue())

    def test_invalid_tag_cannot_escape_logs(self):
        with patch('sys.argv', ['rfdetr_audit.py','--tag','../escape']), \
                contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            rf.main()


if __name__ == '__main__': unittest.main()
