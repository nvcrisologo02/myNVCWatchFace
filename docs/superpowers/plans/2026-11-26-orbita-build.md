# NVC Órbita — plan de construcción

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construir la esfera «NVC Órbita» como cuarto paquete WFF (`com.nvc.orbita`), fiel al boceto
aprobado y con el color del anillo elegible desde el reloj.

**Architecture:** Módulo Gradle sin código `orbita/`, copiado de `nocturne/`. El arte sale de
Blender: un fondo de producción con los sectores en plata neutra, una capa con solo los sectores
que el reloj tiñe con `tintColor`, y las agujas como sprites con sombra. Los impresos y el modo
Always-On salen de PIL. El XML lo genera `scripts/gen_orbita_xml.py` y la instalación usa
`FACE=orbita scripts/watch.sh`.

**Tech Stack:** Blender 5.3 (Cycles), Python 3.11 + PIL + numpy + pytest, WFF v2, Gradle (AGP 9.4),
adb por Wi-Fi.

**Spec:** `docs/superpowers/specs/2026-11-26-orbita-design.md` (aprobado el 2026-11-26). Receta y
trampas: `docs/guia-nueva-esfera.md`.

## Global Constraints

- WFF v2, 466×466, `hasCode=false`, `applicationId com.nvc.orbita` (`.debug` en debug), prefijo de
  recursos `orb_`.
- Ningún nombre de WFF (elemento, atributo, fuente de datos) se usa sin comprobarlo antes en
  developer.android.com/training/wearables/wff o en el validador (regla 3 del CLAUDE.md).
- `x`, `y` y los tamaños de letra de agujas, `PartImage` y `Font` son enteros. El validador
  (`java -jar C:\Users\criso\.claude\tools\android\wff-validator.jar 2 watchface.xml`) tiene que
  decir `PASSED` antes de instalar.
- El arte es determinista y sale de scripts. Ningún PNG ni XML se retoca a mano.
- Glucosa: hueco de solo `RANGED_VALUE` (Gluroo). Valor de 48 px, sin flecha. Blanco `#fff0f0ec`
  de 70 a 180, rojo `#ffe5483c` por debajo de 70, ámbar `#ffe3a63a` por encima de 180 y gris
  `#ff8c8a84` «--» sin dato.
- Medidas del diseño §5: banda r 200–226; sectores de 50° a 130° y de 230° a 310°; ventana del
  globo r 170; sub-esfera (0, 134) con r 46/62; textos de 28 px a r 213, centrados en −33° (pasos),
  206° (batería) y 149° (pulsaciones).
- Marca de progreso de pasos: ángulo `−14 + 68 · clamp(porcentaje, 0, 100) / 100`.
- Nada pequeño entre las 5:30 y las 6:30 junto al bisel.
- Commits en inglés, con prefijo convencional y **sin ninguna atribución a Claude** (regla global
  del usuario: prevalece sobre cualquier otra indicación).
- Nada se da por bueno sin una captura del reloj. Cada informe dice qué se probó en el PC y qué en
  el reloj.

## Review Focus

1. **Glucosa sin dato o con el hueco vacío:** «--» gris, nunca un número viejo ni un 0. Prueba:
   `scripts/glucose_cases.sh` con el caso «sin dato» (tarea 6).
2. **Glucosa en los límites (69/70, 180/181, 39, 401):** el color cambia exactamente en 70 y en 181,
   y el texto no se sale del disco de r 46. Prueba: casos de `fakeglucose` (tarea 6) y un test del
   generador que comprueba los umbrales (tarea 5).
3. **Pasos por encima del objetivo (más del 100 %) o en 0:** la marca se queda en 54° o en −14° y no
   da la vuelta. Prueba: test del generador sobre la expresión con `clamp` (tarea 5).
4. **Pulso sin lectura (reloj fuera de la muñeca, permiso denegado):** «--», no «0 BPM». Prueba:
   rama `Condition` y captura con el reloj sobre la mesa (tareas 5 y 6).
5. **Cambiar de color en «Personalizar»:** solo cambian los sectores; banda, números y Always-On
   no. Prueba: capturas con verde y azul (tarea 6).

---

### Task 1: Comprobar WFF antes de escribir nada

**Files:**
- Create: `docs/pruebas/07-orbita.md` (sección «WFF comprobado»)

**Interfaces:**
- Produces: la tabla «WFF comprobado» en `07-orbita.md`, con los nombres exactos que usan las
  tareas 5 y 6: `SRC_STEPS`, `SRC_STEP_PCT` (o `SRC_STEP_GOAL` para calcularlo), `SRC_HR`, el
  permiso de pulso si hace falta, dónde va `TextCircular` (hijo de `PartText` o no) y la sintaxis de
  `tintColor="[CONFIGURATION.colorAnillo]"`.

- [ ] **Step 1:** Leer en la documentación oficial las fuentes de datos (`.../wff/common/attributes/source-type`)
  y anotar los nombres exactos de pasos, objetivo o porcentaje de pasos y pulso, con la versión de
  WFF en que aparecen. Anotar también si el pulso exige permiso, y cuál.
- [ ] **Step 2:** Escribir un XML de prueba (en el scratchpad, no en el repo) con un `PartText`
  que contenga un `TextCircular` con `[SRC_STEPS]`, un `PartImage` con `tintColor` referido a un
  `ColorConfiguration` y un `ComplicationSlot` vacío. Pasar el validador v2.
  Esperado: `PASSED`. Si falla, anotar el error y la alternativa del diseño §7 (texto recto girado).
- [ ] **Step 3:** Si alguna fuente no existe en v2, **parar y preguntar al usuario** (diseño §7,
  riesgo 2). Si todas existen, escribir la tabla y hacer commit.

```bash
git add docs/pruebas/07-orbita.md
git commit -m "docs: verify WFF names for the Orbita face"
```

### Task 2: Módulo `orbita` y scripts

**Files:**
- Create: `orbita/build.gradle.kts`, `orbita/src/main/AndroidManifest.xml`,
  `orbita/src/main/res/values/strings.xml`, `orbita/src/main/res/xml/watch_face_info.xml`,
  `orbita/src/main/res/font/*` (copiados de `nocturne/`, sin `build/` ni `drawable-nodpi/`)
- Modify: `settings.gradle.kts` (`include(":orbita")`), `scripts/sync_face.sh` (caso `orbita`,
  `PREFIX=orb_`), `scripts/watch.sh` (caso `orbita`, `PKG=com.nvc.orbita.debug`)

**Interfaces:**
- Produces: `FACE=orbita scripts/watch.sh <serial> build|validate|install|select|shot <n>|all`.

- [ ] **Step 1:** Copiar el módulo y cambiar `namespace`/`applicationId` a `com.nvc.orbita`,
  `app_name` a «NVC Órbita». Si la tarea 1 dijo que el pulso necesita permiso, declararlo en el
  manifiesto.
- [ ] **Step 2:** Poner un `watchface.xml` mínimo, con un fondo negro y la hora.
- [ ] **Step 3:** `scripts/build.bat :orbita:assembleDebug`. Esperado: `BUILD SUCCESSFUL`; el APK
  en `orbita/build/outputs/apk/debug/orbita-debug.apk`.
- [ ] **Step 4:** Commit: `feat: add orbita watch face module`.

### Task 3: Arte de producción

**Files:**
- Modify: `art/blender/watchkit.py` (añadir `shoulder_hand` y `_arc`, movidos de `orbita.py` sin
  cambios), `art/blender/orbita.py`, `art/blender/hands.py`, `art/blender/make_prints.py`,
  `scripts/render_3d.sh`
- Create: `art/blender/orbita_aod.py`, `art/tests/test_orbita_art.py`

**Interfaces:**
- Consumes: `watchkit.shoulder_hand(name, deg, length, tail, w_base, base_len, w, slot, z, thick, mat, bevel=0.05, solid=False)`.
- Produces, en `art/out/orbita/`:
  - `bg_3d.png`: 932², opaco, sin contenido dinámico y con los sectores en plata neutra.
  - `ring_tint.png`: 932², alfa solo en los sectores (r 200–226; 50–130° y 230–310°), en blanco y
    gris con el sombreado.
  - `hand3d_{hour,minute,second,cap}.png` y sus `_shadow.png`, más `hand3d_placement.json`, con la
    forma que da `cut_hands.py`.
  - `step_marker.png`: marca naranja de 5×25 px (×2) que apunta a las 12, con el pivote en el
    centro de la esfera.
  - `ambient_dial.png` y `hand3d_{hour,minute}_aod.png`.
  - `icon_battery.png` e `icon_battery_low.png` (pila de 26×12 px, en tinta oscura y en rojo).
    La zapatilla es fija, así que se imprime en el fondo, a la izquierda del texto de pasos.

- [ ] **Step 1: Write the failing tests** en `art/tests/test_orbita_art.py`:
  - `test_prints_deterministic`: dos llamadas a `make_prints.orbita(tmp)` dan los mismos bytes en
    `orbita_print_bg.png`, `orbita_map.png` y `orbita_ring_mask.png`.
  - `test_bg_print_has_no_dynamic_content`: en `orbita_print_bg.png` no hay ningún píxel naranja
    (R > 200, G < 120, B < 80) en el arco r 200–227 entre −20° y 60°, porque la marca ya no se
    imprime; y la zona del texto a −33°, 206° y 149° (r 205–221, ±12°) es transparente.
  - `test_ring_mask_sectors`: en `orbita_ring_mask.png` el valor es 255 en (r 213, 90°) y en
    (r 213, 270°), y 0 en (r 213, 0°), (r 213, 180°) y (r 190, 90°).
  - `test_step_marker_geometry`: `step_marker.png` tiene el alfa dentro de x ∈ [C−6, C+6] e
    y ∈ [C−2·227, C−2·200].
- [ ] **Step 2:** `python -m pytest art/tests/test_orbita_art.py -v`. Esperado: FAIL.
- [ ] **Step 3:** Hacer los cambios:
  - **`make_prints.orbita`:** quitar la marca naranja del impreso de fondo y escribir aparte
    `step_marker.png` (la marca a 0°, r 201–226, 5 px).
  - **`orbita.py` en modo `bg`:**
    - sin agujas;
    - el anillo usa `SILVER_KW` también en los sectores (los dos lados de la mezcla, plata);
    - con `film_transparent` desactivado y recorte redondo opaco, como la NVC.
  - **Nuevo modo `ring` en `orbita.py`:** solo el anillo, con los sectores en blanco anodizado
    (`Base Color (0.9, 0.9, 0.9)`), película transparente, y el alfa multiplicado por
    `orbita_ring_mask.png`.
  - **`hands.py`:** nueva cara `orbita` con hour, minute, second y cap, usando las medidas de
    `orbita.py` (horaria `14.4, 1.6, 2.0, 0.26, 1.25, 0.62`; minutero `20.0, 1.6, 1.8, 0.20, 1.10, 0.52`;
    segundero `wk.hand(…, 22.1, 4.3, 0.40, 0.16, …)` naranja; tapa naranja r 8 con punto blanco).
  - **`orbita_aod.py`:** fondo negro; números, índices, contorno del globo y continentes al 30 %;
    agujas en silueta blanca tenue.
  - **`render_3d.sh`:** caso `orbita`, que también ejecuta `art/satellite_sprite.py` con
    `218 190 112 8`.
- [ ] **Step 4:** `python -m pytest art/tests -v`. Esperado: todo PASS.
- [ ] **Step 5:** `scripts/render_3d.sh 256 orbita`, dos veces. Comprobar que los PNG de
  `art/out/orbita/` dan los mismos bytes las dos veces (`sha256sum`).
- [ ] **Step 6:** Commit: `feat: render Orbita production art`.

### Task 4: Comprobar el tinte del anillo (puerta A/B)

**Files:**
- Create: `art/tint_preview.py`, `docs/mockup/propuestas/orbita_tinte.png`
- Modify: `docs/pruebas/07-orbita.md`

**Interfaces:**
- Consumes: `art/out/orbita/bg_3d.png`, `art/out/orbita/ring_tint.png`, los renders por color
  `art/blender/build/orbita_<color>.png`.
- Produces: `RING_ARGB = {"verde": "#ff…", "naranja": …, "rojo": …, "amarillo": …, "azul": …}`,
  anotado en `07-orbita.md` y usado por la tarea 5.

- [ ] **Step 1:** `tint_preview.py <bg> <ring> <out> <hex>…` compone en PIL lo que hará el reloj:
  `bg` y encima `ring` × color (multiplicado por canal y con su alfa). Saca una lámina de dos filas:
  la de arriba con el tinte para cada color y la de abajo con el render de Blender en ese color.
- [ ] **Step 2:** Ajustar cada hex hasta que el tono medio de los sectores teñidos quede a menos de
  10 unidades por canal de la media de los mismos sectores en el render por color.
- [ ] **Step 3:** **Enseñar la lámina al usuario.** Si alguno queda claramente peor (los brillos se
  apagan, el amarillo se ensucia), parar y pasar al enfoque B del diseño, con su aprobación.
- [ ] **Step 4:** Commit: `feat: tune Orbita ring tint colours`.

### Task 5: Generador del XML

**Files:**
- Create: `scripts/gen_orbita_xml.py`, `art/tests/test_gen_orbita_xml.py`
- Modify: `orbita/src/main/res/raw/watchface.xml` (generado)

**Interfaces:**
- Consumes:
  - de la tarea 1: los nombres `SRC_*` y la estructura de `TextCircular`;
  - de la tarea 3: `art/out/orbita/hand3d_placement.json`;
  - de la tarea 4: `RING_ARGB`.
- Produces:
  - `build_xml() -> str` en `gen_orbita_xml.py`;
  - las constantes `GLUCOSE_SLOT = 1`, `WORKOUT_SLOT = 10`, `MARKER_ANGLE`;
  - el `watchface.xml` escrito en `orbita/src/main/res/raw/`.

- [ ] **Step 1: Write the failing tests** en `art/tests/test_gen_orbita_xml.py` (importan
  `scripts/gen_orbita_xml.py`):
  - `test_marker_angle_is_clamped`: `MARKER_ANGLE` contiene `clamp(` y los números `-14` y `68`.
  - `test_glucose_thresholds`: el XML tiene las condiciones `< 70`, `<= 180` y `> 180` sobre
    `[COMPLICATION.RANGED_VALUE_VALUE]`, con los colores de Global Constraints, y la rama sin dato
    pinta «--» en `#ff8c8a84`.
  - `test_glucose_slot_ranged_only`: el `ComplicationSlot` con `slotId="1"` tiene
    `supportedTypes="RANGED_VALUE EMPTY"`.
  - `test_workout_slot_invisible`: el slot 10 tiene su `BoundingOval` sobre la zona de los pasos
    (centro a −33°, r 213) y su `Complication` no tiene ningún `PartText` ni `PartImage`.
  - `test_colour_config`: `UserConfigurations` tiene un `ColorConfiguration id="colorAnillo"` con
    cinco `ColorOption`, `defaultValue` igual al id del verde, y el `PartImage` del anillo usa
    `tintColor="[CONFIGURATION.colorAnillo]"`.
  - `test_heart_rate_no_reading`: la pulsación tiene una rama que muestra «--» cuando el pulso es
    0 o no hay lectura.
  - `test_integer_geometry`: todos los `x`, `y`, `width`, `height` y `size` del XML son enteros.
- [ ] **Step 2:** `python -m pytest art/tests/test_gen_orbita_xml.py -v`. Esperado: FAIL.
- [ ] **Step 3:** Escribir `gen_orbita_xml.py` siguiendo `gen_nocturne_xml.py` (usar sus
  funciones `needle`, `shadowed` e `ind`). Orden de capas:
  1. fondo;
  2. anillo teñido;
  3. marca de pasos;
  4. textos curvados de pasos, batería (icono de pila y texto, en rojo con `[BATTERY_IS_LOW]`) y
     pulsaciones;
  5. el slot 10 invisible;
  6. el slot 1 de glucosa (`PartText` centrado en (233, 367), Barlow Condensed 48);
  7. las agujas con su sombra (desplazamiento (2, 3));
  8. Always-On por `Variant`.
- [ ] **Step 4:** Ejecutar `python -m pytest art/tests -v` y luego `FACE=orbita scripts/watch.sh <serial> validate`.
  Esperado: todo PASS y `PASSED`.
- [ ] **Step 5:** Commit: `feat: generate Orbita watchface.xml`.

### Task 6: En el reloj

**Files:**
- Modify: `docs/pruebas/07-orbita.md`, `docs/guia-nueva-esfera.md`, `CLAUDE.md` (Estado),
  `docs/superpowers/specs/2026-11-26-orbita-design.md` (estado y cambios)
- Create: `docs/pruebas/capturas/orbita-v1*.png`

- [ ] **Step 1:** Preparar el reloj: Bluetooth apagado, `adb devices`, y
  `FACE=orbita scripts/watch.sh "<serial>" all orbita-v1`.
  Esperado: instalada, seleccionada y con la captura hecha.
- [ ] **Step 2:** Superponer la captura con `docs/mockup/propuestas/orbita_3d.png`, fundidas al 50 %,
  y anotar las diferencias. Volver a la tarea 3 o a la 5 hasta que coincidan.
- [ ] **Step 3:** En «Personalizar»: elegir azul, capturar `orbita-v1-azul`, y volver a verde.
  Comprobar que solo cambian los sectores (Review Focus 5).
- [ ] **Step 4:** Casos de glucosa con `scripts/glucose_cases.sh`: sin dato, 39, 69, 70, 180, 181 y
  401. Capturar cada uno (Review Focus 1 y 2).
- [ ] **Step 5:** Pulso con el reloj sobre la mesa: debe salir «--» (Review Focus 4). Si pide
  permiso, aceptarlo y anotarlo.
- [ ] **Step 6:** Asignar al slot de entreno OHealth «entrenamiento libre» y tocar los pasos:
  tiene que abrir el entreno.
- [ ] **Step 7:** Comprobar Always-On a ojo (diseño §5) y anotarlo.
- [ ] **Step 8:** Documentar en `07-orbita.md` una sección por versión con sus capturas. Añadir las
  lecciones nuevas a la guía (tinte, `TextCircular`, fuentes de pasos y pulso). Actualizar el
  estado en el CLAUDE.md.
- [ ] **Step 9:** Commit: `docs: Orbita tested on the watch`.
