import importlib
import sys
import types
import unittest
from unittest import mock


class InlineTest(unittest.TestCase):
    def setUp(self):
        fake = types.ModuleType("core.gate")
        fake.query = lambda role, sql, params=None: []
        with mock.patch.dict(sys.modules, {"core.gate": fake}):
            sys.modules.pop("helpcenter.build", None)
            self.build = importlib.import_module("helpcenter.build")
        self.addCleanup(sys.modules.pop, "helpcenter.build", None)

    def test_bold_and_code(self):
        self.assertEqual(
            self.build.inline("Error **Invalid SAML** in `NameID` field"),
            "Error <strong>Invalid SAML</strong> in <code>NameID</code> field",
        )

    def test_still_escaped(self):
        out = self.build.inline("**<b>x</b>** and `<script>` & more")
        self.assertEqual(
            out,
            "<strong>&lt;b&gt;x&lt;/b&gt;</strong> and <code>&lt;script&gt;</code> &amp; more",
        )

    def test_markers_inside_code_stay_literal(self):
        self.assertEqual(self.build.inline("`a **b** c`"), "<code>a **b** c</code>")

    def test_code_inside_bold(self):
        self.assertEqual(
            self.build.inline("**use `sso`**"), "<strong>use <code>sso</code></strong>"
        )

    def test_unpaired_markers_untouched(self):
        self.assertEqual(self.build.inline("2 ** 3 and a ` tick"), "2 ** 3 and a ` tick")

    def test_sections_render_heading_and_body(self):
        out = self.build.sections(["[KB: Title > **Setup**]\nSet `idp_url` now"])
        self.assertIn("<h2><strong>Setup</strong></h2>", out)
        self.assertNotIn("KB: Title", out)
        self.assertIn("<p>Set <code>idp_url</code> now</p>", out)


if __name__ == "__main__":
    unittest.main()
