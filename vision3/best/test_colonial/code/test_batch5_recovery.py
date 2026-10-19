"""Regression checks for batch-5 launch failures; no GPU or Slurm needed."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("batch5", HERE / "run_batch5.py")
batch5 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(batch5)


class RecoveryTests(unittest.TestCase):
    def test_review_candidates_keep_fusion_but_relax_filters(self):
        from types import SimpleNamespace
        args = SimpleNamespace(from_batch=HERE / 'run_batch4.sh', netpx='5')
        jobs = batch5.jobs_for('review', args)
        self.assertEqual(len(jobs), 4)
        for run, clip, env in jobs:
            self.assertEqual(run, 'b6_review_candidates')
            self.assertIn('SAHI=1', env)
            self.assertIn('BIC_MIN_SEC=0.4', env)
            self.assertIn('STATIC_FILTER=0', env)
            self.assertIn('TRACK_THR=0.15', env)

    def args(self, *extra):
        return [str(HERE / "run_batch5.py"), "bright", "--from-batch", str(HERE / "run_batch4.sh"),
                "--slurm", str(HERE / "run_xclip_colonial_v19.slurm"),
                "--script", str(HERE / "xclip_overlay_v19_colonial.py"), *extra]

    def test_missing_zerodce_fails_before_submission(self):
        r = subprocess.run([sys.executable, *self.args("--modes", "zerodce", "--zerodce-weights", "/missing/Epoch99.pth")], capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("requires an existing", r.stderr)

    def test_retry_selects_only_two_zerodce_jobs(self):
        with tempfile.NamedTemporaryFile(suffix=".pth") as weights:
            r = subprocess.run([sys.executable, *self.args("--modes", "zerodce", "--zerodce-weights", weights.name)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("2 jobs", r.stdout)
        self.assertIn("ZERODCE_WEIGHTS=", r.stdout)
        self.assertNotIn("RUN=b5_bright_gamma", r.stdout)

    def test_failed_submit_stops_and_preserves_lock(self):
        import os
        with tempfile.TemporaryDirectory() as tmp:
            old = os.getcwd()
            try:
                os.chdir(tmp)
                with patch.object(sys, "argv", self.args("--modes", "gamma", "--go")), \
                     patch.object(batch5.subprocess, "run", return_value=subprocess.CompletedProcess([], 1, "", "queue unavailable")) as submit:
                    with self.assertRaises(SystemExit): batch5.main()
                    self.assertEqual(submit.call_count, 1)
                self.assertIn("queue unavailable", Path("logs/.batch5_bright.lock").read_text())
            finally:
                os.chdir(old)

    def test_full_frame_preserves_wider_source_view(self):
        import undistort_fisheye as fish
        circular, _ = fish.build_maps(960, 540, 101, 101, 180, 110)
        rectangular, _ = fish.build_maps(960, 540, 101, 101, 180, 110, coverage="full-frame")
        self.assertGreater(rectangular[50, 100], circular[50, 100])
        self.assertAlmostEqual(float(rectangular[50, 50]), 480)


if __name__ == "__main__":
    unittest.main()
