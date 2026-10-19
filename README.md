# csv-cleaner

A practical CSV cleaner for messy exports: normalizes header names, trims
whitespace in every cell, drops empty rows and columns, removes duplicates and
optionally infers numeric values. Writes to a new file and prints a summary of
what changed.

## Features

- Header normalization: lowercase, spaces to underscores, no punctuation.
- Trims cells, collapses internal whitespace.
- Drops fully empty rows and columns (opt-in for columns).
- Deduplicates by the full row or by chosen key columns.
- Summary showing rows in, rows out and duplicates removed.
- Tests with deliberately messy fixtures.

## Installation

```bash
git clone https://github.com/victor-harden/csv-cleaner.git
cd csv-cleaner
```

## Usage

```bash
python3 csv_cleaner.py input.csv --out clean.csv
python3 csv_cleaner.py input.csv --dedupe-by email --json
```

## Tests

```bash
python3 -m unittest discover -s tests -v
```

## License

MIT — see [LICENSE](LICENSE).
