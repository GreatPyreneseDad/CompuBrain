"""Tests for the plain-text heading heuristic: no line may be lost from the chunks."""
import unittest
from ingest import chunk


def _text(lines):
    return "\n\n".join(lines)


def _all_content(text):
    return "\n".join(c.content for c in chunk.split(chunk._headings_from_plain(text)))


class TestHeadingsFromPlain(unittest.TestCase):

    def test_consecutive_short_lines_are_kept(self):
        lines = ["Quarterly kickoff", "Revenue up", "Hiring plan", "Ship readers by Friday."]
        content = _all_content(_text(lines))
        for line in lines:
            self.assertIn(line, content)

    def test_short_line_before_heading_with_body_is_kept(self):
        lines = ["Revenue up", "Hiring plan\nThree engineers start in May."]
        content = _all_content(_text(lines))
        self.assertIn("Revenue up", content)
        self.assertIn("Hiring plan", content)
        self.assertIn("Three engineers start in May.", content)

    def test_only_short_lines_are_kept(self):
        lines = ["One", "Two", "Three", "Four", "Five"]
        content = _all_content(_text(lines))
        for line in lines:
            self.assertIn(line, content)

    def test_heading_still_splits_sections(self):
        text = _text(["Overview", "The plan is simple.", "Risks", "Delivery may slip."])
        chunks = chunk.split(chunk._headings_from_plain(text))
        self.assertEqual(2, len(chunks))
        self.assertTrue(chunks[0].content.startswith("[Overview]"))
        self.assertTrue(chunks[1].content.startswith("[Overview > Risks]"))

    def test_heading_with_body_on_next_line(self):
        text = "Overview\nThe plan is simple."
        self.assertEqual("# Overview\n\nThe plan is simple.", chunk._headings_from_plain(text))


if __name__ == "__main__":
    unittest.main()
