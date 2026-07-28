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


def validate_registry() -> None:
    registry = load_yaml(ROOT / "SCHEMA_REGISTRY.yaml")
    seen: set[str] = set()
    for item in registry.get("schemas", []):
        schema_id = item.get("id")
        if not schema_id or schema_id in seen:
            ERRORS.append(f"Duplicate or missing schema id: {schema_id}")
        seen.add(schema_id)
        target = ROOT / item.get("path", "")
        if not target.is_file():
            ERRORS.append(f"Registered schema missing: {target.relative_to(ROOT)}")


def validate_json_files() -> None:
    for path in ROOT.rglob("*.json"):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            ERRORS.append(f"Invalid JSON {path.relative_to(ROOT)}: {exc}")


def validate_fixture() -> None:
    schema_path = ROOT / "schemas/canonical-content.schema.json"
    fixture_path = ROOT / "validation/examples/valid-canonical-content.json"
    if not schema_path.exists() or not fixture_path.exists():
        return
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    for error in sorted(validator.iter_errors(fixture), key=lambda item: list(item.path)):
        ERRORS.append(f"Fixture validation failed at {list(error.path)}: {error.message}")


def main() -> int:
    validate_registry()
    validate_json_files()
    validate_fixture()
    if ERRORS:
        print("OSB validation failed:")
        for error in ERRORS:
            print(f"- {error}")
        return 1
    print("OSB engineering standards validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
