"""Extract plain text from .pptx files.

Slides are read in presentation order: ppt/presentation.xml lists them in <p:sldIdLst>, each entry points through
ppt/_rels/presentation.xml.rels to a slide part. File names (slide1.xml, slide2.xml ...) say nothing about order,
so they are used only as a fallback when the presentation part is missing or lists no slides.

Standard library only; no environment variables, no network.
"""
from __future__ import annotations

EXTENSIONS = (".pptx",)
import posixpath
import re
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

_A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
_P = 'http://schemas.openxmlformats.org/presentationml/2006/main'
_R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
_REL = 'http://schemas.openxmlformats.org/package/2006/relationships'

_SLIDE_FILE = re.compile(r'^ppt/slides/slide(\d+)\.xml$')


def _slide_names(zipf: zipfile.ZipFile) -> list:
    """Slide part names in presentation order."""
    names = set(zipf.namelist())
    ordered = []
    try:
        pres = ET.fromstring(zipf.read('ppt/presentation.xml'))
        rels = ET.fromstring(zipf.read('ppt/_rels/presentation.xml.rels'))
        targets = {r.get('Id'): r.get('Target') for r in rels.iter(f'{{{_REL}}}Relationship')}
        for sld in pres.iter(f'{{{_P}}}sldId'):
            target = targets.get(sld.get(f'{{{_R}}}id'))
            if not target:
                continue
            name = target.lstrip('/') if target.startswith('/') else posixpath.normpath(posixpath.join('ppt', target))
            if name in names:
                ordered.append(name)
    except (KeyError, ET.ParseError):
        ordered = []
    if ordered:
        return ordered
    found = [(int(m.group(1)), n) for n in names for m in [_SLIDE_FILE.match(n)] if m]
    return [n for _, n in sorted(found)]


def _slide_text(xml_bytes: bytes) -> str:
    """Text of one slide: its non-empty paragraphs, one per line.

    Slides are joined with a blank line by extract_text, so chunk.py's heading heuristic sees each slide as
    one block: first line (usually the title) as heading, the rest as its body."""
    paras = []
    root = ET.fromstring(xml_bytes)
    for p in root.iter(f'{{{_A}}}p'):
        line = ''
        for node in p.iter():
            if node.tag == f'{{{_A}}}t':
                line += node.text or ''
            elif node.tag == f'{{{_A}}}tab':
                line += '\t'
            elif node.tag == f'{{{_A}}}br':
                line += '\n'
        line = line.strip()
        if line:
            paras.append(line)
    return '\n'.join(paras)


def extract_text(pptx_path: str | Path) -> str:
    """Extract all slide text from a .pptx file, slides in presentation order.

    Raises:
        zipfile.BadZipFile: If the file is not a valid zip archive
    """
    slides = []
    with zipfile.ZipFile(pptx_path) as zipf:
        for name in _slide_names(zipf):
            text = _slide_text(zipf.read(name))
            if text:
                slides.append(text)
    return '\n\n'.join(slides).strip()
