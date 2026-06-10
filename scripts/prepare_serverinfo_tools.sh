#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVERINFO_DIR="${SERVERINFO_DIR:-/mnt/nvme1p5t/serverinfo}"
TOOLS_DIR="${TOOLS_DIR:-$ROOT_DIR/tools}"

mkdir -p "$TOOLS_DIR"

if [ ! -d "$TOOLS_DIR/mlc" ]; then
  mkdir -p "$TOOLS_DIR/mlc"
  tar -xzf "$SERVERINFO_DIR/mlc_v3.12.tgz" -C "$TOOLS_DIR/mlc"
fi

if [ ! -d "$TOOLS_DIR/perfspect" ]; then
  tar -xzf "$SERVERINFO_DIR/perfspect.tgz" -C "$TOOLS_DIR"
fi

if [ ! -d "$TOOLS_DIR/STREAM_IC2022v0" ]; then
  unzip -q -o "$SERVERINFO_DIR/STREAM_IC2022v04_SRF.zip" -d "$TOOLS_DIR"
fi

chmod +x "$TOOLS_DIR/mlc/Linux/mlc" || true
chmod +x "$TOOLS_DIR/perfspect/perfspect" || true
chmod +x "$TOOLS_DIR/STREAM_IC2022v0"/*.sh "$TOOLS_DIR/STREAM_IC2022v0"/*.exe || true

echo "Tools prepared under $TOOLS_DIR"
