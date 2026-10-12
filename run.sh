#!/bin/sh
# Start the brain on this machine:  ./run.sh   then open http://localhost:8000
# Needs brain.env (or .env) and brain_svc_key.p8 in this folder.
set -e
cd "$(dirname "$0")"
[ -d .venv ] || python3 -m venv .venv
. .venv/bin/activate
pip install -q -r requirements.txt
set -a; [ -f brain.env ] && . ./brain.env; [ -f .env ] && . ./.env; set +a
case "${1:-serve}" in
  serve)  exec python -W ignore -m uvicorn api.main:app --port 8000 ;;
  demo)   exec python -W ignore -m core.demo ;;
  gate)   exec python -W ignore -m sf.test_gate ;;
  ingest) shift; exec python -W ignore -m ingest.run_sf "$@" ;;
  *) echo "usage: ./run.sh [serve|demo|gate|ingest <path> --source NAME --default-scope SCOPE]"; exit 1 ;;
esac
