#!/usr/bin/env bash
set -euo pipefail

OUT_PATH="${1:-}"

collect() {
  echo "timestamp=$(date --iso-8601=seconds)"
  echo "hostname=$(hostname)"
  echo "kernel=$(uname -srmo)"
  echo "nproc=$(nproc)"
  echo
  echo "[lscpu]"
  lscpu
  echo
  echo "[numactl]"
  numactl --hardware 2>/dev/null || true
  echo
  echo "[free]"
  free -h
  echo
  echo "[lsmem]"
  lsmem 2>/dev/null || true
}

if [ -n "$OUT_PATH" ]; then
  mkdir -p "$(dirname "$OUT_PATH")"
  collect | tee "$OUT_PATH"
else
  collect
fi
