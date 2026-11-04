import importlib
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

DOCS = [("d2", "Second <Doc>"), ("d1", "First Doc")]
CHUNKS = [
    ("d1", 0, "alpha"),
    ("d1", 1, '<script>alert("x")</script> & more'),
    ("d2", 0, "beta"),
]


class BuildTest(unittest.TestCase):
    def setUp(self):
        self.roles = []

        def query(role, sql, params=None):
            self.roles.append(role)
            if "visible_document" in sql:
                return sorted(DOCS, key=lambda d: (d[1], d[0]))
            if "from chunk" in sql:
                return list(reversed(CHUNKS))
            raise AssertionError(sql)

        fake = types.ModuleType("core.gate")
        fake.query = query
        with mock.patch.dict(sys.modules, {"core.gate": fake}):
            sys.modules.pop("helpcenter.build", None)
            self.build = importlib.import_module("helpcenter.build")
        self.build.gate = fake
        self.addCleanup(sys.modules.pop, "helpcenter.build", None)

    def run_build(self, token="tok-1"):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        out = Path(tmp.name)
        self.build.build(out, token)
        return out

    def test_asks_only_as_customer(self):
        self.run_build()
        self.assertTrue(self.roles)
        self.assertEqual(set(self.roles), {"BRAIN_CUSTOMER"})

    def test_pages_and_escaping(self):
        out = self.run_build()
        self.assertTrue((out / "index.html").is_file())
        pages = sorted(p.name for p in out.glob("doc-*.html"))
        self.assertEqual(len(pages), 2)
        first = (out / "doc-first-doc.html").read_text(encoding="utf-8")
        self.assertNotIn("<script>alert", first)
        self.assertIn("&lt;script&gt;", first)
        self.assertLess(first.index("alpha"), first.index("&lt;script&gt;"))
        index = (out / "index.html").read_text(encoding="utf-8")
        self.assertIn("Second &lt;Doc&gt;", index)

    def test_ask_script_uses_token_and_text_content(self):
        out = self.run_build("tok-xyz")
        js = (out / "ask.js").read_text(encoding="utf-8")
        self.assertIn("Bearer tok-xyz", js)
        self.assertIn("textContent", js)
        self.assertNotIn("innerHTML", js)

    def test_deterministic(self):
        a, b = self.run_build(), self.run_build()
        names = sorted(p.name for p in a.iterdir())
        self.assertEqual(names, sorted(p.name for p in b.iterdir()))
        for n in names:
            self.assertEqual((a / n).read_bytes(), (b / n).read_bytes())


if __name__ == "__main__":
    unittest.main()
