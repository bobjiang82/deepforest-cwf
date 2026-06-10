#!/usr/bin/env bash
set -euo pipefail

MLC_BIN="${MLC_BIN:-mlc}"

if ! command -v "$MLC_BIN" >/dev/null 2>&1; then
  echo "Intel MLC binary not found. Set MLC_BIN or add mlc to PATH." >&2
  exit 1
fi

exec "$MLC_BIN" "$@"
