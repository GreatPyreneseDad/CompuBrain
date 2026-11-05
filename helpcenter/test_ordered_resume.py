import importlib
import sys
import types
import unittest
from unittest import mock


class OrderedResumeTest(unittest.TestCase):
    def setUp(self):
        fake = types.ModuleType("core.gate")
        fake.query = lambda role, sql, params=None: []
        with mock.patch.dict(sys.modules, {"core.gate": fake}):
            sys.modules.pop("helpcenter.build", None)
            self.build = importlib.import_module("helpcenter.build")
        self.addCleanup(sys.modules.pop, "helpcenter.build", None)

    def test_steps_resume_after_bullets(self):
        out = self.build.blocks(
            "1. Check\n2. Match\n   - `A`: one\n   - `B`: two\n3. Retry\n4. Ticket"
        )
        self.assertEqual(
            out,
            "<ol>\n<li>Check</li>\n<li>Match</li>\n</ol>\n"
            "<ul>\n<li><code>A</code>: one</li>\n<li><code>B</code>: two</li>\n</ul>\n"
            '<ol start="3">\n<li>Retry</li>\n<li>Ticket</li>\n</ol>',
        )

    def test_list_starting_at_one_has_no_start(self):
        out = self.build.blocks("1. a\n2. b")
        self.assertNotIn("start", out)

    def test_uninterrupted_run_uses_its_first_number_only(self):
        out = self.build.blocks("3. a\n4. b")
        self.assertEqual(out, '<ol start="3">\n<li>a</li>\n<li>b</li>\n</ol>')
        self.assertEqual(out.count("<ol"), 1)


if __name__ == "__main__":
    unittest.main()
