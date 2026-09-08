#!/usr/bin/env python3
"""依据 Ledger 检查论文中的 Claim 标签。"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

from common import load_json, write_json


CLAIM_TAG = re.compile(r"\[claim:(Q[1-9][0-9]*-C[0-9]{2,})\]")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paper", type=Path, help="包含 [claim:Q1-C01] 标签的 UTF-8 Markdown 论文")
    parser.add_argument("--ledger", type=Path, default=Path("workspace/claims/claim_ledger.json"))
    parser.add_argument("--output", type=Path, default=Path("workspace/paper/consistency_report.json"))
    args = parser.parse_args()
    text = args.paper.read_text(encoding="utf-8")
    ledger = load_json(args.ledger)
    by_id = {item["claim_id"]: item for item in ledger if isinstance(item, dict) and "claim_id" in item}
    findings: list[dict[str, str]] = []
    used = set(CLAIM_TAG.findall(text))
    for claim_id in sorted(used):
        item = by_id.get(claim_id)
        if item is None:
            findings.append({"claim_id": claim_id, "message": "论文标签不在 Ledger 中"})
        elif item.get("status") in {"draft", "rejected"}:
            findings.append({"claim_id": claim_id, "message": f"论文使用了不合格的 {item.get('status')} Claim"})
    eligible_unused = sorted(key for key, item in by_id.items() if item.get("status") == "verified" and key not in used)
    report = {"used_claims": sorted(used), "verified_claims_not_cited": eligible_unused, "findings": findings, "passed": not findings}
    write_json(args.output, report)
    print("PASS" if report["passed"] else f"FAIL ({len(findings)} findings)")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
