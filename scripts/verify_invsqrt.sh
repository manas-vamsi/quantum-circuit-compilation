#!/bin/bash
# Runs the official invsqrt verifier on a circuit file (inside WSL / Ubuntu).
#   bash scripts/verify_invsqrt.sh path/to/invsqrt.kmb [extra verifier flags]
# The full default check simulates about 200 million shots and takes more than
# 9 minutes on 4 cores, so run it detached if needed:
#   setsid nohup bash scripts/verify_invsqrt.sh file.kmb > ~/gq-compilation/logs/out.log 2>&1 &
set -euo pipefail

CIRCUIT="$(readlink -f "${1:?usage: verify_invsqrt.sh circuit.kmb [flags]}")"
shift || true

ROOT="$HOME/gq-compilation"
mkdir -p "$ROOT/logs"
. "$ROOT/.venv/bin/activate"
cd "$ROOT/data/verifiers"
time python invsqrt/verify_submission_invsqrt.py "$CIRCUIT" "$@"
