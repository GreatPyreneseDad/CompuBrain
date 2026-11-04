"""Tests for .html text extraction."""
import tempfile
import unittest
from pathlib import Path

from ingest import chunk
from ingest.htmlpage import extract_text


class TestHtmlExtraction(unittest.TestCase):
    def _make_html(self, body: str, name: str = "page.html", encoding: str = "utf-8") -> Path:
        d = Path(tempfile.mkdtemp())
        p = d / name
        p.write_bytes(body.encode(encoding))
        self.addCleanup(lambda: (p.unlink(), d.rmdir()))
        return p

    def test_headings_and_paragraphs(self):
        p = self._make_html("<html><body><h1>Handbook</h1><p>First para.</p><h2>Refunds</h2><p>Second para.</p></body></html>")
        text = extract_text(p)
        self.assertEqual("Handbook\n\nFirst para.\n\nRefunds\n\nSecond para.", text)

    def test_entities_decoded(self):
        p = self._make_html("<p>Fish &amp; chips &lt;3 &#36;5 caf&eacute;</p>")
        self.assertEqual("Fish & chips <3 $5 café", extract_text(p))

    def test_script_and_style_dropped(self):
        p = self._make_html("<head><style>.x{color:red}</style><script>var a='<p>no</p>';</script></head>"
                            "<body><p>Visible</p><script>alert(1)</script></body>")
        text = extract_text(p)
        self.assertEqual("Visible", text)

    def test_whitespace_collapsed_and_inline_tags_joined(self):
        p = self._make_html("<p>The   <b>signed</b>\n  amendment</p>")
        self.assertEqual("The signed amendment", extract_text(p))

    def test_table_cells_and_breaks_separate(self):
        p = self._make_html("<table><tr><td>A</td><td>B</td></tr></table><p>one<br>two</p>")
        self.assertEqual("A\n\nB\n\none\n\ntwo", extract_text(p))

    def test_cp1252_fallback(self):
        p = self._make_html("<p>Caf\u00e9</p>", encoding="cp1252")
        self.assertEqual("Café", extract_text(p))

    def test_empty_document(self):
        self.assertEqual("", extract_text(self._make_html("<html></html>")))

    def test_through_chunk_load(self):
        p = self._make_html("<h1>Support handbook</h1><p>Escalate within 4 hours &amp; log every call.</p>", name="Handbook.HTML")
        self.assertIn(".html", chunk.READERS)
        doc = chunk.load(p, source="upload", default_scope="support")
        self.assertFalse(doc.pretagged)
        joined = "\n".join(c.content for c in doc.chunks)
        self.assertIn("Escalate within 4 hours & log every call.", joined)
        with self.assertRaises(ValueError):
            chunk.load(p, source=None, default_scope=None)


if __name__ == "__main__":
    unittest.main()
