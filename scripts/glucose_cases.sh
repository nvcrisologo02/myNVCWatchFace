#!/usr/bin/env bash
# Run the glucose test cases of plan task 6 against the fake provider and capture each one.
# Before: install the fake provider (this script does it) and, on the watch, assign in the NVC face:
#   Glucosa    -> "Glucosa falsa · rango"
#   Tendencia  -> "Glucosa falsa · texto"
#   Antigüedad -> "Glucosa falsa · antigüedad"
# Usage: scripts/glucose_cases.sh <adb-serial> [case ...]   (no case = all)
# Captures: docs/pruebas/capturas/06-<case>.png and 06-<case>-aod.png
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ADB="${LOCALAPPDATA:-/c/Users/criso/AppData/Local}/Android/Sdk/platform-tools/adb.exe"
SERIAL="${1:?serial adb del reloj}"; shift
adbw() { "$ADB" -s "$SERIAL" "$@"; }

declare -A CASES=(
  [normal]="--ei value 112 --ei age_min 4 --es trend →"
  [limite-bajo]="--ei value 70 --ei age_min 1 --es trend →"
  [hipo]="--ei value 55 --ei age_min 2 --es trend ↓"
  [hiper]="--ei value 250 --ei age_min 3 --es trend ↑"
  [extremo-bajo]="--ei value 39 --ei age_min 2 --es trend ↓"
  [extremo-alto]="--ei value 400 --ei age_min 2 --es trend ↑"
  [viejo]="--ei value 112 --ei age_min 25 --es trend →"
  [vacio]="--ez empty true"
  [sin-antiguedad]="--ei value 112 --ez age_empty true"
)
ORDER=(normal limite-bajo hipo hiper extremo-bajo extremo-alto viejo vacio sin-antiguedad)
[[ $# -gt 0 ]] && ORDER=("$@")

if ! adbw shell pm list packages | grep -q "com.nvc.fakeglucose"; then
  "$ROOT/scripts/build.bat" :fakeglucose:assembleDebug
  adbw install -r "$ROOT/fakeglucose/build/outputs/apk/debug/fakeglucose-debug.apk"
fi

mkdir -p "$ROOT/docs/pruebas/capturas"
for c in "${ORDER[@]}"; do
  echo "== $c: ${CASES[$c]}"
  # shellcheck disable=SC2086
  adbw shell am broadcast -a com.nvc.fakeglucose.SET -n com.nvc.fakeglucose/.SetStateReceiver ${CASES[$c]} >/dev/null
  adbw shell input keyevent KEYCODE_WAKEUP
  sleep 3
  adbw exec-out screencap -p > "$ROOT/docs/pruebas/capturas/06-$c.png"
  adbw shell input keyevent KEYCODE_SLEEP      # ambient, if Always-On is enabled
  sleep 4
  adbw exec-out screencap -p > "$ROOT/docs/pruebas/capturas/06-$c-aod.png"
done
adbw shell input keyevent KEYCODE_WAKEUP
echo "capturas en docs/pruebas/capturas/06-*.png"
