#!/usr/bin/env bash
# Copy the committed 3D art of a second/third face (art/out/<face>, from scripts/render_3d.sh)
# into its module resources with a per-face prefix, and compose its picker preview.
# Usage: scripts/sync_face.sh navigator|nocturne|orbita
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
FACE="${1:?navigator|nocturne|orbita}"
case "$FACE" in
  navigator) PREFIX=nav_ ;;
  nocturne) PREFIX=noc_ ;;
  orbita) PREFIX=orb_ ;;
  *) echo "cara desconocida: $FACE" >&2; exit 2 ;;
esac
SRC="art/out/$FACE"
RES="$FACE/src/main/res/drawable-nodpi"
mkdir -p "$RES"
rm -f "$RES/${PREFIX}"*.png
for f in "$SRC"/*.png; do
  cp "$f" "$RES/${PREFIX}$(basename "$f")"   # prefix keeps resource names distinct between faces
done
python -I art/render_preview.py "$SRC" "$RES/preview.png" >/dev/null
echo "$FACE art synced to $RES"
