# A customer help center built from what a customer may see, with an ask box on every page: round 1

Filed by the overseer. The goal's acceptance test (`bash goals/helpcenter/acceptance.sh`) still fails on main
at `9beec351972d`. This proposal is what is missing; the panel lays it out as bounties.
Builders work under `helpcenter/`; the contract itself does not change.

## Still failing (10 of 10)
- check 1: the build runs and writes index.html: AssertionError: python -m helpcenter.build failed: /usr/bin/python3: Error while finding module specification for 'helpcenter.build' (ModuleNotFoundError: No module named 'helpcenter')
- check 2: every visible document has its own page, linked from the index, title as h1, chunks in order: AssertionError: python -m helpcenter.build failed: /usr/bin/python3: Error while finding module specification for 'helpcenter.build' (ModuleNotFoundError: No module named 'helpcenter')
- check 3: it asks only as BRAIN_CUSTOMER, only through core.gate: AssertionError: python -m helpcenter.build failed: /usr/bin/python3: Error while finding module specification for 'helpcenter.build' (ModuleNotFoundError: No module named 'helpcenter')
- check 4: nothing outside the customer's view reaches any output file: AssertionError: python -m helpcenter.build failed: /usr/bin/python3: Error while finding module specification for 'helpcenter.build' (ModuleNotFoundError: No module named 'helpcenter')
- check 5: content is escaped: markup in a chunk shows as text: AssertionError: python -m helpcenter.build failed: /usr/bin/python3: Error while finding module specification for 'helpcenter.build' (ModuleNotFoundError: No module named 'helpcenter')
- check 6: complete documents; every link and asset relative and resolving inside the site: AssertionError: python -m helpcenter.build failed: /usr/bin/python3: Error while finding module specification for 'helpcenter.build' (ModuleNotFoundError: No module named 'helpcenter')
- check 7: self-contained: no external scripts, styles, fonts or images: AssertionError: python -m helpcenter.build failed: /usr/bin/python3: Error while finding module specification for 'helpcenter.build' (ModuleNotFoundError: No module named 'helpcenter')
- check 8: the ask box: on every page, posts the question to /ask with the help center token, answer as text: AssertionError: python -m helpcenter.build failed: /usr/bin/python3: Error while finding module specification for 'helpcenter.build' (ModuleNotFoundError: No module named 'helpcenter')
- check 9: the build is deterministic: AssertionError: python -m helpcenter.build failed: /usr/bin/python3: Error while finding module specification for 'helpcenter.build' (ModuleNotFoundError: No module named 'helpcenter')
- check 10: helpcenter/ modules: standard library (plus core, helpcenter) only, no network: AssertionError: there is no helpcenter/ package

## Already passing
- none

## Earlier attempts that gave up
- none

## Files in scope today
```
(nothing yet)
```

## Acceptance output (tail)
```
FAIL 1 the build runs and writes index.html: AssertionError: python -m helpcenter.build failed: /usr/bin/python3: Error while finding module specification for 'helpcenter.build' (ModuleNotFoundError: No module named 'helpcenter')

FAIL 2 every visible document has its own page, linked from the index, title as h1, chunks in order: AssertionError: python -m helpcenter.build failed: /usr/bin/python3: Error while finding module specification for 'helpcenter.build' (ModuleNotFoundError: No module named 'helpcenter')

FAIL 3 it asks only as BRAIN_CUSTOMER, only through core.gate: AssertionError: python -m helpcenter.build failed: /usr/bin/python3: Error while finding module specification for 'helpcenter.build' (ModuleNotFoundError: No module named 'helpcenter')

FAIL 4 nothing outside the customer's view reaches any output file: AssertionError: python -m helpcenter.build failed: /usr/bin/python3: Error while finding module specification for 'helpcenter.build' (ModuleNotFoundError: No module named 'helpcenter')

FAIL 5 content is escaped: markup in a chunk shows as text: AssertionError: python -m helpcenter.build failed: /usr/bin/python3: Error while finding module specification for 'helpcenter.build' (ModuleNotFoundError: No module named 'helpcenter')

FAIL 6 complete documents; every link and asset relative and resolving inside the site: AssertionError: python -m helpcenter.build failed: /usr/bin/python3: Error while finding module specification for 'helpcenter.build' (ModuleNotFoundError: No module named 'helpcenter')

FAIL 7 self-contained: no external scripts, styles, fonts or images: AssertionError: python -m helpcenter.build failed: /usr/bin/python3: Error while finding module specification for 'helpcenter.build' (ModuleNotFoundError: No module named 'helpcenter')

FAIL 8 the ask box: on every page, posts the question to /ask with the help center token, answer as text: AssertionError: python -m helpcenter.build failed: /usr/bin/python3: Error while finding module specification for 'helpcenter.build' (ModuleNotFoundError: No module named 'helpcenter')

FAIL 9 the build is deterministic: AssertionError: python -m helpcenter.build failed: /usr/bin/python3: Error while finding module specification for 'helpcenter.build' (ModuleNotFoundError: No module named 'helpcenter')

FAIL 10 helpcenter/ modules: standard library (plus core, helpcenter) only, no network: AssertionError: there is no helpcenter/ package
SUMMARY passed=0 failed=10

```

Each bounty's acceptance command should be `bash goals/helpcenter/acceptance.sh --only <n>` for the checks it covers, joined with
`&&`. Prefer pieces small enough that one failing check is one bounty. Do not repeat a piece that already merged.
