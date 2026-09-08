from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from data_profile import profile
from final_audit import audit, freeze_from_manifest
from validate_results import CHECKS, validate


class ToolTests(unittest.TestCase):
    def test_data_profile_reports_core_fields(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "data.csv"
            source.write_text("id,value,group\n1,10,a\n2,20,b\n2,20,b\n", encoding="utf-8")
            result = profile(source)
            self.assertEqual(result["shape"], [3, 3])
            self.assertEqual(result["suspicious_duplicate_rows"], 1)
            self.assertEqual(result["columns"]["value"]["numeric"]["max"], 20.0)

    def test_validation_fails_closed_and_is_problem_aware(self) -> None:
        report = validate(["forecasting"], {})
        self.assertFalse(report["passed"])
        self.assertEqual(len(report["findings"]), len(CHECKS["forecasting"]))
        evidence = {name: {"status": "pass", "evidence": "recorded diagnostic"} for name in CHECKS["forecasting"]}
        evidence["constraint_feasibility"] = {"status": "fail", "evidence": "irrelevant"}
        report = validate(["forecasting"], evidence)
        self.assertTrue(report["passed"])
        self.assertIn("constraint_feasibility", report["unknown_checks_ignored"])

    def test_freeze_detects_changed_file(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            base = Path(directory)
            source = base / "metrics.json"
            source.write_text('{"score": 1}\n', encoding="utf-8")
            experiment = ROOT / "workspace" / "experiments" / "EXP-1"
            experiment.mkdir(parents=True, exist_ok=False)
            for name in ("config.json", "metrics.json", "results.json", "runtime.json"):
                (experiment / name).write_text("{}\n", encoding="utf-8")
            manifest = base / "manifest.json"
            manifest.write_text(json.dumps({
                "accepted_model": "A",
                "accepted_experiment_ids": ["EXP-1"],
                "final_metrics": {"score": 1},
                "final_tables": [],
                "final_figures": [],
                "files": [source.relative_to(ROOT).as_posix()],
            }), encoding="utf-8")
            frozen = base / "FROZEN_RESULTS.json"
            previous = Path.cwd()
            try:
                import os
                os.chdir(ROOT)
                freeze_from_manifest(manifest, frozen)
                self.assertTrue(audit(frozen)["passed"])
                source.write_text('{"score": 2}\n', encoding="utf-8")
                self.assertFalse(audit(frozen)["passed"])
            finally:
                os.chdir(previous)
                for name in ("config.json", "metrics.json", "results.json", "runtime.json"):
                    (experiment / name).unlink(missing_ok=True)
                experiment.rmdir()


if __name__ == "__main__":
    unittest.main()
