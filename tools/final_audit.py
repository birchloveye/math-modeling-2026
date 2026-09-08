#!/usr/bin/env python3
"""创建或验证冻结结果的可复现性清单。"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from common import load_json, resolve_inside, sha256_file, write_json


def freeze_from_manifest(manifest_path: Path, output: Path) -> dict[str, Any]:
    manifest = load_json(manifest_path)
    if not isinstance(manifest, dict):
        raise ValueError("Freeze Manifest 必须是对象")
    required = {"accepted_model", "accepted_experiment_ids", "final_metrics", "final_tables", "final_figures", "files"}
    missing = sorted(required - manifest.keys())
    if missing:
        raise ValueError(f"Freeze Manifest 缺少字段：{', '.join(missing)}")
    if not manifest["accepted_experiment_ids"]:
        raise ValueError("至少需要一个已接受实验")
    root = Path.cwd().resolve()
    source_items = list(manifest["files"])
    for experiment_id in manifest["accepted_experiment_ids"]:
        source_items.extend(
            f"workspace/experiments/{experiment_id}/{name}"
            for name in ("config.json", "metrics.json", "results.json", "runtime.json")
        )
    for collection in (manifest["final_tables"], manifest["final_figures"]):
        if not isinstance(collection, list):
            raise ValueError("final_tables 和 final_figures 必须是文件路径数组")
        source_items.extend(collection)
    hashes: dict[str, str] = {}
    for item in sorted(set(source_items)):
        path = resolve_inside(root, item)
        if not path.is_file():
            raise ValueError(f"Freeze 来源不是文件：{item}")
        hashes[path.relative_to(root).as_posix()] = sha256_file(path)
    frozen = {
        "accepted_model": manifest["accepted_model"],
        "accepted_experiment_ids": manifest["accepted_experiment_ids"],
        "final_metrics": manifest["final_metrics"],
        "final_tables": manifest["final_tables"],
        "final_figures": manifest["final_figures"],
        "freeze_timestamp": datetime.now(timezone.utc).isoformat(),
        "sha256": hashes,
    }
    write_json(output, frozen)
    return frozen


def audit(freeze_path: Path) -> dict[str, Any]:
    freeze = load_json(freeze_path)
    if not isinstance(freeze, dict):
        raise ValueError("Freeze 必须是对象")
    expected = freeze.get("sha256")
    if not isinstance(expected, dict) or not expected:
        raise ValueError("Freeze 中没有 SHA256 清单")
    root = Path.cwd().resolve()
    findings: list[dict[str, str]] = []
    for item, digest in sorted(expected.items()):
        path = resolve_inside(root, item)
        if not path.is_file():
            findings.append({"file": item, "message": "文件缺失"})
        elif sha256_file(path) != digest:
            findings.append({"file": item, "message": "哈希不匹配；Freeze 已失效"})
    return {"freeze": str(freeze_path), "checked_files": len(expected), "findings": findings, "passed": not findings}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true", help="根据 --manifest 创建 Freeze")
    parser.add_argument("--manifest", type=Path, help="与 --freeze 配合使用的已接受结果清单")
    parser.add_argument("--frozen-results", type=Path, default=Path("workspace/experiments/FROZEN_RESULTS.json"))
    parser.add_argument("--report", type=Path, default=Path("workspace/experiments/final_audit_report.json"))
    args = parser.parse_args()
    if args.freeze:
        if args.manifest is None:
            parser.error("--freeze 必须同时提供 --manifest")
        freeze_from_manifest(args.manifest, args.frozen_results)
        print(f"已创建 {args.frozen_results}")
        return 0
    report = audit(args.frozen_results)
    write_json(args.report, report)
    print("PASS" if report["passed"] else f"FAIL ({len(report['findings'])} findings)")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
