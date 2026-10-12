"""Tests for .docx text extraction."""
import unittest
import tempfile
import zipfile
from pathlib import Path
from ingest.docx import extract_text


class TestDocxExtraction(unittest.TestCase):
    """Test .docx text extraction against synthetic documents."""
    
    def _make_docx(self, content_xml: str, headers: list[str] = None, footers: list[str] = None) -> Path:
        """Create a minimal valid .docx file for testing."""
        tmp = tempfile.NamedTemporaryFile(mode='wb', suffix='.docx', delete=False)
        tmp.close()
        path = Path(tmp.name)
        
        with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Minimal required structure
            zf.writestr('[Content_Types].xml', 
                       '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>')
            zf.writestr('word/document.xml', content_xml)
            
            # Optional headers/footers
            if headers:
                for i, h in enumerate(headers):
                    zf.writestr(f'word/header{i+1}.xml', h)
            if footers:
                for i, f in enumerate(footers):
                    zf.writestr(f'word/footer{i+1}.xml', f)
        
        return path
    
    def test_simple_paragraph(self):
        """Single paragraph extracts cleanly."""
        doc_xml = '''<?xml version="1.0"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p><w:r><w:t>Hello World</w:t></w:r></w:p>
  </w:body>
</w:document>'''
        path = self._make_docx(doc_xml)
        try:
            text = extract_text(path)
            self.assertIn('Hello World', text)
        finally:
            path.unlink()
    
    def test_multiple_paragraphs(self):
        """Paragraph breaks produce double newlines."""
        doc_xml = '''<?xml version="1.0"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p><w:r><w:t>First paragraph</w:t></w:r></w:p>
    <w:p><w:r><w:t>Second paragraph</w:t></w:r></w:p>
  </w:body>
</w:document>'''
        path = self._make_docx(doc_xml)
        try:
            text = extract_text(path)
            self.assertIn('First paragraph', text)
            self.assertIn('Second paragraph', text)
            # Paragraph breaks should create vertical space
            self.assertIn('\n', text)
        finally:
            path.unlink()
    
    def test_tabs_and_breaks(self):
        """Tabs and line breaks map to their text equivalents."""
        doc_xml = '''<?xml version="1.0"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p>
      <w:r><w:t>Column A</w:t></w:r>
      <w:r><w:tab/></w:r>
      <w:r><w:t>Column B</w:t></w:r>
      <w:r><w:br/></w:r>
      <w:r><w:t>Next line</w:t></w:r>
    </w:p>
  </w:body>
</w:document>'''
        path = self._make_docx(doc_xml)
        try:
            text = extract_text(path)
            self.assertIn('\t', text)  # tab preserved
            self.assertIn('Column A', text)
            self.assertIn('Column B', text)
            self.assertIn('Next line', text)
        finally:
            path.unlink()
    
    def test_headers_and_footers(self):
        """Header and footer content is included."""
        doc_xml = '''<?xml version="1.0"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p><w:r><w:t>Body content</w:t></w:r></w:p>
  </w:body>
</w:document>'''
        header_xml = '''<?xml version="1.0"?>
<w:hdr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:p><w:r><w:t>Header text</w:t></w:r></w:p>
</w:hdr>'''
        footer_xml = '''<?xml version="1.0"?>
<w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:p><w:r><w:t>Footer text</w:t></w:r></w:p>
</w:ftr>'''
        path = self._make_docx(doc_xml, headers=[header_xml], footers=[footer_xml])
        try:
            text = extract_text(path)
            self.assertIn('Header text', text)
            self.assertIn('Body content', text)
            self.assertIn('Footer text', text)
        finally:
            path.unlink()
    
    def test_empty_document(self):
        """Empty document returns empty string."""
        doc_xml = '''<?xml version="1.0"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body/>
</w:document>'''
        path = self._make_docx(doc_xml)
        try:
            text = extract_text(path)
            self.assertEqual('', text)
        finally:
            path.unlink()
    
    def test_missing_document_xml_raises(self):
        """Missing document.xml raises KeyError."""
        tmp = tempfile.NamedTemporaryFile(mode='wb', suffix='.docx', delete=False)
        tmp.close()
        path = Path(tmp.name)
        
        with zipfile.ZipFile(path, 'w') as zf:
            zf.writestr('[Content_Types].xml', '<?xml version="1.0"?><Types/>')
            # No word/document.xml
        
        try:
            with self.assertRaises(KeyError):
                extract_text(path)
        finally:
            path.unlink()


if __name__ == '__main__':
    unittest.main()
