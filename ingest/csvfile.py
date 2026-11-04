"""Extract plain text from .csv files.

One line per non-empty row, cells joined by " | " (the same shape xlsx.py produces). The csv module does the
parsing, so a quoted field that contains a comma or a line break stays one cell. The delimiter is taken from the
header line (comma, semicolon, tab or pipe, comma if none). Standard library only.
"""
from __future__ import annotations

EXTENSIONS = (".csv",)
import csv
import io
from pathlib import Path

_DELIMITERS = ",;\t|"


def _delimiter(text: str) -> str:
    """The candidate delimiter that occurs most often on the first line; a comma when none occurs."""
    first = text.split("\n", 1)[0]
    best = max(_DELIMITERS, key=lambda d: (first.count(d), d == ","))
    return best if first.count(best) else ","


def extract_text(csv_path: str | Path) -> str:
    """Extract every row of a .csv file as text, one line per row.

    Cells have their whitespace collapsed, trailing empty cells are dropped and empty rows are skipped.
    """
    text = Path(csv_path).read_bytes().decode("utf-8-sig", errors="replace")
    rows = []
    for row in csv.reader(io.StringIO(text, newline=""), delimiter=_delimiter(text)):
        cells = [" ".join(cell.split()) for cell in row]
        while cells and not cells[-1]:
            cells.pop()
        if cells:
            rows.append(" | ".join(cells))
    return "\n".join(rows)
