#!/usr/bin/env bash
# Render the 3D art of a watch face with Blender.
#   scripts/render_3d.sh [samples] [nvc|navigator]
# nvc (default):  art/out/bg_3d.png, art/out/hand3d_*.png      -> scripts/sync_art.sh
# navigator:      art/out/navigator/{bg_3d,ambient_dial,hand3d_*}.png -> scripts/sync_navigator.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
BLENDER="${BLENDER:-/c/Users/criso/Apps/blender-5.3.0-windows-x64/blender.exe}"
SAMPLES="${1:-256}"
FACE="${2:-nvc}"
BUILD=art/blender/build

python -I art/blender/make_prints.py "$BUILD" >/dev/null
python -I -c "from PIL import Image; Image.new('RGBA',(8,8),(0,0,0,0)).save('$BUILD/empty.png')"

round_crop() {  # the screen is round: black outside the bezel
  python -I - "$1" "$2" <<'EOF'
import sys
from PIL import Image, ImageDraw
src, dst = sys.argv[1], sys.argv[2]
im = Image.open(src).convert("RGB")
m = Image.new("L", (im.width * 4, im.height * 4), 0)
ImageDraw.Draw(m).ellipse([0, 0, m.width - 1, m.height - 1], fill=255)
m = m.resize(im.size, Image.LANCZOS)
out = Image.new("RGB", im.size, (0, 0, 0))
out.paste(im, (0, 0), m)
out.save(dst, optimize=True)
EOF
}

case "$FACE" in
  nvc)
    OUT=art/out
    "$BLENDER" -b -P art/blender/current.py -- "$ROOT/$BUILD/bg_3d_raw.png" "$SAMPLES" 2>&1 | grep -E "rendered|Error"
    "$BLENDER" -b -P art/blender/hands.py -- "$ROOT/$BUILD/hands" 128 nvc 2>&1 | grep -E "Error" || true
    python -I art/blender/cut_hands.py "$BUILD/hands" "$OUT" >/dev/null
    cp "$BUILD/hands/placement.json" "$OUT/hand3d_placement.json"
    round_crop "$BUILD/bg_3d_raw.png" "$OUT/bg_3d.png"
    ;;
  navigator)
    OUT=art/out/navigator
    mkdir -p "$OUT"
    "$BLENDER" -b -P art/blender/navigator.py -- "$ROOT/$BUILD/navigator_bg_raw.png" "$SAMPLES" bg 2>&1 \
      | grep -E "rendered|Error"
    "$BLENDER" -b -P art/blender/hands.py -- "$ROOT/$BUILD/hands_navigator" 128 navigator 2>&1 | grep -E "Error" || true
    python -I art/blender/cut_hands.py "$BUILD/hands_navigator" "$OUT" >/dev/null
    cp "$BUILD/hands_navigator/placement.json" "$OUT/hand3d_placement.json"
    round_crop "$BUILD/navigator_bg_raw.png" "$OUT/bg_3d.png"
    python -I art/blender/navigator_aod.py "$OUT" "$BUILD" >/dev/null
    ;;
  *) echo "cara desconocida: $FACE" >&2; exit 2 ;;
esac
echo "3D art in $OUT"
