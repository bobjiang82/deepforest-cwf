#!/usr/bin/env bash
set -euo pipefail

VENV_DIR="${VENV_DIR:-$HOME/venvs/deepforest-cwf-py39}"

mkdir -p "$(dirname "$VENV_DIR")"
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

python -m pip install -U pip setuptools wheel
python -m pip install \
  numpy==1.23.5 \
  scikit-learn==1.5.2 \
  scipy==1.13.1 \
  deep-forest==0.1.7 \
  openml==0.15.1 \
  pyyaml

echo "Environment ready: $VENV_DIR"
python - <<'PY'
import sys
mods = ['numpy', 'sklearn', 'scipy', 'deepforest', 'openml', 'yaml']
for m in mods:
    mod = __import__(m)
    print(m, getattr(mod, '__version__', 'unknown'))
PY
