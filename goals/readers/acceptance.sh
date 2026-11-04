#!/usr/bin/env bash
# The readers contract. Referee: goals/readers/referee.py (nine checks; see its docstring). Builders work under
# ingest/ only and must not change goals/.   usage: bash goals/readers/acceptance.sh [--only <n>]
cd "$(dirname "$0")/../.." && exec python3 goals/readers/referee.py "$@"
