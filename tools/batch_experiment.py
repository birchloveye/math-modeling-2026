#!/usr/bin/env python3
"""展开 JSON 实验计划并运行每个配置。"""
from __future__ import annotations

import argparse
import itertools
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from common import load_json, require_keys, resolve_inside, write_json


def combinations(grid: dict[str, list[Any]]) -> list[dict[str, Any]]:
    keys = sorted(grid)
    return [dict(zip(keys, values, strict=True)) for values in itertools.product(*(grid[key] for key in keys))]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--continue-on-error", action="store_true", help="单次运行失败后继续执行其他组合")
    args = parser.parse_args()
    plan = load_json(args.plan)
    if not isinstance(plan, dict):
        raise ValueError("实验计划必须是对象")
    require_keys(plan, ["plan_id", "runner", "base_config", "parameter_grid", "seeds", "output_root"], "实验计划")
    if not plan["parameter_grid"] or not plan["seeds"]:
        raise ValueError("parameter_grid 和 seeds 不得为空")
    root = Path.cwd().resolve()
    runner = resolve_inside(root, plan["runner"])
    output_root = resolve_inside(root, plan["output_root"])
    timeout = plan.get("timeout_seconds")
    failures = 0
    run_number = 0
    for params in combinations(plan["parameter_grid"]):
        for seed in plan["seeds"]:
            run_number += 1
            experiment_id = f"{plan['plan_id']}-{run_number:04d}"
            directory = output_root / experiment_id
            directory.mkdir(parents=True, exist_ok=False)
            config = dict(plan["base_config"])
            config.update(params)
            config["seed"] = seed
            write_json(directory / "config.json", config)
            start = time.perf_counter()
            command = [sys.executable, str(runner), "--config", str(directory / "config.json"), "--output", str(directory)]
            try:
                result = subprocess.run(command, cwd=root, capture_output=True, text=True, encoding="utf-8", timeout=timeout, check=False)
                (directory / "logs").mkdir()
                (directory / "logs" / "stdout.txt").write_text(result.stdout, encoding="utf-8")
                (directory / "logs" / "stderr.txt").write_text(result.stderr, encoding="utf-8")
                write_json(directory / "runtime.json", {"command": command, "elapsed_seconds": time.perf_counter() - start, "returncode": result.returncode})
                required = [directory / "metrics.json", directory / "results.json"]
                if result.returncode or any(not path.is_file() for path in required):
                    failures += 1
                    if not args.continue_on_error:
                        raise RuntimeError(f"{experiment_id} 失败；请检查 {directory / 'logs'}")
            except subprocess.TimeoutExpired as exc:
                failures += 1
                write_json(directory / "runtime.json", {"command": command, "elapsed_seconds": time.perf_counter() - start, "timed_out": True})
                if not args.continue_on_error:
                    raise RuntimeError(f"{experiment_id} 超时") from exc
    print(f"共完成 {run_number} 次运行；失败次数={failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
