#!/usr/bin/env bash
# vendored from buildup runner/rerun.sh @ f41de85 — keep in sync.
# buildup evidence runner — forge-blind.
# usage: rerun.sh <finding.json> [checkout_dir]
#   Reads a finding.v0 file, clones (or reuses) its repo, pins the commit, runs the repro.
#   Prints one JSON line to stdout and exits 0 either way; RESULT is in the JSON.
#   red   = repro reproduces  = finding STANDS
#   green = repro did not     = finding FAILS
# Any CI (GitHub Actions, GitLab CI, a cron on a bare server, a laptop) wraps this. Nothing in here knows a forge.
set -euo pipefail

F_PATH="${1:?finding.json}"; DIR="${2:-}"
F=$(cat "$F_PATH")
REPO=$(jq -r .location.repo <<<"$F")
COMMIT=$(jq -r .location.commit <<<"$F")
WD=$(jq -r '.evidence.repro.workdir // "."' <<<"$F")
SETUP=$(jq -r '.evidence.repro.setup // empty' <<<"$F")
CMD=$(jq -r .evidence.repro.cmd <<<"$F")
EXP=$(jq -r .evidence.repro.expect <<<"$F")
NEEDLE=$(jq -r '.evidence.repro.needle // empty' <<<"$F")
T=$(jq -r '.evidence.repro.timeout_s // 120' <<<"$F")
FSHA=$(jq -c 'del(.contribution_token)' <<<"$F" | python3 -c 'import sys,json,hashlib; o=json.load(sys.stdin)
def c(v): return [c(x) for x in v] if isinstance(v,list) else {k:c(v[k]) for k in sorted(v)} if isinstance(v,dict) else v
print(hashlib.sha256(json.dumps(c(o),separators=(",",":")).encode()).hexdigest())')

if [ -z "$DIR" ]; then DIR=$(mktemp -d); git clone -q "$REPO" "$DIR"; fi
git -C "$DIR" fetch -q origin "$COMMIT" 2>/dev/null || true
git -C "$DIR" checkout -q "$COMMIT"

cd "$DIR/$WD"
[ -n "$SETUP" ] && bash -c "$SETUP" >/dev/null 2>&1 || true
set +e
OUT=$(timeout "$T" bash -c "$CMD" 2>/tmp/rerun.err); RC=$?
set -e
ERR=$(cat /tmp/rerun.err)

case "$EXP" in
  nonzero_exit)    REPRODUCED=$([ $RC -ne 0 ] && echo true || echo false) ;;
  stdout_contains) REPRODUCED=$(grep -q -- "$NEEDLE" <<<"$OUT" && echo true || echo false) ;;
  stderr_contains) REPRODUCED=$(grep -q -- "$NEEDLE" <<<"$ERR" && echo true || echo false) ;;
  *) REPRODUCED=false ;;
esac
RESULT=$([ "$REPRODUCED" = true ] && echo red || echo green)

jq -c -n --arg r "$RESULT" --arg repo "$REPO" --arg commit "$COMMIT" --arg fsha "$FSHA" \
  --argjson rc "$RC" --arg out "$(tail -c 2000 <<<"$OUT")" --arg err "$(tail -c 2000 <<<"$ERR")" \
  '{result:$r, repo:$repo, commit:$commit, finding_sha256:$fsha, exit:$rc, stdout_tail:$out, stderr_tail:$err}'
