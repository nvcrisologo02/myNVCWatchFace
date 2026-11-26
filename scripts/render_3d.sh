#!/usr/bin/env bash
# Render the 3D art of a watch face with Blender.
#   scripts/render_3d.sh [samples] [nvc|navigator|nocturne|orbita]
# nvc (default):  art/out/bg_3d.png, art/out/hand3d_*.png      -> scripts/sync_art.sh
# navigator, nocturne: art/out/<face>/{bg_3d,ambient_dial,hand3d_*}.png -> scripts/sync_face.sh <face>
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
  nocturne)
    OUT=art/out/nocturne
    mkdir -p "$OUT"
    "$BLENDER" -b -P art/blender/nocturne.py -- "$ROOT/$BUILD/nocturne_bg_raw.png" "$SAMPLES" bg 2>&1 \
      | grep -E "rendered|Error"
    "$BLENDER" -b -P art/blender/hands.py -- "$ROOT/$BUILD/hands_nocturne" 128 nocturne 2>&1 | grep -E "Error" || true
    python -I art/blender/cut_hands.py "$BUILD/hands_nocturne" "$OUT" >/dev/null
    cp "$BUILD/hands_nocturne/placement.json" "$OUT/hand3d_placement.json"
    # keep the render's alpha: the moon aperture is a hole the turning disc shows through
    python -I art/blender/round_alpha.py "$BUILD/nocturne_bg_raw.png" "$OUT/bg_3d.png"
    python -I art/blender/nocturne_aod.py "$OUT" "$BUILD" >/dev/null
    ;;
  orbita)
    OUT=art/out/orbita
    mkdir -p "$OUT"
    python -I art/satellite_sprite.py docs/referencias/satelite.png "$BUILD/orbita_satellite.png" 218 190 112 8 >/dev/null
    "$BLENDER" -b -P art/blender/orbita.py -- "$ROOT/$BUILD/orbita_bg_raw.png" "$SAMPLES" verde bg 2>&1       | grep -E "rendered|Error"
    "$BLENDER" -b -P art/blender/orbita.py -- "$ROOT/$BUILD/orbita_ring_raw.png" "$SAMPLES" verde ring 2>&1       | grep -E "rendered|Error"
    "$BLENDER" -b -P art/blender/hands.py -- "$ROOT/$BUILD/hands_orbita" 128 orbita 2>&1 | grep -E "Error" || true
    python -I art/blender/cut_hands.py "$BUILD/hands_orbita" "$OUT" >/dev/null
    cp "$BUILD/hands_orbita/placement.json" "$OUT/hand3d_placement.json"
    round_crop "$BUILD/orbita_bg_raw.png" "$OUT/bg_3d.png"
    python -I art/blender/round_alpha.py "$BUILD/orbita_ring_raw.png" "$OUT/ring_tint.png"
    cp "$BUILD/orbita_step_marker.png" "$OUT/step_marker.png"
    cp "$BUILD/orbita_icon_battery.png" "$OUT/icon_battery.png"
    cp "$BUILD/orbita_icon_battery_low.png" "$OUT/icon_battery_low.png"
    python -I art/blender/orbita_aod.py "$OUT" "$BUILD" >/dev/null
    ;;
  *) echo "cara desconocida: $FACE" >&2; exit 2 ;;
esac
echo "3D art in $OUT"
