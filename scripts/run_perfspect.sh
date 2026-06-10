#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TOOLS_DIR="${TOOLS_DIR:-$ROOT_DIR/tools}"
OUT_PATH=""

if [ "${1:-}" = "--out" ]; then
  OUT_PATH="${2:?missing path for --out}"
  shift 2
fi

bash "$ROOT_DIR/scripts/prepare_serverinfo_tools.sh"
PERFSPECT_BIN="$TOOLS_DIR/perfspect/perfspect"

if [ ! -x "$PERFSPECT_BIN" ]; then
  echo "PerfSpect binary not found after preparation: $PERFSPECT_BIN" >&2
  exit 1
fi

shift || true
CMD=("$PERFSPECT_BIN" report "$@")

if [ -n "$OUT_PATH" ]; then
  mkdir -p "$(dirname "$OUT_PATH")"
  "${CMD[@]}" | tee "$OUT_PATH"
else
  exec "${CMD[@]}"
fi
