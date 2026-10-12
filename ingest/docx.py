"""Extract plain text from .docx files.

Upstream: ankushshah89/python-docx2txt @ 0ae7fce1c208
License: MIT
Repo: https://github.com/ankushshah89/python-docx2txt

Adapted for Company Brain:
- Removed CLI, image extraction, and sys.stdout writes
- Returns string from extract_text() instead of writing bytes
- Integrated into ingest pipeline (no standalone script)
"""
from __future__ import annotations
import re
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

# Namespace map for Office Open XML (Word 2007+)
_NSMAP = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}


def _qn(tag: str) -> str:
    """Convert namespace-prefixed tag to Clark notation.
    
    Example: 'w:t' -> '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'
    """
    prefix, tagroot = tag.split(':')
    uri = _NSMAP[prefix]
    return f'{{{uri}}}{tagroot}'


def _xml_to_text(xml_bytes: bytes) -> str:
    """Extract textual content from Word XML, translating structural elements.
    
    Maps:
    - <w:t> -> text content
    - <w:tab/> -> tab character
    - <w:br/>, <w:cr/> -> newline
    - <w:p> -> double newline (paragraph break)
    """
    text = ''
    root = ET.fromstring(xml_bytes)
    for child in root.iter():
        if child.tag == _qn('w:t'):
            t_text = child.text
            text += t_text if t_text is not None else ''
        elif child.tag == _qn('w:tab'):
            text += '\t'
        elif child.tag in (_qn('w:br'), _qn('w:cr')):
            text += '\n'
        elif child.tag == _qn('w:p'):
            text += '\n\n'
    return text


def extract_text(docx_path: str | Path) -> str:
    """Extract all text from a .docx file.
    
    Processes header, main document, and footer XML files inside the .docx archive.
    Returns concatenated plain text with original paragraph/line breaks preserved.
    
    Args:
        docx_path: Path to .docx file
        
    Returns:
        Plain text content, stripped of leading/trailing whitespace
        
    Raises:
        zipfile.BadZipFile: If file is not a valid zip archive
        KeyError: If document.xml is missing (not a valid .docx)
    """
    text = ''
    
    with zipfile.ZipFile(docx_path) as zipf:
        filelist = zipf.namelist()
        
        # Extract header text (0-3 header files may exist)
        header_pattern = re.compile(r'^word/header[0-9]*\.xml$')
        for fname in filelist:
            if header_pattern.match(fname):
                text += _xml_to_text(zipf.read(fname))
        
        # Extract main document text
        text += _xml_to_text(zipf.read('word/document.xml'))
        
        # Extract footer text (0-3 footer files may exist)
        footer_pattern = re.compile(r'^word/footer[0-9]*\.xml$')
        for fname in filelist:
            if footer_pattern.match(fname):
                text += _xml_to_text(zipf.read(fname))
    
    return text.strip()
