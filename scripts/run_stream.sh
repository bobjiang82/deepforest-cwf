#!/usr/bin/env bash
set -euo pipefail

if command -v stream_c.exe >/dev/null 2>&1; then
  exec stream_c.exe "$@"
elif command -v stream >/dev/null 2>&1; then
  exec stream "$@"
else
  echo "STREAM binary not found. Install/build STREAM and ensure stream or stream_c.exe is on PATH." >&2
  exit 1
fi
