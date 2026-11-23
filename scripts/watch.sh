#!/usr/bin/env bash
# Build, validate, install, select and capture the NVC watch face on the watch.
# Usage: scripts/watch.sh <adb-serial> [build|validate|install|select|shot <name>|all]
# The serial of a paired watch over wireless debugging ends with a dot, e.g.
#   adb-H631104000081G14004R-e9DEII._adb-tls-connect._tcp.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ADB="${LOCALAPPDATA:-/c/Users/criso/AppData/Local}/Android/Sdk/platform-tools/adb.exe"
JAVA="/c/Program Files/Android/Android Studio/jbr/bin/java"
VALIDATOR="/c/Users/criso/.claude/tools/android/wff-validator.jar"
WFF_VERSION=2
PKG="com.nvc.watchface.debug"
APK="$ROOT/watchface/build/outputs/apk/debug/watchface-debug.apk"

SERIAL="${1:?serial adb del reloj}"
CMD="${2:-all}"
adbw() { "$ADB" -s "$SERIAL" "$@"; }

build() { "$ROOT/scripts/sync_art.sh" && "$ROOT/scripts/build.bat"; }

validate() {
  local out
  out="$("$JAVA" -jar "$VALIDATOR" "$WFF_VERSION" "$ROOT/watchface/src/main/res/raw/watchface.xml" 2>&1)"
  echo "$out"
  [[ "$out" == *PASSED* ]]
}

install() { adbw install -r "$APK"; }

# Not in the official docs; it is the debug broadcast Android Studio uses. Verified on the
# OnePlus Watch 3 (Wear OS 5.0) on 2026-11-22: result=1 and the DWF renderer loads the face.
select_face() {
  adbw shell am broadcast -a com.google.android.wearable.app.DEBUG_SURFACE \
    --es operation set-watchface --es watchFaceId "$PKG"
}

shot() {
  local name="${1:?nombre de la captura}"
  mkdir -p "$ROOT/docs/pruebas/capturas"
  adbw shell input keyevent KEYCODE_WAKEUP
  sleep 2
  adbw exec-out screencap -p > "$ROOT/docs/pruebas/capturas/$name.png"
  echo "docs/pruebas/capturas/$name.png"
}

case "$CMD" in
  build) build ;;
  validate) validate ;;
  install) install ;;
  select) select_face ;;
  shot) shot "${3:-}" ;;
  all) build && validate && install && select_face && sleep 3 && shot "${3:-ultima}" ;;
  *) echo "orden desconocida: $CMD" >&2; exit 2 ;;
esac
