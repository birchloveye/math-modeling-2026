#!/usr/bin/env python3
"""依据实验与结果 Freeze 验证 Claim Ledger 的证据来源。"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from common import load_json, resolve_inside, write_json


def dotted(value: Any, key: str) -> Any:
    current = value
    for part in key.split("."):
        if not isinstance(current, dict) or part not in current:
            raise KeyError(key)
        current = current[part]
    return current


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, default=Path("workspace/claims/claim_ledger.json"))
    parser.add_argument("--freeze", type=Path, default=Path("workspace/experiments/FROZEN_RESULTS.json"))
    parser.add_argument("--experiments-root", type=Path, default=Path("workspace/experiments"))
    parser.add_argument("--output", type=Path, default=Path("workspace/claims/claim_check_report.json"))
    args = parser.parse_args()
    ledger, freeze = load_json(args.ledger), load_json(args.freeze)
    if not isinstance(ledger, list) or not isinstance(freeze, dict):
        raise ValueError("Ledger 必须是数组，Freeze 必须是对象")
    accepted = set(freeze.get("accepted_experiment_ids", []))
    findings: list[dict[str, str]] = []
    seen: set[str] = set()
    root = args.experiments_root.resolve()
    for claim in ledger:
        if not isinstance(claim, dict):
            findings.append({"claim_id": "?", "message": "Claim 必须是对象"})
            continue
        claim_id = str(claim.get("claim_id", "?"))
        if claim_id in seen:
            findings.append({"claim_id": claim_id, "message": "claim_id 重复"})
        seen.add(claim_id)
        status = claim.get("status")
        experiment = claim.get("source_experiment")
        if status == "verified" and experiment not in accepted:
            findings.append({"claim_id": claim_id, "message": "verified Claim 的来源实验未被 Freeze 接受"})
            continue
        if status in {"supported", "verified"}:
            try:
                metrics = load_json(resolve_inside(root, Path(str(experiment)) / "metrics.json"))
                dotted(metrics, str(claim.get("source_metric", "")))
            except (ValueError, KeyError) as exc:
                findings.append({"claim_id": claim_id, "message": str(exc)})
            code = Path(str(claim.get("code", "")))
            if not code.is_file():
                findings.append({"claim_id": claim_id, "message": f"源代码不存在：{code}"})
    report = {"checked": len(ledger), "findings": findings, "passed": not findings}
    write_json(args.output, report)
    print("PASS" if report["passed"] else f"FAIL ({len(findings)} findings)")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
