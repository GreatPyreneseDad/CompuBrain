# The brain reads spreadsheets, slide decks, web pages, CSV and email: round 1

Filed by the overseer. The goal's acceptance test (`bash goals/readers/acceptance.sh`) still fails on main
at `7d263c4c56d5`. This proposal is what is missing; the panel lays it out as bounties.
Builders work under `ingest/`; the contract itself does not change.

## Still failing (8 of 9)
- check 2: .xlsx: cells as text, sheet names as headings: UnsupportedFormat: pipeline.xlsx: no reader for .xlsx
- check 3: .pptx: slide text in presentation order: UnsupportedFormat: kickoff.pptx: no reader for .pptx
- check 4: .html: text and headings, entities decoded, script and style dropped: UnsupportedFormat: handbook.html: no reader for .html
- check 5: .csv: rows as text, quoted commas kept whole: UnsupportedFormat: accounts.csv: no reader for .csv
- check 6: .eml: subject, sender and plain body; no MIME debris: UnsupportedFormat: mail.eml: no reader for .eml
- check 7: every new type: registered, Doc shape, refuses without source and scope: AssertionError: .xlsx not in READERS
- check 8: upper-case extensions route to their reader: UnsupportedFormat: UPPER.XLSX: no reader for .XLSX
- check 9: reader modules: standard library only, no environment or network: AssertionError: loading the samples failed: t68/host/ingest/chunk.py", line 49, in load

## Already passing
- check 1: the existing ingest tests still pass

## Earlier attempts that gave up
- none

## Files in scope today
```
ingest/LICENSE-python-docx2txt
ingest/LICENSE-striprtf
ingest/__init__.py
ingest/chunk.py
ingest/docx.py
ingest/embed.py
ingest/llm.py
ingest/make_corpus.py
ingest/rtf.py
ingest/run.py
ingest/run_sf.py
ingest/summarize.py
ingest/tag.py
ingest/test_chunk_docx.py
ingest/test_docx.py
ingest/test_rtf.py
```

## Acceptance output (tail)
```
PASS 1 the existing ingest tests still pass
FAIL 2 .xlsx: cells as text, sheet names as headings: UnsupportedFormat: pipeline.xlsx: no reader for .xlsx
FAIL 3 .pptx: slide text in presentation order: UnsupportedFormat: kickoff.pptx: no reader for .pptx
FAIL 4 .html: text and headings, entities decoded, script and style dropped: UnsupportedFormat: handbook.html: no reader for .html
FAIL 5 .csv: rows as text, quoted commas kept whole: UnsupportedFormat: accounts.csv: no reader for .csv
FAIL 6 .eml: subject, sender and plain body; no MIME debris: UnsupportedFormat: mail.eml: no reader for .eml
FAIL 7 every new type: registered, Doc shape, refuses without source and scope: AssertionError: .xlsx not in READERS
FAIL 8 upper-case extensions route to their reader: UnsupportedFormat: UPPER.XLSX: no reader for .XLSX
FAIL 9 reader modules: standard library only, no environment or network: AssertionError: loading the samples failed: t68/host/ingest/chunk.py", line 49, in load
    raise UnsupportedFormat(f"{path.name}: no reader for {path.suffix or 'this file type'}")
ingest.chunk.UnsupportedFormat: mod
SUMMARY passed=1 failed=8

```

Each bounty's acceptance command should be `bash goals/readers/acceptance.sh --only <n>` for the checks it covers, joined with
`&&`. Prefer pieces small enough that one failing check is one bounty. Do not repeat a piece that already merged.
