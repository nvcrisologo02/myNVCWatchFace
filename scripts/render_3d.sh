#!/usr/bin/env bash
# Render the 3D art of the installed face with Blender and leave it in art/out:
#   bg_3d.png (932x932 background, no hands), hand3d_<hour|minute|second|cap>[_shadow].png
# Then scripts/sync_art.sh copies it into the watch face resources.
# Usage: scripts/render_3d.sh [samples]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
BLENDER="${BLENDER:-/c/Users/criso/Apps/blender-5.3.0-windows-x64/blender.exe}"
SAMPLES="${1:-256}"
BUILD=art/blender/build

python -I art/blender/make_prints.py "$BUILD" >/dev/null
python -I -c "from PIL import Image; Image.new('RGBA',(8,8),(0,0,0,0)).save('$BUILD/empty.png')"
"$BLENDER" -b -P art/blender/current.py -- "$ROOT/$BUILD/bg_3d_raw.png" "$SAMPLES" 2>&1 | grep -E "rendered|Error"
"$BLENDER" -b -P art/blender/hands.py -- "$ROOT/$BUILD/hands" 128 2>&1 | grep -E "Error" || true
python -I art/blender/cut_hands.py "$BUILD/hands" art/out >/dev/null
cp "$BUILD/hands/placement.json" art/out/hand3d_placement.json
# the screen is round: black outside the bezel
python -I - "$BUILD/bg_3d_raw.png" art/out/bg_3d.png <<'EOF'
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
echo "3D art in art/out"
