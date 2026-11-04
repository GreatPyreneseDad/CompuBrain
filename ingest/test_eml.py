"""Tests for .eml text extraction."""
import email.message
import tempfile
import unittest
from pathlib import Path

from ingest import chunk
from ingest.eml import extract_text


def _message(subject="Signed amendment for Halcyon") -> email.message.EmailMessage:
    m = email.message.EmailMessage()
    m["Subject"] = subject
    m["From"] = "Lee Park <lee@halcyon.example>"
    m["To"] = "brain@company.example"
    return m


class TestEmlExtraction(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def _write(self, name: str, m) -> Path:
        p = self.dir / name
        p.write_bytes(bytes(m))
        return p

    def test_plain_body_preferred_and_attachment_ignored(self):
        m = _message()
        m.set_content("The signed amendment is attached. Countersign by Friday.")
        m.add_alternative("<p>HTML twin of the body.</p>", subtype="html")
        m.add_attachment(b"%PDF-1.4 binary-ish" * 40, maintype="application", subtype="pdf", filename="a.pdf")
        text = extract_text(self._write("a.eml", m))
        self.assertTrue(text.startswith("Signed amendment for Halcyon\nFrom: Lee Park <lee@halcyon.example>\nTo: brain@company.example"))
        self.assertIn("Countersign by Friday.", text)
        for debris in ("Content-Type", "boundary", "base64", "%PDF", "HTML twin"):
            self.assertNotIn(debris, text)

    def test_html_only_converted(self):
        m = _message()
        m.set_content("<html><head><title>T</title><style>p{color:red}</style></head><body>"
                      "<p>The <b>signed amendment</b> is attached &amp; ready.</p>"
                      "<script>var x='secret';</script><p>Second<br>line</p></body></html>", subtype="html")
        text = extract_text(self._write("b.eml", m))
        self.assertIn("The signed amendment is attached & ready.", text)
        self.assertIn("Second\nline", text)
        for debris in ("<b>", "<p>", "color:red", "secret", "&amp;"):
            self.assertNotIn(debris, text)

    def test_encoded_headers_and_body(self):
        m = _message("Caf\u00e9 renewal")
        m.set_content("Pr\u00fcfung bis Freitag.", charset="utf-8", cte="base64")
        text = extract_text(self._write("c.eml", m))
        self.assertTrue(text.startswith("Caf\u00e9 renewal\n"))
        self.assertIn("Pr\u00fcfung bis Freitag.", text)

    def test_no_body_and_no_subject(self):
        m = email.message.EmailMessage()
        m["From"] = "a@b.example"
        m.set_content("")
        text = extract_text(self._write("d.eml", m))
        self.assertEqual("(no subject)\nFrom: a@b.example", text)

    def test_loads_through_chunk(self):
        m = _message()
        m.set_content("Countersign by Friday.")
        p = self._write("MAIL.EML", m)
        self.assertIn(".eml", chunk.READERS)
        doc = chunk.load(p, source="mail", default_scope="sales")
        self.assertFalse(doc.pretagged)
        joined = "\n".join(c.content for c in doc.chunks)
        self.assertIn("Signed amendment for Halcyon", joined)
        self.assertIn("Countersign by Friday.", joined)
        with self.assertRaises(ValueError):
            chunk.load(p, source=None, default_scope=None)


if __name__ == "__main__":
    unittest.main()
