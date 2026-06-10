#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVERINFO_DIR="${SERVERINFO_DIR:-/mnt/nvme1p5t/serverinfo}"
TOOLS_DIR="${TOOLS_DIR:-$ROOT_DIR/tools}"
OUT_PATH=""

if [ "${1:-}" = "--out" ]; then
  OUT_PATH="${2:?missing path for --out}"
  shift 2
fi

bash "$ROOT_DIR/scripts/prepare_serverinfo_tools.sh"
MLC_BIN="$TOOLS_DIR/mlc/Linux/mlc"

if [ ! -x "$MLC_BIN" ]; then
  echo "Intel MLC binary not found after preparation: $MLC_BIN" >&2
  exit 1
fi

if [ -n "$OUT_PATH" ]; then
  mkdir -p "$(dirname "$OUT_PATH")"
  "$MLC_BIN" "$@" | tee "$OUT_PATH"
else
  exec "$MLC_BIN" "$@"
fi
