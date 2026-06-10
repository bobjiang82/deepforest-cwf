#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${VENV_DIR:-$HOME/venvs/deepforest-cwf-py39}"
CONFIG_PATH="${CONFIG_PATH:-$ROOT_DIR/configs/benchmark-default.yaml}"
TAG="${TAG:-default}"
OUT_DIR="${OUT_DIR:-$ROOT_DIR/results/$TAG}"
N_JOBS="${DF_N_JOBS:-}"
REPEATS="${REPEATS:-}"
WARMUP_RUNS="${WARMUP_RUNS:-}"
BACKEND="${BACKEND:-}"

source "$VENV_DIR/bin/activate"
mkdir -p "$OUT_DIR"

bash "$ROOT_DIR/scripts/collect_system_info.sh" "$OUT_DIR/system_info.txt"

CMD=(
  python "$ROOT_DIR/benchmark/deepforest/repeat_runner.py"
  --config "$CONFIG_PATH"
  --python "$(command -v python)"
  --script "$ROOT_DIR/benchmark/deepforest/benchmark_df_openml.py"
  --out-dir "$OUT_DIR"
  --tag "$TAG"
)

if [ -n "$N_JOBS" ]; then
  CMD+=(--n-jobs "$N_JOBS")
fi
if [ -n "$REPEATS" ]; then
  CMD+=(--repeats "$REPEATS")
fi
if [ -n "$WARMUP_RUNS" ]; then
  CMD+=(--warmup-runs "$WARMUP_RUNS")
fi
if [ -n "$BACKEND" ]; then
  CMD+=(--backend "$BACKEND")
fi

"${CMD[@]}"
