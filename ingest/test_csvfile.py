"""Tests for .csv text extraction."""
import tempfile
import unittest
from pathlib import Path

from ingest import chunk
from ingest.csvfile import extract_text


class TestCsvExtraction(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def _write(self, name: str, data, mode="w") -> Path:
        p = self.dir / name
        if isinstance(data, bytes):
            p.write_bytes(data)
        else:
            p.write_text(data, encoding="utf-8", newline="")
        return p

    def test_quoted_comma_stays_whole(self):
        p = self._write("a.csv", 'account,region,owner\n"Kestrel, Ridge Co",West,Dana\nHalcyon Freight,East,Lee\n')
        self.assertEqual("account | region | owner\nKestrel, Ridge Co | West | Dana\nHalcyon Freight | East | Lee",
                         extract_text(p))

    def test_quoted_newline_and_escaped_quote(self):
        p = self._write("b.csv", 'note,who\n"line one\nline two, ""quoted""",Sam\n')
        self.assertEqual('note | who\nline one line two, "quoted" | Sam', extract_text(p))

    def test_empty_rows_and_trailing_cells_dropped(self):
        p = self._write("c.csv", "a,b,c\n\n,,\nx,,y\nz,,\n")
        self.assertEqual("a | b | c\nx |  | y\nz", extract_text(p))

    def test_semicolon_delimiter_and_bom(self):
        p = self._write("d.csv", b"\xef\xbb\xbfname;city\nAda;Z\xc3\xbcrich\n")
        self.assertEqual("name | city\nAda | Z\u00fcrich", extract_text(p))

    def test_empty_file(self):
        self.assertEqual("", extract_text(self._write("e.csv", "")))

    def test_loads_through_chunk(self):
        p = self._write("ACCOUNTS.CSV", 'account,region\n"Kestrel, Ridge Co",West\n')
        self.assertIn(".csv", chunk.READERS)
        doc = chunk.load(p, source="upload", default_scope="sales")
        self.assertFalse(doc.pretagged)
        self.assertIn("Kestrel, Ridge Co", "\n".join(c.content for c in doc.chunks))
        with self.assertRaises(ValueError):
            chunk.load(p, source=None, default_scope=None)


if __name__ == "__main__":
    unittest.main()
