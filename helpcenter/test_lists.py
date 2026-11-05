import importlib
import sys
import types
import unittest
from unittest import mock


class ListTest(unittest.TestCase):
    def setUp(self):
        fake = types.ModuleType("core.gate")
        fake.query = lambda role, sql, params=None: []
        with mock.patch.dict(sys.modules, {"core.gate": fake}):
            sys.modules.pop("helpcenter.build", None)
            self.build = importlib.import_module("helpcenter.build")
        self.addCleanup(sys.modules.pop, "helpcenter.build", None)

    def test_dash_lines_become_list(self):
        out = self.build.blocks("Roles:\n- Admin\n- Member")
        self.assertEqual(
            out, "<p>Roles:</p>\n<ul>\n<li>Admin</li>\n<li>Member</li>\n</ul>"
        )

    def test_no_dash_lines_is_one_paragraph(self):
        self.assertEqual(self.build.blocks("just text\nmore text"), "<p>just text\nmore text</p>")

    def test_text_after_list_and_two_lists(self):
        out = self.build.blocks("- a\n- b\nthen\n- c")
        self.assertEqual(out.count("<ul>"), 2)
        self.assertIn("<p>then</p>", out)
        self.assertNotIn("- ", out)

    def test_items_are_escaped_and_inline_rendered(self):
        out = self.build.blocks("- **Admin** <b> & `sso`")
        self.assertIn("<li><strong>Admin</strong> &lt;b&gt; &amp; <code>sso</code></li>", out)

    def test_hyphen_inside_text_is_not_a_list(self):
        self.assertEqual(self.build.blocks("well-known - ok"), "<p>well-known - ok</p>")

    def test_sections_use_lists(self):
        out = self.build.sections(["[KB: Title > Roles]\n- Admin\n- Member"])
        self.assertIn("<h2>Roles</h2>", out)
        self.assertIn("<li>Member</li>", out)


if __name__ == "__main__":
    unittest.main()
