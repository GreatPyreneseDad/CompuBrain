"""The readers contract: the brain reads spreadsheets, slide decks, web pages, CSV and email.

Each check builds its own sample file in a temp dir (no sample files in the repo, per .cerata/guide.md), loads it
through ingest.chunk.load() exactly as intake does, and checks what comes out. Builders work under ingest/ only and
must not change goals/. Run one check with:  python3 goals/readers/referee.py --only <n>

  1  the existing ingest tests still pass
  2  .xlsx  every sheet's cells as text, sheet names as section headings, shared and inline strings, numbers
  3  .pptx  every slide's text, in presentation order (sldIdLst), not file-name order
  4  .html  headings and paragraphs as text, entities decoded, script and style dropped
  5  .csv   rows as text, a quoted field with a comma kept whole
  6  .eml   subject, sender and the plain body; HTML-only parts converted; no MIME boundaries or base64 left in
  7  every new type: in READERS, returns a Doc with chunks, pretagged False, and refuses to load without
         source and default_scope (ValueError), like .docx and .rtf
  8  upper-case extensions route to their reader (.XLSX, and the existing .DOCX path)
  9  the reader modules load() imports for these types use the standard library only and touch no environment
         variables or network (the guide's rule)
"""
import ast, email.message, io, os, subprocess, sys, tempfile, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
W = Path(tempfile.mkdtemp(prefix="readers-"))
RESULTS = []


def check(n, title):
    def deco(fn):
        RESULTS.append((n, title, fn)); return fn
    return deco


def load(path, **kw):
    from ingest import chunk
    return chunk.load(path, source=kw.get("source", "test"), default_scope=kw.get("default_scope", "internal"))


def text_of(doc):
    return "\n".join(c.content for c in doc.chunks)


# ---------------------------------------------------------------- samples --

def make_xlsx(name="pipeline.xlsx"):
    p = W / name
    with zipfile.ZipFile(p, "w") as z:
        z.writestr("[Content_Types].xml", '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                   '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/></Types>')
        z.writestr("xl/workbook.xml", '<?xml version="1.0"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
                   'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>'
                   '<sheet name="Pipeline" sheetId="1" r:id="rId1"/><sheet name="Renewals" sheetId="2" r:id="rId2"/></sheets></workbook>')
        z.writestr("xl/_rels/workbook.xml.rels", '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
                   '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet2.xml"/></Relationships>')
        z.writestr("xl/sharedStrings.xml", '<?xml version="1.0"?><sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                   '<si><t>Account</t></si><si><t>Value</t></si><si><t>Halcyon Freight</t></si><si><r><t>Tallgrass </t></r><r><t>Logistics</t></r></si></sst>')
        z.writestr("xl/worksheets/sheet1.xml", '<?xml version="1.0"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>'
                   '<row r="1"><c r="A1" t="s"><v>0</v></c><c r="B1" t="s"><v>1</v></c></row>'
                   '<row r="2"><c r="A2" t="s"><v>2</v></c><c r="B2"><v>42000</v></c></row>'
                   '<row r="3"><c r="A3" t="s"><v>3</v></c><c r="B3"><v>17500.5</v></c></row></sheetData></worksheet>')
        z.writestr("xl/worksheets/sheet2.xml", '<?xml version="1.0"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>'
                   '<row r="1"><c r="A1" t="inlineStr"><is><t>Ridgeback Cold Chain renews in March</t></is></c></row></sheetData></worksheet>')
    return p


def make_pptx(name="kickoff.pptx"):
    p = W / name
    ns = 'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"'
    slide = lambda title, body: (f'<?xml version="1.0"?><p:sld {ns}><p:cSld><p:spTree>'
                                 f'<p:sp><p:txBody><a:p><a:r><a:t>{title}</a:t></a:r></a:p></p:txBody></p:sp>'
                                 f'<p:sp><p:txBody><a:p><a:r><a:t>{body}</a:t></a:r></a:p></p:txBody></p:sp>'
                                 f'</p:spTree></p:cSld></p:sld>')
    with zipfile.ZipFile(p, "w") as z:
        z.writestr("[Content_Types].xml", '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>')
        # presentation order is slide2.xml, then slide1.xml: a reader that sorts by file name gets it backwards
        z.writestr("ppt/presentation.xml", '<?xml version="1.0"?><p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
                   'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><p:sldIdLst>'
                   '<p:sldId id="256" r:id="rIdB"/><p:sldId id="257" r:id="rIdA"/></p:sldIdLst></p:presentation>')
        z.writestr("ppt/_rels/presentation.xml.rels", '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   '<Relationship Id="rIdA" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide1.xml"/>'
                   '<Relationship Id="rIdB" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide2.xml"/></Relationships>')
        z.writestr("ppt/slides/slide1.xml", slide("Next steps", "Ship the Halcyon amendment by Friday"))
        z.writestr("ppt/slides/slide2.xml", slide("Q4 kickoff", "Three accounts carry the quarter"))
    return p


def make_html(name="handbook.html"):
    p = W / name
    p.write_text("<!doctype html><html><head><title>Support handbook</title><style>.x{color:red}</style>"
                 "<script>var secret='do-not-index';</script></head><body><h1>Support handbook</h1>"
                 "<p>Escalate within 4 hours &amp; log every call.</p><h2>Refunds</h2><p>Refunds over $500 need a manager.</p>"
                 "</body></html>", encoding="utf-8")
    return p


def make_csv(name="accounts.csv"):
    p = W / name
    p.write_text('account,region,owner\n"Kestrel, Ridge Co",West,Dana\nHalcyon Freight,East,Lee\n', encoding="utf-8")
    return p


def make_eml(name="mail.eml", html_only=False):
    p = W / name
    m = email.message.EmailMessage()
    m["Subject"] = "Signed amendment for Halcyon"
    m["From"] = "Lee Park <lee@halcyon.example>"
    m["To"] = "brain@company.example"
    if html_only:
        m.set_content("<p>The <b>signed amendment</b> is attached.</p>", subtype="html")
    else:
        m.set_content("The signed amendment is attached. Countersign by Friday.")
        m.add_alternative("<p>The signed amendment is attached. Countersign by Friday.</p>", subtype="html")
        m.add_attachment(b"%PDF-1.4 binary-ish" * 40, maintype="application", subtype="pdf", filename="amendment.pdf")
    p.write_bytes(bytes(m))
    return p


# ----------------------------------------------------------------- checks --

@check(1, "the existing ingest tests still pass")
def c1():
    r = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "ingest", "-t", "."], cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, (r.stdout + r.stderr)[-300:]


@check(2, ".xlsx: cells as text, sheet names as headings")
def c2():
    t = text_of(load(make_xlsx()))
    for s in ("Halcyon Freight", "42000", "Tallgrass Logistics", "17500.5", "Ridgeback Cold Chain renews in March"):
        assert s in t, f"missing {s!r}"
    # a chunk carries its heading trail as "[trail]" on its first line: each sheet must be its own section
    trails = [c.content.splitlines()[0] for c in load(make_xlsx("pipeline2.xlsx")).chunks if c.content.startswith("[")]
    assert any("Pipeline" in h for h in trails) and any("Renewals" in h for h in trails), f"sheets are not sections: {trails}"


@check(3, ".pptx: slide text in presentation order")
def c3():
    t = text_of(load(make_pptx()))
    for s in ("Q4 kickoff", "Three accounts carry the quarter", "Next steps", "Ship the Halcyon amendment by Friday"):
        assert s in t, f"missing {s!r}"
    assert t.index("Q4 kickoff") < t.index("Next steps"), "slides are out of presentation order (sorted by file name?)"


@check(4, ".html: text and headings, entities decoded, script and style dropped")
def c4():
    t = text_of(load(make_html()))
    assert "Escalate within 4 hours & log every call." in t, "paragraph or entity wrong"
    assert "Refunds over $500 need a manager." in t
    assert "do-not-index" not in t and "color:red" not in t, "script or style leaked into the text"
    assert "<p>" not in t and "<h2>" not in t, "tags left in the text"


@check(5, ".csv: rows as text, quoted commas kept whole")
def c5():
    t = text_of(load(make_csv()))
    assert "Kestrel, Ridge Co" in t, "a quoted field with a comma was split"
    assert "Halcyon Freight" in t and "Dana" in t and "region" in t


@check(6, ".eml: subject, sender and plain body; no MIME debris")
def c6():
    t = text_of(load(make_eml()))
    assert "Signed amendment for Halcyon" in t and "lee@halcyon.example" in t, "subject or sender missing"
    assert "Countersign by Friday." in t, "plain body missing"
    assert "Content-Type" not in t and "base64" not in t.lower() and "%PDF" not in t, "MIME headers or attachment bytes leaked"
    t2 = text_of(load(make_eml("html-only.eml", html_only=True)))
    assert "signed amendment" in t2 and "<b>" not in t2, "an HTML-only email was not converted to text"


@check(7, "every new type: registered, Doc shape, refuses without source and scope")
def c7():
    from ingest import chunk
    makers = {".xlsx": make_xlsx, ".pptx": make_pptx, ".html": make_html, ".csv": make_csv, ".eml": make_eml}
    for ext, mk in makers.items():
        assert ext in chunk.READERS, f"{ext} not in READERS"
        d = load(mk(f"shape{ext}"))
        assert isinstance(d, chunk.Doc) and d.chunks and d.pretagged is False, f"{ext}: wrong Doc shape"
        assert d.default_scope == "internal" and d.source == "test", f"{ext}: source or scope not carried"
        try:
            chunk.load(mk(f"noscope{ext}"), source=None, default_scope=None)
        except ValueError:
            pass
        else:
            raise AssertionError(f"{ext}: loaded without source and default_scope")


@check(8, "upper-case extensions route to their reader")
def c8():
    p = make_xlsx("UPPER.XLSX")
    t = text_of(load(p))
    assert "Halcyon Freight" in t, ".XLSX was not read as a spreadsheet"
    # a minimal .docx, named in upper case: today this passes the READERS gate and is then read as UTF-8 bytes
    q = W / "MEMO.DOCX"
    with zipfile.ZipFile(q, "w") as z:
        z.writestr("[Content_Types].xml", '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>')
        z.writestr("word/document.xml", '<?xml version="1.0"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                   '<w:body><w:p><w:r><w:t>Upper case memo body text.</w:t></w:r></w:p></w:body></w:document>')
    t = text_of(load(q))
    assert "Upper case memo body text." in t and "word/document.xml" not in t and "PK" not in t[:4], ".DOCX was read as raw bytes"


@check(9, "reader modules: standard library only, no environment or network")
def c9():
    # a fresh interpreter, so modules earlier checks imported still count: which ingest.* modules does loading
    # these five types pull in, beyond what importing ingest.chunk already does?
    samples = [str(mk(f"mods{ext}")) for ext, mk in ((".xlsx", make_xlsx), (".pptx", make_pptx), (".html", make_html), (".csv", make_csv), (".eml", make_eml))]
    probe = ("import sys, json; sys.path.insert(0, %r); from ingest import chunk; before = set(sys.modules)\n"
             "for p in json.loads(sys.argv[1]): chunk.load(p, source='t', default_scope='internal')\n"
             "print(json.dumps(sorted(sys.modules[m].__file__ for m in set(sys.modules) - before if m.startswith('ingest.'))))") % str(ROOT)
    r = subprocess.run([sys.executable, "-c", probe, __import__("json").dumps(samples)], capture_output=True, text=True, cwd=ROOT)
    assert r.returncode == 0, f"loading the samples failed: {r.stderr[-200:]}"
    files = __import__("json").loads(r.stdout.strip().splitlines()[-1])
    assert files, "loading the new types imported no reader module from ingest/"
    new = files
    std = set(sys.stdlib_module_names) | {"__future__", "ingest"}
    for mod in new:
        f = Path(mod)
        tree = ast.parse(f.read_text())
        for node in ast.walk(tree):
            names = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module or ""] if isinstance(node, ast.ImportFrom) and node.level == 0 else []
            for n in names:
                assert n.split(".")[0] in std, f"{f.name} imports {n}, not the standard library"
        net = {"socket", "ssl", "urllib", "http", "ftplib", "smtplib", "poplib", "imaplib", "asyncio", "subprocess"}
        for node in ast.walk(tree):
            names = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module or ""] if isinstance(node, ast.ImportFrom) and node.level == 0 else []
            for n in names:
                assert n.split(".")[0] not in net, f"{f.name} imports {n}: a reader makes no network calls or subprocesses"
        src = f.read_text()
        for bad in ("os.environ", "getenv("):
            assert bad not in src, f"{f.name} reads the environment ({bad})"


def main():
    only = int(sys.argv[sys.argv.index("--only") + 1]) if "--only" in sys.argv else None
    p = f = 0
    for n, title, fn in RESULTS:
        if only and n != only:
            continue
        try:
            fn(); p += 1; print(f"PASS {n} {title}")
        except Exception as e:
            f += 1; print(f"FAIL {n} {title}: {type(e).__name__}: {str(e)[:200]}")
    print(f"SUMMARY passed={p} failed={f}")
    return 0 if f == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
