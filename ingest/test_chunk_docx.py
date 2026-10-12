"""Integration tests: .docx files through the chunk.load pipeline."""
import unittest
import tempfile
import zipfile
from pathlib import Path
from ingest import chunk


class TestChunkDocx(unittest.TestCase):
    """Test that .docx files load and chunk like .md/.txt."""
    
    def _make_docx_with_text(self, text_content: str) -> Path:
        """Create a .docx containing the given plain text as one paragraph."""
        tmp = tempfile.NamedTemporaryFile(mode='wb', suffix='.docx', delete=False)
        tmp.close()
        path = Path(tmp.name)
        
        # Wrap text in minimal Word XML
        doc_xml = f'''<?xml version="1.0"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p><w:r><w:t>{text_content}</w:t></w:r></w:p>
  </w:body>
</w:document>'''
        
        with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr('[Content_Types].xml',
                       '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>')
            zf.writestr('word/document.xml', doc_xml)
        
        return path
    
    def _make_docx_with_paragraphs(self, paragraphs: list[str]) -> Path:
        """Create a .docx with multiple paragraphs."""
        tmp = tempfile.NamedTemporaryFile(mode='wb', suffix='.docx', delete=False)
        tmp.close()
        path = Path(tmp.name)
        
        # Build multiple <w:p> elements
        para_xml = '\n'.join(f'<w:p><w:r><w:t>{p}</w:t></w:r></w:p>' for p in paragraphs)
        doc_xml = f'''<?xml version="1.0"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    {para_xml}
  </w:body>
</w:document>'''
        
        with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr('[Content_Types].xml',
                       '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>')
            zf.writestr('word/document.xml', doc_xml)
        
        return path
    
    def test_load_docx_without_frontmatter(self):
        """A .docx with no frontmatter loads with supplied source and scope."""
        path = self._make_docx_with_text("This is a test document about expense policies.")
        try:
            doc = chunk.load(path, source="upload", default_scope="finance")
            self.assertEqual("upload", doc.source)
            self.assertEqual("finance", doc.default_scope)
            self.assertFalse(doc.pretagged)
            self.assertTrue(len(doc.chunks) > 0)
            self.assertIn("expense policies", doc.chunks[0].content)
        finally:
            path.unlink()
    
    def test_docx_title_from_stem(self):
        """Title derives from filename when no frontmatter present."""
        tmp = tempfile.NamedTemporaryFile(mode='wb', suffix='.docx', delete=False, 
                                         prefix='q4-sales-targets-')
        tmp.close()
        path = Path(tmp.name)
        
        doc_xml = '''<?xml version="1.0"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body><w:p><w:r><w:t>Content here</w:t></w:r></w:p></w:body>
</w:document>'''
        
        with zipfile.ZipFile(path, 'w') as zf:
            zf.writestr('[Content_Types].xml', '<?xml version="1.0"?><Types/>')
            zf.writestr('word/document.xml', doc_xml)
        
        try:
            doc = chunk.load(path, source="upload", default_scope="sales")
            # stem is "q4-sales-targets-<random>", title is titlecased with hyphens->spaces
            self.assertIn("Q4", doc.title)
            self.assertIn("Sales", doc.title)
        finally:
            path.unlink()
    
    def test_docx_chunks_like_markdown(self):
        """Chunking behavior matches .md: long text splits into multiple chunks."""
        # Generate multiple paragraphs, each ~100 words, to exceed MAX_WORDS (300) per chunk
        paragraphs = []
        for i in range(5):
            para = " ".join([f"Word{i}_{j}" for j in range(100)])
            paragraphs.append(para)
        
        path = self._make_docx_with_paragraphs(paragraphs)
        
        try:
            doc = chunk.load(path, source="test", default_scope="internal")
            # 5 paragraphs * 100 words = 500 words total
            # _pack() should create at least 2 chunks (MAX_WORDS=300)
            self.assertGreater(len(doc.chunks), 1, 
                             f"Expected multiple chunks for 500-word document, got {len(doc.chunks)}")
            # Each chunk should have content
            for c in doc.chunks:
                self.assertTrue(len(c.content) > 0)
        finally:
            path.unlink()


if __name__ == '__main__':
    unittest.main()
