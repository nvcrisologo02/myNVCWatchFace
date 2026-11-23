#!/usr/bin/env bash
# Copy the committed Navigator art (art/out/navigator, from scripts/render_3d.sh _ navigator)
# into the navigator module resources, and compose its picker preview.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
SRC=art/out/navigator
RES=navigator/src/main/res/drawable-nodpi
mkdir -p "$RES"
for f in "$SRC"/*.png; do
  b=$(basename "$f")
  cp "$f" "$RES/nav_${b}"   # nav_ prefix: resource names stay distinct from the NVC face
done
python -I art/render_preview.py "$SRC" "$RES/preview.png" >/dev/null
echo "navigator art synced to $RES"
