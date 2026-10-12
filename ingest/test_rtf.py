"""Tests for RTF text extraction."""
import unittest
import tempfile
from pathlib import Path
from ingest.rtf import extract_text


class TestRtfExtraction(unittest.TestCase):
    """Test RTF-to-plaintext conversion against synthetic RTF documents."""
    
    def _make_rtf(self, body: str) -> Path:
        """Create a minimal RTF file for testing."""
        rtf_content = r'{\rtf1\ansi\deff0' + '\n' + body + '\n}'
        tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.rtf', delete=False, encoding='cp1252')
        tmp.write(rtf_content)
        tmp.close()
        return Path(tmp.name)
    
    def test_simple_paragraph(self):
        """Plain text extracts cleanly."""
        path = self._make_rtf(r'Hello World\par')
        try:
            text = extract_text(path)
            self.assertIn('Hello World', text)
        finally:
            path.unlink()
    
    def test_multiple_paragraphs(self):
        """\\par produces newlines."""
        path = self._make_rtf(r'First paragraph\par Second paragraph\par')
        try:
            text = extract_text(path)
            self.assertIn('First paragraph', text)
            self.assertIn('Second paragraph', text)
            self.assertIn('\n', text)
        finally:
            path.unlink()
    
    def test_special_chars(self):
        """RTF special characters map to Unicode equivalents."""
        path = self._make_rtf(r'Em\emdash dash\endash bullet\bullet tab\tab line\line')
        try:
            text = extract_text(path)
            self.assertIn('\u2014', text)  # em dash
            self.assertIn('\u2013', text)  # en dash
            self.assertIn('\u2022', text)  # bullet
            self.assertIn('\t', text)      # tab
            self.assertIn('\n', text)      # line break
        finally:
            path.unlink()
    
    def test_unicode_escape(self):
        """\\uNNNN escapes decode to Unicode."""
        path = self._make_rtf(r'\u8364? Euro sign')  # € = U+20AC = 8364 decimal
        try:
            text = extract_text(path)
            self.assertIn('€', text)
        finally:
            path.unlink()
    
    def test_hex_escape(self):
        """\\\'hh hex bytes decode per charset."""
        # \'e9 in cp1252 is é (U+00E9)
        path = self._make_rtf(r"Caf\'e9")
        try:
            text = extract_text(path)
            self.assertIn('é', text)
            self.assertIn('Café', text)
        finally:
            path.unlink()
    
    def test_ignorable_destinations(self):
        """Content inside \\fonttbl, \\colortbl, etc. is discarded."""
        path = self._make_rtf(r'{\fonttbl{\f0 Times;}}Body text\par')
        try:
            text = extract_text(path)
            self.assertNotIn('Times', text)
            self.assertIn('Body text', text)
        finally:
            path.unlink()
    
    def test_nested_groups(self):
        """Nested groups preserve scope."""
        path = self._make_rtf(r'Outer{\b bold{\i italic}back}end\par')
        try:
            text = extract_text(path)
            # Formatting commands are ignored; text is concatenated.
            self.assertIn('Outer', text)
            self.assertIn('bold', text)
            self.assertIn('italic', text)
            self.assertIn('back', text)
            self.assertIn('end', text)
        finally:
            path.unlink()
    
    def test_table_cells(self):
        """\\cell and \\row produce pipe and newline."""
        path = self._make_rtf(r'A\cell B\cell\row C\cell D\cell\row')
        try:
            text = extract_text(path)
            self.assertIn('|', text)  # cell separator
            self.assertIn('A', text)
            self.assertIn('B', text)
        finally:
            path.unlink()
    
    def test_binary_pict_removal(self):
        """\\pict...\\bin groups with binary data are stripped."""
        path = self._make_rtf(r'Before{\pict\bin4 ####}After\par')
        try:
            text = extract_text(path)
            self.assertIn('Before', text)
            self.assertIn('After', text)
            self.assertNotIn('#', text)  # binary data removed
        finally:
            path.unlink()
    
    def test_hyperlinks(self):
        """HYPERLINK fields convert to text(url) format."""
        rtf = (r'{\field{\*\fldinst{HYPERLINK "http://example.com"}}'
               r'{\fldrslt{Click here}}}')
        path = self._make_rtf(rtf)
        try:
            text = extract_text(path)
            # Exact format may vary; check both components are present.
            self.assertIn('example.com', text)
            self.assertIn('Click here', text)
        finally:
            path.unlink()
    
    def test_empty_document(self):
        """Empty RTF body returns empty string."""
        path = self._make_rtf('')
        try:
            text = extract_text(path)
            self.assertEqual('', text)
        finally:
            path.unlink()
    
    def test_charset_directive(self):
        """\\ansicpgNNN overrides default encoding."""
        # cp1251 (Cyrillic): \'e0 = а (U+0430)
        rtf_content = r'{\rtf1\ansi\ansicpg1251\deff0' + '\n' + r"Test \'e0\par" + '\n}'
        tmp = tempfile.NamedTemporaryFile(mode='wb', suffix='.rtf', delete=False)
        tmp.write(rtf_content.encode('cp1252'))
        tmp.close()
        path = Path(tmp.name)
        try:
            text = extract_text(path)
            self.assertIn('а', text)  # Cyrillic а
        finally:
            path.unlink()


if __name__ == '__main__':
    unittest.main()
