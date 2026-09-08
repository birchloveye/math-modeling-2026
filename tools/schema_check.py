#!/usr/bin/env python3
"""使用标准库校验本仓库 JSON artifact 所需的 JSON Schema 关键字。"""
from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Any

from common import load_json


class SchemaValidationError(ValueError):
    """表示 artifact 不符合 Schema，包含可定位的 JSON 路径。"""


def _type_matches(value: Any, expected: str) -> bool:
    if expected == "null":
        return value is None
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
    if expected == "string":
        return isinstance(value, str)
    if expected == "array":
        return isinstance(value, list)
    if expected == "object":
        return isinstance(value, dict)
    raise SchemaValidationError(f"Schema 使用了不支持的 type：{expected}")


def _resolve_ref(root_schema: dict[str, Any], ref: str) -> dict[str, Any]:
    if not ref.startswith("#/"):
        raise SchemaValidationError(f"仅支持本地 JSON Pointer $ref：{ref}")
    current: Any = root_schema
    for raw_part in ref[2:].split("/"):
        part = raw_part.replace("~1", "/").replace("~0", "~")
        if not isinstance(current, dict) or part not in current:
            raise SchemaValidationError(f"无法解析 $ref：{ref}")
        current = current[part]
    if not isinstance(current, dict):
        raise SchemaValidationError(f"$ref 未指向 Schema 对象：{ref}")
    return current


def validate_instance(instance: Any, schema: dict[str, Any]) -> list[str]:
    """返回全部校验错误；空列表表示通过。"""
    errors: list[str] = []

    def check(value: Any, rule: dict[str, Any], path: str) -> None:
        if "$ref" in rule:
            check(value, _resolve_ref(schema, rule["$ref"]), path)
            return
        if "enum" in rule and value not in rule["enum"]:
            errors.append(f"{path}: 值不在允许枚举中")
            return
        expected = rule.get("type")
        if expected is not None:
            choices = expected if isinstance(expected, list) else [expected]
            if not any(_type_matches(value, item) for item in choices):
                errors.append(f"{path}: 类型应为 {' 或 '.join(choices)}")
                return
        if isinstance(value, dict):
            required = rule.get("required", [])
            for key in required:
                if key not in value:
                    errors.append(f"{path}: 缺少必需字段 {key}")
            properties = rule.get("properties", {})
            additional = rule.get("additionalProperties", True)
            for key, child in value.items():
                child_path = f"{path}.{key}"
                if key in properties:
                    check(child, properties[key], child_path)
                elif additional is False:
                    errors.append(f"{child_path}: 不允许额外字段")
                elif isinstance(additional, dict):
                    check(child, additional, child_path)
            if len(value) < rule.get("minProperties", 0):
                errors.append(f"{path}: 字段数量少于 {rule['minProperties']}")
        elif isinstance(value, list):
            if len(value) < rule.get("minItems", 0):
                errors.append(f"{path}: 元素数量少于 {rule['minItems']}")
            if rule.get("uniqueItems"):
                encoded = [json.dumps(item, ensure_ascii=False, sort_keys=True) for item in value]
                if len(encoded) != len(set(encoded)):
                    errors.append(f"{path}: 元素必须唯一")
            item_rule = rule.get("items")
            if isinstance(item_rule, dict):
                for index, child in enumerate(value):
                    check(child, item_rule, f"{path}[{index}]")
        elif isinstance(value, str):
            if len(value) < rule.get("minLength", 0):
                errors.append(f"{path}: 字符串长度少于 {rule['minLength']}")
            if "pattern" in rule and re.search(rule["pattern"], value) is None:
                errors.append(f"{path}: 不符合模式 {rule['pattern']}")
        elif isinstance(value, (int, float)) and not isinstance(value, bool):
            if "minimum" in rule and value < rule["minimum"]:
                errors.append(f"{path}: 数值小于最小值 {rule['minimum']}")
            if "exclusiveMinimum" in rule and value <= rule["exclusiveMinimum"]:
                errors.append(f"{path}: 数值必须大于 {rule['exclusiveMinimum']}")

    check(instance, schema, "$")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("schema", type=Path, help="JSON Schema 文件")
    parser.add_argument("artifact", type=Path, help="待校验的 JSON artifact")
    args = parser.parse_args()
    schema, artifact = load_json(args.schema), load_json(args.artifact)
    if not isinstance(schema, dict):
        raise ValueError("Schema 根节点必须是对象")
    errors = validate_instance(artifact, schema)
    if errors:
        print(f"FAIL：发现 {len(errors)} 个 Schema 错误")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS：artifact 符合 Schema")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

