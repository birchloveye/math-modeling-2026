from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from data_profile import profile
from final_audit import audit, freeze_from_manifest
from schema_check import validate_instance
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

    @unittest.skipUnless(importlib.util.find_spec("openpyxl"), "openpyxl is not installed")
    def test_data_profile_reads_all_xlsx_sheets_and_names_blank_headers(self) -> None:
        import openpyxl

        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "data.xlsx"
            workbook = openpyxl.Workbook()
            first = workbook.active
            first.title = "男胎"
            first.append(["孕妇代码", None, "数值"])
            first.append(["A001", None, 1.5])
            second = workbook.create_sheet("女胎")
            second.append(["孕妇代码", "标签"])
            second.append(["B001", "正常"])
            workbook.save(source)
            result = profile(source)
            self.assertEqual(result["format"], "xlsx")
            self.assertEqual(result["sheet_count"], 2)
            self.assertEqual(result["sheets"][0]["shape"], [1, 3])
            self.assertIn("column_B", result["sheets"][0]["columns"])

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

    def test_schema_check_accepts_valid_and_rejects_extra_fields(self) -> None:
        schema = {
            "type": "object",
            "additionalProperties": False,
            "required": ["id", "values"],
            "properties": {
                "id": {"type": "string", "pattern": "^Q[0-9]+$"},
                "values": {"type": "array", "minItems": 1, "uniqueItems": True, "items": {"type": "integer", "minimum": 0}}
            }
        }
        self.assertEqual(validate_instance({"id": "Q1", "values": [0, 2]}, schema), [])
        errors = validate_instance({"id": "bad", "values": [1, 1], "extra": True}, schema)
        self.assertEqual(len(errors), 3)


if __name__ == "__main__":
    unittest.main()
