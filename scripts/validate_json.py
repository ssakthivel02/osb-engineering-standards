#!/usr/bin/env python3
"""Parse every JSON file and report failures with deterministic exit codes."""
from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    failures: list[str] = []
    for path in sorted(Path('.').rglob('*.json')):
        if any(part in {'.git', 'node_modules'} for part in path.parts):
            continue
        try:
            with path.open('r', encoding='utf-8') as handle:
                json.load(handle)
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            failures.append(f"{path}: {exc}")
    if failures:
        print('\n'.join(failures), file=sys.stderr)
        return 1
    print('JSON validation passed')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
