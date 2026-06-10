#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${VENV_DIR:-$HOME/venvs/deepforest-cwf-py39}"
N_JOBS="${DF_N_JOBS:-$(nproc)}"
REPEATS="${REPEATS:-5}"
WARMUP_RUNS="${WARMUP_RUNS:-1}"
TAG="${TAG:-default}"
OUT_DIR="${OUT_DIR:-$ROOT_DIR/results/$TAG}"

source "$VENV_DIR/bin/activate"
mkdir -p "$OUT_DIR"

bash "$ROOT_DIR/scripts/collect_system_info.sh" "$OUT_DIR/system_info.txt"

python "$ROOT_DIR/benchmark/deepforest/repeat_runner.py" \
  --python "$(command -v python)" \
  --script "$ROOT_DIR/benchmark/deepforest/benchmark_df_openml.py" \
  --repeats "$REPEATS" \
  --warmup-runs "$WARMUP_RUNS" \
  --n-jobs "$N_JOBS" \
  --cache-dir "$ROOT_DIR/data/openml_cache" \
  --out-dir "$OUT_DIR" \
  --tag "$TAG"
