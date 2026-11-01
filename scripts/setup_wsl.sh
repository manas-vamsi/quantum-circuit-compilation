#!/bin/bash
# Creates the Python environment used for the competition (run inside WSL / Ubuntu).
# Needs python3-venv once, as root:
#   wsl -d Ubuntu -u root -- apt-get install -y python3.12-venv python3-pip
set -euo pipefail

ROOT="$HOME/gq-compilation"
mkdir -p "$ROOT"
cd "$ROOT"

python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip -q
pip install qualtran                 # tested with 0.7.0
pip install kickmix==1.0.0           # prebuilt wheel; metadata points to the Qualtran project

python - <<'PY'
import kickmix, qualtran
print("kickmix OK:", kickmix.__file__)
print("qualtran OK")
PY
echo "Next: unpack the Kaggle data to $ROOT/data (see README)."
