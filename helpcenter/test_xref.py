import importlib
import sys
import types
import unittest
from unittest import mock

DOCS = [
    ("a", "Billing FAQ"),
    ("b", "Refund Policy for Enterprise Customers"),
    ("c", "Refund Policy for Teams"),
    ("d", "Single Sign-On Setup"),
    ("e", "Support KB: Data Connectors"),
    ("f", "Support KB \u2014 Usage Limits"),
]


class XrefTest(unittest.TestCase):
    def setUp(self):
        fake = types.ModuleType("core.gate")
        fake.query = lambda role, sql, params=None: []
        with mock.patch.dict(sys.modules, {"core.gate": fake}):
            sys.modules.pop("helpcenter.build", None)
            self.build = importlib.import_module("helpcenter.build")
        self.addCleanup(sys.modules.pop, "helpcenter.build", None)
        self.names = self.build.slugs(sorted(DOCS, key=lambda d: (d[1], d[0])))
        self.linker = self.build.xref_linker(DOCS, self.names)

    def render(self, text, current="a"):
        return self.build.blocks(text, self.linker(current))

    def test_leading_words_of_title_link(self):
        out = self.render("See the separate Refund Policy for Teams article for details.")
        self.assertIn(
            '<a href="doc-refund-policy-for-teams.html">Refund Policy for Teams article</a>', out
        )

    def test_full_title_and_case_and_line_wrap(self):
        out = self.render("Read the single sign-on\nsetup article first.")
        self.assertIn('<a href="doc-single-sign-on-setup.html">single sign-on\nsetup article</a>', out)

    def test_ambiguous_prefix_is_not_linked(self):
        out = self.render("The Refund Policy article applies.")
        self.assertNotIn("<a ", out)
        self.assertEqual(out, "<p>The Refund Policy article applies.</p>")

    def test_no_link_to_itself(self):
        out = self.render("This Billing FAQ article is long.", current="a")
        self.assertNotIn("<a ", out)
        self.assertIn("<a ", self.render("This Billing FAQ article is long.", current="c"))

    def test_needs_the_word_article(self):
        self.assertNotIn("<a ", self.render("The Refund Policy for Teams applies."))

    def test_single_leading_word_does_not_match(self):
        self.assertNotIn("<a ", self.render("The Single article."))

    def test_title_without_its_source_prefix_links(self):
        out = self.render("See the separate Data Connectors article.")
        self.assertIn('<a href="doc-support-kb-data-connectors.html">Data Connectors article</a>', out)
        self.assertIn("<a ", self.render("The Support KB: Data Connectors article."))

    def test_dash_separated_source_prefix_links(self):
        out = self.render("See the Usage Limits article.")
        self.assertIn('<a href="doc-support-kb-usage-limits.html">Usage Limits article</a>', out)

    def test_text_is_still_escaped(self):
        out = self.render("<i> & Refund Policy for Teams article <b>")
        self.assertIn("&lt;i&gt; &amp; <a ", out)
        self.assertTrue(out.endswith("</a> &lt;b&gt;</p>"))
        self.assertNotIn("<i>", out)

    def test_urls_and_code_are_left_alone(self):
        out = self.render("`Refund Policy for Teams article` and https://x.example/Refund Policy for Teams article")
        self.assertIn("<code>Refund Policy for Teams article</code>", out)
        self.assertIn('<a href="https://x.example/Refund">https://x.example/Refund</a>', out)

    def test_lists_and_tables_link(self):
        out = self.render("- the Refund Policy for Teams article\n\n| a |\n|---|\n| Refund Policy for Teams article |")
        self.assertEqual(out.count('<a href="doc-refund-policy-for-teams.html">'), 2)

    def test_default_renderer_does_not_link(self):
        self.assertNotIn("<a ", self.build.blocks("the Refund Policy for Teams article"))

    def test_no_documents(self):
        linker = self.build.xref_linker([], {})
        self.assertEqual(self.build.blocks("a <b> article", linker("x")), "<p>a &lt;b&gt; article</p>")


if __name__ == "__main__":
    unittest.main()
