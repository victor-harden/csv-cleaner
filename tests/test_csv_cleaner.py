import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))
import csv_cleaner


class HeaderTests(unittest.TestCase):
    def test_normalize_header(self):
        self.assertEqual(csv_cleaner.normalize_header("  First Name "), "first_name")
        self.assertEqual(csv_cleaner.normalize_header("E-Mail!"), "e_mail")

    def test_empty_header_fallback(self):
        self.assertEqual(csv_cleaner.normalize_header("***"), "column")


class CleanRowsTests(unittest.TestCase):
    def test_trims_and_normalizes(self):
        cleaned, stats = csv_cleaner.clean_rows([["Name", " Age "], ["  Ada  ", " 36 "]])
        self.assertEqual(cleaned[0], ["name", "age"])
        self.assertEqual(cleaned[1], ["Ada", "36"])
        self.assertEqual(stats["rows_in"], 1)

    def test_drops_empty_rows(self):
        cleaned, stats = csv_cleaner.clean_rows([["a"], ["x"], ["  "], ["y"]])
        self.assertEqual(len(cleaned), 3)
        self.assertEqual(stats["rows_in"], 3)

    def test_removes_duplicates(self):
        cleaned, stats = csv_cleaner.clean_rows([["a", "b"], ["1", "2"], ["1", "2"]])
        self.assertEqual(stats["duplicates"], 1)
        self.assertEqual(len(cleaned), 2)

    def test_dedupe_by_single_column(self):
        cleaned, stats = csv_cleaner.clean_rows(
            [["email", "name"], ["a@x.com", "A"], ["a@x.com", "A2"], ["b@x.com", "B"]],
            dedupe_by=["email"],
        )
        self.assertEqual(stats["duplicates"], 1)
        self.assertEqual(len(cleaned), 3)

    def test_unknown_dedupe_column(self):
        with self.assertRaises(ValueError):
            csv_cleaner.clean_rows([["a"], ["1"]], dedupe_by=["nope"])

    def test_collapses_internal_whitespace(self):
        cleaned, _ = csv_cleaner.clean_rows([["a"], ["hello    world"]])
        self.assertEqual(cleaned[1][0], "hello world")


class CliTests(unittest.TestCase):
    def test_writes_clean_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "in.csv"
            out = Path(tmp) / "out.csv"
            source.write_text("Name , Age\n Ada , 36 \n Ada , 36 \n")
            code = csv_cleaner.main([str(source), "--out", str(out), "--json"])
            self.assertEqual(code, 0)
            rows = list(csv.reader(out.open()))
            self.assertEqual(rows[0], ["name", "age"])
            self.assertEqual(len(rows), 2)

    def test_missing_file(self):
        import contextlib
        import io
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(csv_cleaner.main(["/nope/in.csv"]), 2)


if __name__ == "__main__":
    unittest.main()
