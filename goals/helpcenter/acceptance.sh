#!/usr/bin/env bash
# The help center contract. Referee: goals/helpcenter/referee.py (ten checks; see its docstring). Builders work under
# helpcenter/ only and must not change goals/.   usage: bash goals/helpcenter/acceptance.sh [--only <n>]
cd "$(dirname "$0")/../.." && exec python3 goals/helpcenter/referee.py "$@"
