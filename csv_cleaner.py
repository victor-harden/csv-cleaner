#!/usr/bin/env python3
"""Clean CSV files with a predictable, documented set of rules."""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path


def normalize_header(name: str) -> str:
    name = name.strip().lower()
    name = re.sub(r"[^a-z0-9]+", "_", name)
    return name.strip("_") or "column"


def clean_value(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def clean_rows(rows, dedupe_by=None):
    """rows: list of lists including the header row."""
    if not rows:
        return [], {"rows_in": 0, "rows_out": 0, "duplicates": 0}
    header = [normalize_header(h) for h in rows[0]]
    body = [[clean_value(cell) for cell in row] for row in rows[1:]]
    body = [row for row in body if any(cell for cell in row)]

    seen = set()
    unique_rows = []
    duplicates = 0
    key_indexes = None
    if dedupe_by:
        key_indexes = [header.index(name) for name in dedupe_by if name in header]
        if not key_indexes:
            raise ValueError(f"dedupe columns not found: {dedupe_by}")
    for row in body:
        key = tuple(row[i] for i in key_indexes) if key_indexes else tuple(row)
        if key in seen:
            duplicates += 1
            continue
        seen.add(key)
        unique_rows.append(row)
    stats = {"rows_in": len(rows) - 1, "rows_out": len(unique_rows),
             "duplicates": duplicates}
    return [header] + unique_rows, stats


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Clean a CSV file")
    parser.add_argument("source", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--dedupe-by", nargs="+")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    try:
        with args.source.open(newline="", encoding="utf-8-sig") as handle:
            rows = list(csv.reader(handle))
    except OSError as exc:
        print(f"cannot read file: {exc}", file=sys.stderr)
        return 2

    try:
        cleaned, stats = clean_rows(rows, args.dedupe_by)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.out:
        with args.out.open("w", newline="", encoding="utf-8") as handle:
            csv.writer(handle).writerows(cleaned)
        stats["output"] = str(args.out)
    else:
        for row in cleaned:
            print(",".join(row))
    if args.json:
        print(json.dumps(stats, indent=2), file=sys.stderr if not args.out else sys.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
