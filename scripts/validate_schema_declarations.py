#!/usr/bin/env python3
"""Enforce JSON Schema 2020-12 declarations and absolute identifiers."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.parse import urlparse

DRAFT = 'https://json-schema.org/draft/2020-12/schema'


def main() -> int:
    failures: list[str] = []
    for path in sorted(Path('schemas').glob('*.schema.json')):
        data = json.loads(path.read_text(encoding='utf-8'))
        if data.get('$schema') != DRAFT:
            failures.append(f'{path}: $schema must be {DRAFT}')
        schema_id = data.get('$id', '')
        parsed = urlparse(schema_id)
        if parsed.scheme != 'https' or not parsed.netloc:
            failures.append(f'{path}: $id must be an absolute HTTPS URI')
    if failures:
        print('\n'.join(failures), file=sys.stderr)
        return 1
    print('Schema declaration validation passed')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
