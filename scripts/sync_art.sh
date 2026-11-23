#!/usr/bin/env bash
# Regenerate all generated art and copy it into the watch face resources.
# Fails if a committed file in art/out changes: the generators are deterministic, so a change
# means the scripts changed and the new output must be reviewed and committed on purpose.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
OUT=art/out
RES=watchface/src/main/res/drawable-nodpi

python -I art/render_bg.py art/data/ne_50m_land.geojson art/src/logo-nvc.jpg "$OUT" bajo >/dev/null
python -I art/render_hands.py "$OUT" >/dev/null
python -I art/render_ambient.py "$OUT/logo.png" "$OUT" >/dev/null

if [[ "${ALLOW_ART_CHANGES:-0}" != 1 ]] && ! git diff --quiet -- "$OUT"; then
  echo "art/out changed after regenerating; review it and commit, or rerun with ALLOW_ART_CHANGES=1" >&2
  git diff --stat -- "$OUT" >&2
  exit 1
fi

mkdir -p "$RES"
cp "$OUT"/bg_bajo.png "$OUT"/logo.png "$OUT"/ambient_dial.png "$OUT"/hand_*.png "$RES"/
python -I art/render_preview.py "$OUT" "$RES/preview.png" >/dev/null
echo "art synced to $RES"
