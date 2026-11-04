"""Extract plain text from .xlsx workbooks.

Each sheet becomes a block: the sheet name on its own line (chunk.py turns it into a section heading), then one
line per non-empty row with the cells joined by " | ". Standard library only (zipfile and XML).
"""
from __future__ import annotations

EXTENSIONS = (".xlsx",)
import posixpath
import re
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path


def _local(tag: str) -> str:
    """Tag or attribute name without its namespace, so transitional and strict OOXML read the same."""
    return tag.rsplit("}", 1)[-1]


def _text(el) -> str:
    """Text of a shared-string <si> or inline-string <is>: plain <t> and rich-text <r><t> runs.
    Phonetic hints (<rPh>) are skipped."""
    parts = []
    for child in el:
        name = _local(child.tag)
        if name == "t":
            parts.append(child.text or "")
        elif name == "r":
            parts.extend(t.text or "" for t in child if _local(t.tag) == "t")
    return "".join(parts)


def _shared_strings(zipf: zipfile.ZipFile) -> list:
    if "xl/sharedStrings.xml" not in zipf.namelist():
        return []
    root = ET.fromstring(zipf.read("xl/sharedStrings.xml"))
    return [_text(si) for si in root if _local(si.tag) == "si"]


def _sheets(zipf: zipfile.ZipFile) -> list:
    """(name, part path) for each sheet, in workbook order."""
    workbook = ET.fromstring(zipf.read("xl/workbook.xml"))
    targets = {}
    if "xl/_rels/workbook.xml.rels" in zipf.namelist():
        rels = ET.fromstring(zipf.read("xl/_rels/workbook.xml.rels"))
        for rel in rels:
            target = rel.get("Target")
            if rel.get("Id") and target:
                targets[rel.get("Id")] = (target.lstrip("/") if target.startswith("/")
                                          else posixpath.normpath(posixpath.join("xl", target)))
    out = []
    for el in workbook.iter():
        if _local(el.tag) != "sheet":
            continue
        rid = next((v for k, v in el.attrib.items() if _local(k) == "id"), None)
        part = targets.get(rid)
        if part:
            out.append((el.get("name") or "Sheet", part))
    return out


def _col_index(ref: str):
    m = re.match(r"[A-Za-z]+", ref or "")
    if not m:
        return None
    n = 0
    for ch in m.group(0).upper():
        n = n * 26 + ord(ch) - 64
    return n - 1


def _cell_value(c, shared: list) -> str:
    kind = c.get("t")
    if kind == "inlineStr":
        for child in c:
            if _local(child.tag) == "is":
                return " ".join(_text(child).split())
        return ""
    v = next((child.text for child in c if _local(child.tag) == "v"), None)
    if v is None:
        return ""
    if kind == "s":
        try:
            v = shared[int(v)]
        except (ValueError, IndexError):
            return ""
    elif kind == "b":
        v = "TRUE" if v.strip() == "1" else "FALSE"
    return " ".join(v.split())


def _rows(xml_bytes: bytes, shared: list) -> list:
    rows = []
    for row in ET.fromstring(xml_bytes).iter():
        if _local(row.tag) != "row":
            continue
        cells, nxt = {}, 0
        for c in row:
            if _local(c.tag) != "c":
                continue
            idx = _col_index(c.get("r"))
            if idx is None:
                idx = nxt
            nxt = idx + 1
            val = _cell_value(c, shared)
            if val:
                cells[idx] = val
        if cells:
            rows.append(" | ".join(cells.get(i, "") for i in range(max(cells) + 1)))
    return rows


def extract_text(xlsx_path: str | Path) -> str:
    """Extract all cell text from an .xlsx file, one block per sheet (sheet name, then its rows).

    Raises:
        zipfile.BadZipFile: If the file is not a zip archive
        KeyError: If xl/workbook.xml is missing (not a valid .xlsx)
    """
    blocks = []
    with zipfile.ZipFile(xlsx_path) as zipf:
        shared = _shared_strings(zipf)
        for name, part in _sheets(zipf):
            if part not in zipf.namelist():
                continue
            rows = _rows(zipf.read(part), shared)
            if rows:
                blocks.append(" ".join(name.split()) + "\n" + "\n".join(rows))
    return "\n\n".join(blocks)
