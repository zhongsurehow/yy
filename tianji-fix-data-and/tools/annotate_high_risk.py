#!/usr/bin/env python3
"""
Scan card JSON files for high-risk actions and optionally annotate them with metadata.review = "required".
Usage: python3 tools/annotate_high_risk.py [--apply]
"""
import json
import os
import sys
from typing import List

BASE = 'assets/data/cards'
RISKS = ['EXECUTE_LATER', 'COPY_EFFECT', 'MODIFY_RULE', 'CREATE_ENTITY', 'SWAP_DISCARD_PILES', 'SWAP_RESOURCE', 'SWAP_HAND_CARDS']

def find_files() -> List[str]:
    out = []
    for root, _, files in os.walk(BASE):
        for f in files:
            if f.endswith('.json'):
                out.append(os.path.join(root, f))
    return out

def file_has_risk(path: str) -> bool:
    try:
        with open(path, 'r', encoding='utf-8') as fh:
            txt = fh.read()
            for r in RISKS:
                if r in txt:
                    return True
    except Exception:
        return False
    return False

def annotate(path: str) -> None:
    with open(path, 'r', encoding='utf-8') as fh:
        data = json.load(fh)
    meta = data.get('metadata', {})
    meta.setdefault('review', 'required')
    data['metadata'] = meta
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)

def main():
    apply_changes = '--apply' in sys.argv
    files = find_files()
    hits = []
    for f in files:
        if file_has_risk(f):
            hits.append(f)
            if apply_changes:
                annotate(f)

    print(f'Found {len(hits)} high-risk file(s):')
    for h in hits:
        print(' -', h)
    if apply_changes:
        print('\nAnnotated all files with metadata.review = "required"')

if __name__ == '__main__':
    main()
