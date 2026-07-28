#!/usr/bin/env python3
"""Validate controlled vocabulary shape and code uniqueness."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

CODE = re.compile(r'^[A-Z][A-Z0-9_]*$')


def main() -> int:
    failures: list[str] = []
    for path in sorted(Path('vocabularies').glob('*.json')):
        data = json.loads(path.read_text(encoding='utf-8'))
        values = data.get('values', [])
        codes = [item.get('code') for item in values]
        if len(codes) != len(set(codes)):
            failures.append(f'{path}: duplicate codes')
        for code in codes:
            if not isinstance(code, str) or not CODE.fullmatch(code):
                failures.append(f'{path}: invalid code {code!r}')
    if failures:
        print('\n'.join(failures), file=sys.stderr)
        return 1
    print('Vocabulary validation passed')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
