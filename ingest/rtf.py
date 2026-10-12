"""Extract plain text from RTF files.

Upstream: joshy/striprtf @ 4f856ae78d19
License: BSD-3-Clause
Repo: https://github.com/joshy/striprtf

Adapted for Company Brain:
- Removed font_table_group() optimization (main parser tracks fonts inline)
- Removed codecs.lookup() validation (rely on decode() to raise)
- Simplified to extract_text(path) -> str interface matching docx.py
- No CLI, no network calls, stdlib only
"""
from __future__ import annotations
import re
from pathlib import Path

# Control words which specify a "destination" (content to ignore).
_DESTINATIONS = frozenset((
    'aftncn', 'aftnsep', 'aftnsepc', 'annotation', 'atnauthor', 'atndate', 'atnicn', 'atnid',
    'atnparent', 'atnref', 'atntime', 'atrfend', 'atrfstart', 'author', 'background',
    'bkmkend', 'bkmkstart', 'blipuid', 'buptim', 'category', 'colorschememapping',
    'colortbl', 'comment', 'company', 'creatim', 'datafield', 'datastore', 'defchp', 'defpap',
    'do', 'doccomm', 'docvar', 'dptxbxtext', 'ebcend', 'ebcstart', 'factoidname', 'falt',
    'fchars', 'ffdeftext', 'ffentrymcr', 'ffexitmcr', 'ffformat', 'ffhelptext', 'ffl',
    'ffname', 'ffstattext', 'file', 'filetbl', 'fldinst', 'fldtype', 'fonttbl',
    'fname', 'fontemb', 'fontfile', 'footer', 'footerf', 'footerl', 'footerr',
    'footnote', 'formfield', 'ftncn', 'ftnsep', 'ftnsepc', 'g', 'generator', 'gridtbl',
    'header', 'headerf', 'headerl', 'headerr', 'hl', 'hlfr', 'hlinkbase', 'hlloc', 'hlsrc',
    'hsv', 'htmltag', 'info', 'keycode', 'keywords', 'latentstyles', 'lchars', 'levelnumbers',
    'leveltext', 'lfolevel', 'linkval', 'list', 'listlevel', 'listname', 'listoverride',
    'listoverridetable', 'listpicture', 'liststylename', 'listtable',
    'lsdlockedexcept', 'macc', 'maccPr', 'mailmerge', 'maln', 'malnScr', 'manager', 'margPr',
    'mbar', 'mbarPr', 'mbaseJc', 'mbegChr', 'mborderBox', 'mborderBoxPr', 'mbox', 'mboxPr',
    'mchr', 'mcount', 'mctrlPr', 'md', 'mdeg', 'mdegHide', 'mden', 'mdiff', 'mdPr', 'me',
    'mendChr', 'meqArr', 'meqArrPr', 'mf', 'mfName', 'mfPr', 'mfunc', 'mfuncPr', 'mgroupChr',
    'mgroupChrPr', 'mgrow', 'mhideBot', 'mhideLeft', 'mhideRight', 'mhideTop', 'mhtmltag',
    'mlim', 'mlimloc', 'mlimlow', 'mlimlowPr', 'mlimupp', 'mlimuppPr', 'mm', 'mmaddfieldname',
    'mmath', 'mmathPict', 'mmathPr', 'mmaxdist', 'mmc', 'mmcJc', 'mmconnectstr',
    'mmconnectstrdata', 'mmcPr', 'mmcs', 'mmdatasource', 'mmheadersource', 'mmmailsubject',
    'mmodso', 'mmodsofilter', 'mmodsofldmpdata', 'mmodsomappedname', 'mmodsoname',
    'mmodsorecipdata', 'mmodsosort', 'mmodsosrc', 'mmodsotable', 'mmodsoudl',
    'mmodsoudldata', 'mmodsouniquetag', 'mmPr', 'mmquery', 'mmr', 'mnary', 'mnaryPr',
    'mnoBreak', 'mnum', 'mobjDist', 'moMath', 'moMathPara', 'moMathParaPr', 'mopEmu',
    'mphant', 'mphantPr', 'mplcHide', 'mpos', 'mr', 'mrad', 'mradPr', 'mrPr', 'msepChr',
    'mshow', 'mshp', 'msPre', 'msPrePr', 'msSub', 'msSubPr', 'msSubSup', 'msSubSupPr', 'msSup',
    'msSupPr', 'mstrikeBLTR', 'mstrikeH', 'mstrikeTLBR', 'mstrikeV', 'msub', 'msubHide',
    'msup', 'msupHide', 'mtransp', 'mtype', 'mvertJc', 'mvfmf', 'mvfml', 'mvtof', 'mvtol',
    'mzeroAsc', 'mzeroDesc', 'mzeroWid', 'nesttableprops', 'nextfile', 'nonesttables',
    'objalias', 'objclass', 'objdata', 'object', 'objname', 'objsect', 'objtime', 'oldcprops',
    'oldpprops', 'oldsprops', 'oldtprops', 'oleclsid', 'operator', 'panose', 'password',
    'passwordhash', 'pgp', 'pgptbl', 'picprop', 'pict', 'pn', 'pnseclvl', 'pntext', 'pntxta',
    'pntxtb', 'printim', 'private', 'propname', 'protend', 'protstart', 'protusertbl', 'pxe',
    'result', 'revtbl', 'revtim', 'rsidtbl', 'rxe', 'shp', 'shpgrp', 'shpinst',
    'shppict', 'shprslt', 'shptxt', 'sn', 'sp', 'staticval', 'stylesheet', 'subject', 'sv',
    'svb', 'tc', 'template', 'themedata', 'title', 'txe', 'ud', 'upr', 'userprops',
    'wgrffmtfilter', 'windowcaption', 'writereservation', 'writereservhash', 'xe', 'xform',
    'xmlattrname', 'xmlattrvalue', 'xmlclose', 'xmlname', 'xmlnstbl', 'xmlopen',
))

# Map RTF charset numbers to Python encoding names.
_CHARSET_MAP = {
    0: 'cp1252',          # Default (ANSI Western)
    42: 'cp1252',         # Symbol
    77: 'mac_roman',      # Mac Roman
    78: 'mac_japanese',   # Mac Japanese
    79: 'mac_chinesetrad',  # Mac Traditional Chinese
    80: 'mac_korean',     # Mac Korean
    81: 'mac_arabic',     # Mac Arabic
    82: 'mac_hebrew',     # Mac Hebrew
    83: 'mac_greek',      # Mac Greek
    84: 'mac_cyrillic',   # Mac Cyrillic
    85: 'mac_chinesesimp',  # Mac Simplified Chinese
    86: 'mac_rumanian',   # Mac Romanian
    87: 'mac_ukrainian',  # Mac Ukrainian
    88: 'mac_thai',       # Mac Thai
    89: 'mac_ce',         # Mac Central European
    128: 'cp932',         # Japanese
    129: 'cp949',         # Korean
    130: 'cp1361',        # Johab (Korean)
    134: 'cp936',         # Simplified Chinese (GBK)
    136: 'cp950',         # Traditional Chinese (Big5)
    161: 'cp1253',        # Greek
    162: 'cp1254',        # Turkish
    163: 'cp1258',        # Vietnamese
    177: 'cp1255',        # Hebrew
    178: 'cp1256',        # Arabic
    186: 'cp1257',        # Baltic
    204: 'cp1251',        # Cyrillic
    222: 'cp874',         # Thai
    238: 'cp1250',        # Eastern European
    254: 'cp437',         # OEM United States
    255: 'cp850',         # OEM Multilingual Latin 1
}

# Section breaks and special characters (subset that resets formatting).
_SECTIONCHARS = {'par': '\n', 'sect': '\n\n', 'page': '\n\n'}

# Translation of RTF special characters to Unicode.
_SPECIALCHARS = {
    'line': '\n',
    'tab': '\t',
    'emdash': '\u2014',
    'endash': '\u2013',
    'emspace': '\u2003',
    'enspace': '\u2002',
    'qmspace': '\u2005',
    'bullet': '\u2022',
    'lquote': '\u2018',
    'rquote': '\u2019',
    'ldblquote': '\u201C',
    'rdblquote': '\u201D',
    'row': '\n',
    'cell': '|',
    'nestcell': '|',
    '~': '\xa0',
    '\n': '\n',
    '\r': '\r',
    '{': '{',
    '}': '}',
    '\\': '\\',
    '-': '\xad',
    '_': '\u2011',
    **_SECTIONCHARS,
}

# Regex to tokenize RTF: control word, hex escape, special char, brace, or text.
_PATTERN = re.compile(
    r'\\([a-z]{1,32})(-?\d{1,10})?[ ]?'  # \controlword123
    r"|\\\'([0-9a-f]{2})"                # \'hh hex escape
    r'|\\([^a-z])'                       # \X special char
    r'|([{}])'                           # braces
    r'|[\r\n]+'                          # line breaks (ignored)
    r'|(.)',                             # any other char
    re.IGNORECASE
)

# Regex to detect and rewrite RTF hyperlinks: {{\field...HYPERLINK "url"}...{link text}}}
_HYPERLINKS = re.compile(
    r'(\{\\field\{\s*\\\*\\fldinst\{.*HYPERLINK\s(\".*\")\}{2}\s*\{.*?\s+(.*?)\}{2,3})',
    re.IGNORECASE
)


def _remove_pict_groups(rtf_text: str) -> str:
    """Remove all \\pict groups containing binary data (\\bin<N>...).
    
    Binary picture data can corrupt the parser if interpreted as text.
    If no \\pict...\\bin sequences exist, returns original text unchanged.
    """
    if '\\pict' not in rtf_text or '\\bin' not in rtf_text:
        return rtf_text
    
    result = []
    i = 0
    n = len(rtf_text)
    in_pict = False
    binary_length = 0
    
    while i < n:
        if not in_pict and rtf_text.startswith('\\pict', i):
            in_pict = True
            i += len('\\pict')
            continue
        
        if in_pict:
            if rtf_text.startswith('\\bin', i):
                i += len('\\bin')
                length_str = ''
                while i < n and rtf_text[i].isdigit():
                    length_str += rtf_text[i]
                    i += 1
                binary_length = int(length_str)
                i += binary_length
                continue
            elif rtf_text[i] == '}':
                in_pict = False
                i += 1
                continue
        
        if not in_pict:
            result.append(rtf_text[i])
        
        i += 1
    
    return ''.join(result)


def _rtf_to_text(text: str, encoding: str = 'cp1252', errors: str = 'strict') -> str:
    """Convert RTF markup to plain text.
    
    Args:
        text: RTF source string
        encoding: Default encoding (overridden by \\ansicpg directive)
        errors: How to handle decode errors ('strict' or 'ignore')
    
    Returns:
        Plain text with formatting stripped, Unicode normalized
    """
    # Strip binary picture groups before parsing.
    text = _remove_pict_groups(text)
    
    # Rewrite hyperlinks to text(url) format.
    text = re.sub(_HYPERLINKS, r'\1(\2)', text)
    
    stack = []
    ignorable = False      # Current group is ignorable (e.g., inside \\fonttbl).
    suppress_output = False  # Current group suppresses output (e.g., \\fonttbl, \\colortbl).
    ucskip = 1             # Chars to skip after \\uN (Unicode escape).
    curskip = 0            # Remaining chars to skip.
    hexes = None           # Accumulated hex bytes (\'hh sequences).
    out = ''
    depth = 0
    in_document = False
    
    for match in _PATTERN.finditer(text):
        word, arg, _hex, char, brace, tchar = match.groups()
        
        # Flush accumulated hex bytes if we hit non-hex token.
        if hexes and not _hex:
            out += bytes.fromhex(hexes).decode(encoding=encoding, errors=errors)
            hexes = None
        
        if brace:
            curskip = 0
            if brace == '{':
                depth += 1
                in_document = True
                stack.append((ucskip, ignorable, suppress_output))
            elif brace == '}':
                depth -= 1
                if stack:
                    ucskip, ignorable, suppress_output = stack.pop()
                else:
                    # Malformed RTF: unbalanced braces. Reset to safe defaults.
                    ucskip = 1
                    ignorable = False
                    suppress_output = False
                if in_document and depth <= 0:
                    # Outer document group closed; discard trailing content.
                    break
        
        elif char:  # \X (single non-letter after backslash)
            curskip = 0
            if char in _SPECIALCHARS:
                if not ignorable:
                    out += _SPECIALCHARS[char]
            elif char == '*':
                ignorable = True
        
        elif word:  # \controlword
            curskip = 0
            if word in _DESTINATIONS:
                ignorable = True
            elif word == 'ansicpg':
                # Charset directive overrides default encoding.
                encoding = f'cp{arg}'
            # Handle ignorable/suppress_output check BEFORE special char check
            if ignorable or suppress_output:
                # State-changing commands still need to process even when suppressed
                if word == 'uc':
                    ucskip = int(arg)
                elif word == 'u':
                    if arg is None:
                        curskip = ucskip
                    else:
                        c = int(arg)
                        if c < 0:
                            c += 0x10000
                        curskip = ucskip
            else:
                # Not ignorable/suppressed: emit special chars and handle commands
                if word in _SPECIALCHARS:
                    out += _SPECIALCHARS[word]
                elif word == 'uc':
                    ucskip = int(arg)
                elif word == 'u':
                    if arg is None:
                        curskip = ucskip
                    else:
                        c = int(arg)
                        if c < 0:
                            c += 0x10000
                        out += chr(c)
                        curskip = ucskip
                elif word == 'fonttbl':
                    suppress_output = True
                elif word == 'colortbl':
                    suppress_output = True
        
        elif _hex:  # \'hh hex byte
            if curskip > 0:
                curskip -= 1
            elif not ignorable:
                hexes = _hex if not hexes else hexes + _hex
        
        elif tchar:  # Plain text character
            if curskip > 0:
                curskip -= 1
            elif not ignorable and not suppress_output:
                out += tchar
    
    return out


def extract_text(rtf_path: str | Path) -> str:
    """Extract plain text from an RTF file.
    
    Args:
        rtf_path: Path to .rtf file
    
    Returns:
        Plain text content, stripped of RTF markup and trailing whitespace
    
    Raises:
        FileNotFoundError: If file does not exist
        UnicodeDecodeError: If encoding detection fails (use errors='ignore' in _rtf_to_text if needed)
    """
    rtf_path = Path(rtf_path)
    rtf_bytes = rtf_path.read_bytes()
    
    # RTF is typically ASCII or cp1252; try UTF-8 fallback if needed.
    try:
        rtf_str = rtf_bytes.decode('cp1252')
    except UnicodeDecodeError:
        rtf_str = rtf_bytes.decode('utf-8', errors='replace')
    
    return _rtf_to_text(rtf_str).strip()
