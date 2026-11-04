"""Tests for .xlsx text extraction."""
import tempfile
import unittest
import zipfile
from pathlib import Path

from ingest import chunk
from ingest.xlsx import extract_text

_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


def _make_xlsx(path: Path, sheets: dict, shared=None, with_workbook=True) -> Path:
    """sheets: {name: <sheetData> inner XML}. Sheet i is written to xl/worksheets/sheet<i>.xml."""
    names = list(sheets)
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("[Content_Types].xml",
                   '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>')
        if with_workbook:
            entries = "".join(f'<sheet name="{n}" sheetId="{i}" r:id="rId{i}"/>' for i, n in enumerate(names, 1))
            z.writestr("xl/workbook.xml", f'<?xml version="1.0"?><workbook xmlns="{_MAIN}" xmlns:r="{_REL}"><sheets>{entries}</sheets></workbook>')
            rels = "".join(f'<Relationship Id="rId{i}" Type="{_REL}/worksheet" Target="worksheets/sheet{i}.xml"/>'
                           for i in range(1, len(names) + 1))
            z.writestr("xl/_rels/workbook.xml.rels",
                       f'<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">{rels}</Relationships>')
        if shared is not None:
            z.writestr("xl/sharedStrings.xml", f'<?xml version="1.0"?><sst xmlns="{_MAIN}">{shared}</sst>')
        for i, n in enumerate(names, 1):
            z.writestr(f"xl/worksheets/sheet{i}.xml",
                       f'<?xml version="1.0"?><worksheet xmlns="{_MAIN}"><sheetData>{sheets[n]}</sheetData></worksheet>')
    return path


class TestXlsxExtraction(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_shared_strings_numbers_and_sheet_names(self):
        shared = "<si><t>Account</t></si><si><t>Value</t></si><si><r><t>Tallgrass </t></r><r><t>Logistics</t></r></si>"
        p = _make_xlsx(self.dir / "a.xlsx", {
            "Pipeline": '<row r="1"><c r="A1" t="s"><v>0</v></c><c r="B1" t="s"><v>1</v></c></row>'
                        '<row r="2"><c r="A2" t="s"><v>2</v></c><c r="B2"><v>17500.5</v></c></row>',
            "Renewals": '<row r="1"><c r="A1" t="inlineStr"><is><t>Ridgeback renews in March</t></is></c></row>',
        }, shared=shared)
        text = extract_text(p)
        self.assertIn("Pipeline\nAccount | Value\nTallgrass Logistics | 17500.5", text)
        self.assertIn("Renewals\nRidgeback renews in March", text)
        self.assertLess(text.index("Pipeline"), text.index("Renewals"))

    def test_gaps_booleans_and_empty_rows(self):
        p = _make_xlsx(self.dir / "b.xlsx", {
            "Data": '<row r="1"><c r="A1" t="b"><v>1</v></c><c r="C1" t="str"><v>done</v></c></row>'
                    '<row r="2"><c r="A2"/></row>'
                    '<row r="3"><c r="B3"><v>7</v></c></row>',
        })
        self.assertEqual("Data\nTRUE |  | done\n | 7", extract_text(p))

    def test_empty_sheet_is_skipped(self):
        p = _make_xlsx(self.dir / "c.xlsx", {"Empty": "", "Full": '<row r="1"><c r="A1"><v>1</v></c></row>'})
        text = extract_text(p)
        self.assertNotIn("Empty", text)
        self.assertIn("Full", text)

    def test_missing_workbook_raises(self):
        p = _make_xlsx(self.dir / "d.xlsx", {"S": ""}, with_workbook=False)
        with self.assertRaises(KeyError):
            extract_text(p)


class TestChunkXlsx(unittest.TestCase):
    def test_upper_case_extension_loads_with_sheet_sections(self):
        with tempfile.TemporaryDirectory() as d:
            p = _make_xlsx(Path(d) / "REPORT.XLSX", {
                "Pipeline": '<row r="1"><c r="A1" t="inlineStr"><is><t>Halcyon Freight</t></is></c></row>',
                "Renewals": '<row r="1"><c r="A1" t="inlineStr"><is><t>Ridgeback Cold Chain</t></is></c></row>',
            })
            self.assertIn(".xlsx", chunk.READERS)
            doc = chunk.load(p, source="upload", default_scope="sales")
            self.assertFalse(doc.pretagged)
            heads = [c.content.splitlines()[0] for c in doc.chunks]
            self.assertEqual(2, len(heads))
            # chunk._headings_from_plain gives the first heading level 1 and the rest level 2, so the
            # second sheet's trail is "Pipeline > Renewals"
            self.assertEqual("[Pipeline]", heads[0])
            self.assertTrue(heads[1].endswith("Renewals]"), heads[1])
            self.assertIn("Halcyon Freight", doc.chunks[0].content)
            with self.assertRaises(ValueError):
                chunk.load(p, source=None, default_scope=None)


if __name__ == "__main__":
    unittest.main()
