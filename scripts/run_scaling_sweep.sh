#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${VENV_DIR:-$HOME/venvs/deepforest-cwf-py39}"
CONFIG_PATH="${CONFIG_PATH:-$ROOT_DIR/configs/benchmark-default.yaml}"
SWEEP_NAME="${SWEEP_NAME:-core_scaling}"
OUT_ROOT="${OUT_ROOT:-$ROOT_DIR/results/$SWEEP_NAME}"
CORE_LIST="${CORE_LIST:-1,12,24,48,96,144,192,240,288}"
REPEATS="${REPEATS:-3}"
WARMUP_RUNS="${WARMUP_RUNS:-1}"
BACKEND="${BACKEND:-}"
BASE_TAG="${BASE_TAG:-$SWEEP_NAME}"
BASELINE_N_JOBS="${BASELINE_N_JOBS:-}"

source "$VENV_DIR/bin/activate"
mkdir -p "$OUT_ROOT"

IFS=',' read -r -a CORES <<< "$CORE_LIST"
for raw_core in "${CORES[@]}"; do
  core="$(echo "$raw_core" | xargs)"
  if [[ ! "$core" =~ ^[0-9]+$ ]]; then
    echo "Invalid core count: $raw_core" >&2
    exit 1
  fi
  tag="${BASE_TAG}_n${core}"
  out_dir="$OUT_ROOT/n_jobs_${core}"
  echo "=== Running n_jobs=${core} -> ${out_dir} ==="
  TAG="$tag" \
  OUT_DIR="$out_dir" \
  DF_N_JOBS="$core" \
  REPEATS="$REPEATS" \
  WARMUP_RUNS="$WARMUP_RUNS" \
  BACKEND="$BACKEND" \
  CONFIG_PATH="$CONFIG_PATH" \
  bash "$ROOT_DIR/scripts/run_benchmark.sh"
done

ANALYZE_CMD=(
  python "$ROOT_DIR/benchmark/deepforest/analyze_scaling.py"
  --input-dir "$OUT_ROOT"
  --json-out "$OUT_ROOT/scaling_analysis.json"
  --table-out "$OUT_ROOT/scaling_analysis.txt"
)

if [ -n "$BASELINE_N_JOBS" ]; then
  ANALYZE_CMD+=(--baseline-n-jobs "$BASELINE_N_JOBS")
fi

"${ANALYZE_CMD[@]}"

echo "Scaling sweep complete: $OUT_ROOT"
