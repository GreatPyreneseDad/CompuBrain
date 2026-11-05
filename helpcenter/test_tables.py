import importlib
import sys
import types
import unittest
from unittest import mock


class TableTest(unittest.TestCase):
    def setUp(self):
        fake = types.ModuleType("core.gate")
        fake.query = lambda role, sql, params=None: []
        with mock.patch.dict(sys.modules, {"core.gate": fake}):
            sys.modules.pop("helpcenter.build", None)
            self.build = importlib.import_module("helpcenter.build")
        self.addCleanup(sys.modules.pop, "helpcenter.build", None)

    def test_pipe_table_becomes_table(self):
        out = self.build.blocks("| Setting | Value |\n|---|---|\n| Name ID format | EmailAddress |\n| Signed | Yes |")
        self.assertEqual(
            out,
            "<table>\n<thead>\n"
            '<tr><th scope="col">Setting</th><th scope="col">Value</th></tr>\n'
            "</thead>\n<tbody>\n"
            "<tr><td>Name ID format</td><td>EmailAddress</td></tr>\n"
            "<tr><td>Signed</td><td>Yes</td></tr>\n"
            "</tbody>\n</table>",
        )
        self.assertNotIn("|", out)

    def test_text_around_table_stays_paragraphs(self):
        out = self.build.blocks("Before:\n| a | b |\n|:--|--:|\n| 1 | 2 |\nAfter")
        self.assertTrue(out.startswith("<p>Before:</p>\n<table>"))
        self.assertTrue(out.endswith("</table>\n<p>After</p>"))

    def test_cells_are_escaped_and_inline_rendered(self):
        out = self.build.blocks("| **K** | V |\n|---|---|\n| <b> & | `x` |")
        self.assertIn('<th scope="col"><strong>K</strong></th>', out)
        self.assertIn("<td>&lt;b&gt; &amp;</td><td><code>x</code></td>", out)

    def test_short_and_long_rows_match_header_width(self):
        out = self.build.blocks("| a | b |\n|---|---|\n| 1 |\n| 1 | 2 | 3 |")
        self.assertIn("<tr><td>1</td><td></td></tr>", out)
        self.assertIn("<tr><td>1</td><td>2</td></tr>", out)
        self.assertNotIn("3", out)

    def test_escaped_pipe_is_one_cell(self):
        out = self.build.blocks("| a | b |\n|---|---|\n| x \\| y | z |")
        self.assertIn("<td>x | y</td><td>z</td>", out)

    def test_header_only_table(self):
        out = self.build.blocks("| a | b |\n|---|---|")
        self.assertIn("<thead>", out)
        self.assertNotIn("<tbody>", out)

    def test_pipe_line_without_separator_is_a_paragraph(self):
        self.assertEqual(self.build.blocks("| a | b |"), "<p>| a | b |</p>")

    def test_list_still_works_next_to_table(self):
        out = self.build.blocks("- one\n| a | b |\n|---|---|\n| 1 | 2 |\n- two")
        self.assertEqual(out.count("<ul>"), 2)
        self.assertEqual(out.count("<table>"), 1)

    def test_sections_use_tables(self):
        out = self.build.sections(["[KB: Title > Values]\n| Setting | Value |\n|---|---|\n| A | B |"])
        self.assertIn("<h2>Values</h2>", out)
        self.assertIn("<td>A</td>", out)


if __name__ == "__main__":
    unittest.main()
