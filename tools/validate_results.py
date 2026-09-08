#!/usr/bin/env python3
"""对已记录证据执行失败关闭、题型感知的验证。"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from common import load_json, write_json


CHECKS = {
    "forecasting": ["data_leakage", "train_test_split", "baseline", "residual", "cross_validation", "uncertainty", "extrapolation_risk"],
    "optimization": ["constraint_feasibility", "constraint_residual", "convergence", "baseline", "optimality_evidence", "sensitivity", "boundary_behavior"],
    "statistical": ["assumptions", "sample_adequacy", "multicollinearity", "residual_diagnostics", "confidence_interval", "robustness"],
    "graph": ["connectivity", "topology_assumptions", "baseline", "complexity", "graph_construction_sensitivity"],
    "simulation": ["initialization", "stochastic_seed", "repeated_runs", "convergence", "variance", "parameter_sensitivity"],
    "ode_pde": ["units", "initial_boundary_conditions", "numerical_convergence", "parameter_sensitivity", "physical_plausibility"],
}
STATUSES = {"pass", "fail", "not_applicable"}


def validate(problem_types: list[str], evidence: dict[str, Any]) -> dict[str, Any]:
    applicable = sorted({check for kind in problem_types for check in CHECKS.get(kind, [])})
    findings: list[dict[str, str]] = []
    for check in applicable:
        item = evidence.get(check)
        if not isinstance(item, dict):
            findings.append({"check": check, "severity": "blocking", "message": "缺少检查证据"})
            continue
        status, detail = item.get("status"), item.get("evidence")
        if status not in STATUSES:
            findings.append({"check": check, "severity": "blocking", "message": "status 必须是 pass、fail 或 not_applicable"})
        elif not isinstance(detail, str) or not detail.strip():
            findings.append({"check": check, "severity": "blocking", "message": "必须提供非空证据或理由"})
        elif status == "fail":
            findings.append({"check": check, "severity": "blocking", "message": detail})
    unknown = sorted(set(evidence) - set(applicable))
    return {"problem_types": problem_types, "applicable_checks": applicable, "unknown_checks_ignored": unknown, "findings": findings, "passed": not findings}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--problem", type=Path, default=Path("workspace/problem/problem_contract.json"))
    parser.add_argument("--evidence", type=Path, required=True, help="以适用检查名为键的 JSON 对象")
    parser.add_argument("--output", type=Path, default=Path("workspace/experiments/validation_report.json"))
    args = parser.parse_args()
    problem, evidence = load_json(args.problem), load_json(args.evidence)
    if not isinstance(problem, dict) or not isinstance(problem.get("problem_type"), list):
        raise ValueError("问题契约必须包含 problem_type 数组")
    if not isinstance(evidence, dict):
        raise ValueError("evidence 必须是对象")
    report = validate(problem["problem_type"], evidence)
    write_json(args.output, report)
    print("PASS" if report["passed"] else f"FAIL ({len(report['findings'])} findings)")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
