"""Tests for .pptx text extraction."""
import unittest
import tempfile
import zipfile
from pathlib import Path
from ingest.pptx import extract_text
from ingest import chunk

_NS = ('xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
       'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"')
_PRES = ('<?xml version="1.0"?><p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
         'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><p:sldIdLst>{ids}</p:sldIdLst>'
         '</p:presentation>')
_RELS = ('<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
         '{rels}</Relationships>')
_REL = ('<Relationship Id="{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" '
        'Target="{t}"/>')


def _slide(*paragraphs: str) -> str:
    body = ''.join(f'<a:p>{p}</a:p>' for p in paragraphs)
    return (f'<?xml version="1.0"?><p:sld {_NS}><p:cSld><p:spTree><p:sp><p:txBody>{body}</p:txBody></p:sp>'
            f'</p:spTree></p:cSld></p:sld>')


def _run(text: str) -> str:
    return f'<a:r><a:t>{text}</a:t></a:r>'


class TestPptxExtraction(unittest.TestCase):

    def _make(self, slides: dict, order=None, suffix='.pptx') -> Path:
        """slides: part name -> xml. order: list of (rId, target) in presentation order, or None for no presentation part."""
        tmp = tempfile.NamedTemporaryFile(mode='wb', suffix=suffix, delete=False)
        tmp.close()
        path = Path(tmp.name)
        with zipfile.ZipFile(path, 'w') as zf:
            zf.writestr('[Content_Types].xml',
                        '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>')
            if order is not None:
                ids = ''.join(f'<p:sldId id="{256 + n}" r:id="{i}"/>' for n, (i, _) in enumerate(order))
                rels = ''.join(_REL.format(i=i, t=t) for i, t in order)
                zf.writestr('ppt/presentation.xml', _PRES.format(ids=ids))
                zf.writestr('ppt/_rels/presentation.xml.rels', _RELS.format(rels=rels))
            for name, xml in slides.items():
                zf.writestr(name, xml)
        return path

    def test_presentation_order_not_file_name_order(self):
        path = self._make(
            {'ppt/slides/slide1.xml': _slide(_run('Second slide')),
             'ppt/slides/slide2.xml': _slide(_run('First slide'))},
            order=[('rId9', 'slides/slide2.xml'), ('rId8', 'slides/slide1.xml')])
        try:
            text = extract_text(path)
            self.assertLess(text.index('First slide'), text.index('Second slide'))
        finally:
            path.unlink()

    def test_multiple_runs_join_into_one_paragraph(self):
        path = self._make({'ppt/slides/slide1.xml': _slide(_run('Tallgrass ') + _run('Logistics'))},
                          order=[('rId1', 'slides/slide1.xml')])
        try:
            self.assertEqual('Tallgrass Logistics', extract_text(path))
        finally:
            path.unlink()

    def test_paragraphs_and_line_breaks(self):
        path = self._make({'ppt/slides/slide1.xml': _slide(_run('Title'), _run('Line one') + '<a:br/>' + _run('Line two'))},
                          order=[('rId1', 'slides/slide1.xml')])
        try:
            text = extract_text(path)
            self.assertEqual('Title\nLine one\nLine two', text)
        finally:
            path.unlink()

    def test_table_cell_text_is_read(self):
        xml = (f'<?xml version="1.0"?><p:sld {_NS}><p:cSld><p:spTree><p:graphicFrame><a:tbl><a:tr><a:tc><a:txBody>'
               f'<a:p>{_run("Cell A")}</a:p></a:txBody></a:tc><a:tc><a:txBody><a:p>{_run("Cell B")}</a:p></a:txBody></a:tc>'
               f'</a:tr></a:tbl></p:graphicFrame></p:spTree></p:cSld></p:sld>')
        path = self._make({'ppt/slides/slide1.xml': xml}, order=[('rId1', 'slides/slide1.xml')])
        try:
            text = extract_text(path)
            self.assertIn('Cell A', text)
            self.assertIn('Cell B', text)
        finally:
            path.unlink()

    def test_absolute_target(self):
        path = self._make({'ppt/slides/slide1.xml': _slide(_run('Absolute'))},
                          order=[('rId1', '/ppt/slides/slide1.xml')])
        try:
            self.assertEqual('Absolute', extract_text(path))
        finally:
            path.unlink()

    def test_fallback_sorts_slide_files_numerically(self):
        path = self._make({'ppt/slides/slide10.xml': _slide(_run('Tenth')),
                           'ppt/slides/slide2.xml': _slide(_run('Second'))})
        try:
            text = extract_text(path)
            self.assertLess(text.index('Second'), text.index('Tenth'))
        finally:
            path.unlink()

    def test_empty_deck(self):
        path = self._make({}, order=[])
        try:
            self.assertEqual('', extract_text(path))
        finally:
            path.unlink()

    def test_not_a_zip_raises(self):
        tmp = tempfile.NamedTemporaryFile(mode='wb', suffix='.pptx', delete=False)
        tmp.write(b'not a zip')
        tmp.close()
        path = Path(tmp.name)
        try:
            with self.assertRaises(zipfile.BadZipFile):
                extract_text(path)
        finally:
            path.unlink()

    def test_registered_and_loads_through_chunk(self):
        self.assertIn('.pptx', chunk.READERS)
        path = self._make(
            {'ppt/slides/slide1.xml': _slide(_run('Q4 kickoff'), _run('Three accounts carry the quarter'))},
            order=[('rId1', 'slides/slide1.xml')], suffix='.PPTX')
        try:
            doc = chunk.load(path, source='test', default_scope='internal')
            self.assertFalse(doc.pretagged)
            self.assertTrue(doc.chunks)
            self.assertIn('Three accounts carry the quarter', doc.chunks[0].content)
            with self.assertRaises(ValueError):
                chunk.load(path, source=None, default_scope=None)
        finally:
            path.unlink()


if __name__ == '__main__':
    unittest.main()
