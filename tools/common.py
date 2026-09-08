"""仓库命令行工具共用的轻量辅助函数。"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


def load_json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError as exc:
        raise ValueError(f"必需文件不存在：{path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"文件中的 JSON 无效（{path}）：{exc}") from exc


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")


def require_keys(value: dict[str, Any], keys: Iterable[str], context: str) -> None:
    missing = sorted(set(keys) - value.keys())
    if missing:
        raise ValueError(f"{context} 缺少必需字段：{', '.join(missing)}")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_inside(root: Path, candidate: str | Path) -> Path:
    root = root.resolve()
    path = Path(candidate)
    resolved = (root / path).resolve() if not path.is_absolute() else path.resolve()
    if resolved != root and root not in resolved.parents:
        raise ValueError(f"路径超出允许的根目录 {root}：{candidate}")
    return resolved
