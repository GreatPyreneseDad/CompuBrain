import importlib
import sys
import types
import unittest
from unittest import mock


class OrderedListTest(unittest.TestCase):
    def setUp(self):
        fake = types.ModuleType("core.gate")
        fake.query = lambda role, sql, params=None: []
        with mock.patch.dict(sys.modules, {"core.gate": fake}):
            sys.modules.pop("helpcenter.build", None)
            self.build = importlib.import_module("helpcenter.build")
        self.addCleanup(sys.modules.pop, "helpcenter.build", None)

    def test_numbered_lines_become_ol(self):
        out = self.build.blocks("Steps:\n1. Open\n2. Save")
        self.assertEqual(out, "<p>Steps:</p>\n<ol>\n<li>Open</li>\n<li>Save</li>\n</ol>")

    def test_dash_and_numbered_runs_stay_separate(self):
        out = self.build.blocks("- a\n1. b\n2. c\n- d")
        self.assertEqual(out.count("<ul>"), 2)
        self.assertEqual(out.count("<ol>"), 1)

    def test_items_are_escaped(self):
        out = self.build.blocks("1. **Go** <b> & `x`")
        self.assertIn("<li><strong>Go</strong> &lt;b&gt; &amp; <code>x</code></li>", out)

    def test_number_without_space_is_text(self):
        self.assertEqual(self.build.blocks("2.0 released"), "<p>2.0 released</p>")


if __name__ == "__main__":
    unittest.main()
