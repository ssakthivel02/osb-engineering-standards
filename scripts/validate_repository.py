#!/usr/bin/env python3
"""Validate OSB engineering standards registries, schemas and examples."""
from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    import yaml
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError as exc:
    raise SystemExit(f"Missing validation dependency: {exc}")

ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []


def load_yaml(path: Path):
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def validate_registry() -> list[dict]:
    registry = load_yaml(ROOT / "SCHEMA_REGISTRY.yaml")
    seen: set[str] = set()
    entries = registry.get("schemas", [])
    for item in entries:
        schema_id = item.get("id")
        if not schema_id or schema_id in seen:
            ERRORS.append(f"Duplicate or missing schema id: {schema_id}")
        seen.add(schema_id)
        target = ROOT / item.get("path", "")
        if not target.is_file():
            ERRORS.append(f"Registered schema missing: {target.relative_to(ROOT)}")
        valid_example = ROOT / item.get("examples", {}).get("valid", "")
        if not valid_example.is_file():
            ERRORS.append(f"Registered valid example missing for {schema_id}: {valid_example.relative_to(ROOT)}")
    return entries


def validate_json_files() -> None:
    for path in ROOT.rglob("*.json"):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            ERRORS.append(f"Invalid JSON {path.relative_to(ROOT)}: {exc}")


def validate_schema_metadata(schema_path: Path, schema: dict) -> None:
    if not str(schema.get("$id", "")).startswith("https://"):
        ERRORS.append(f"Schema $id must use HTTPS: {schema_path.relative_to(ROOT)}")
    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        ERRORS.append(f"Schema draft mismatch: {schema_path.relative_to(ROOT)}")
    if "additionalProperties" not in schema:
        ERRORS.append(f"Schema must explicitly declare additionalProperties: {schema_path.relative_to(ROOT)}")
    for error in Draft202012Validator.check_schema(schema) or []:
        ERRORS.append(f"Invalid schema {schema_path.relative_to(ROOT)}: {error}")


def validate_examples(entries: list[dict]) -> None:
    for item in entries:
        schema_path = ROOT / item["path"]
        example_path = ROOT / item["examples"]["valid"]
        if not schema_path.is_file() or not example_path.is_file():
            continue
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        example = json.loads(example_path.read_text(encoding="utf-8"))
        validate_schema_metadata(schema_path, schema)
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        for error in sorted(validator.iter_errors(example), key=lambda value: list(value.path)):
            ERRORS.append(
                f"Example {example_path.relative_to(ROOT)} failed at {list(error.path)}: {error.message}"
            )


def main() -> int:
    entries = validate_registry()
    validate_json_files()
    validate_examples(entries)
    if ERRORS:
        print("OSB validation failed:")
        for error in ERRORS:
            print(f"- {error}")
        return 1
    print(f"OSB engineering standards validation passed ({len(entries)} schemas)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
