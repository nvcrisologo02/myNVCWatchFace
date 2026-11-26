# 07 · NVC Órbita

Diseño: `docs/superpowers/specs/2026-11-26-orbita-design.md`. Plan: `docs/superpowers/plans/2026-11-26-orbita-build.md`.

## WFF comprobado (2026-11-26, antes de construir)

Fuente: developer.android.com/reference/wear-os/wff (source-type, part-text, text-circular,
part-image, color-configuration). Además se pasó un XML de prueba por el validador v2 con todo lo
de abajo a la vez: **PASSED**.

| Nombre en el plan | WFF | Notas |
|---|---|---|
| `SRC_STEPS` | `[STEP_COUNT]` | entero, pasos de hoy (versión 1) |
| `SRC_STEP_PCT` | `[STEP_PERCENT]` | entero 0–100, ya redondeado y limitado (versión 1). `[STEP_GOAL]` ≥ 1000 existe, pero no hace falta |
| `SRC_HR` | `[HEART_RATE]` | float o texto según el dispositivo, de 0 a 240: se usa `round([HEART_RATE])`. **0 = sin lectura**: la documentación no lo dice, se trata como «--» y se comprueba en el reloj |
| Permiso de pulso | — | ninguna página lo menciona. No se declara nada; se mira en el reloj si lo pide (tarea 6) |
| Texto curvado | `<PartText><TextCircular centerX centerY width height startAngle endAngle direction><Font>…` | `TextCircular` sustituye a `Text` dentro de `PartText`; ángulo 0 = 12 h. Fuera de complicaciones, como decide el diseño |
| Tinte del anillo | `<PartImage … tintColor="[CONFIGURATION.colorAnillo]">` con `<UserConfigurations><ColorConfiguration id="colorAnillo" displayName defaultValue><ColorOption id displayName colors="#AARRGGBB"/>` | validado |
| `clamp`, `round` | expresiones | `clamp` ya funciona en la Nocturne en el reloj; `round` aparece en la documentación |
| Slot invisible | `ComplicationSlot` con `<Complication type="…"/>` vacíos | validado. Falta comprobar en el reloj que el toque abre el proveedor |

## Tinte del anillo (tarea 4, 2026-11-26, en el PC)

`python -I art/tint_preview.py art/out/orbita art/blender/build/tintref docs/mockup/propuestas/orbita_tinte.png`
compone en el PC lo que hará el reloj (capa `ring_tint.png` multiplicada por el color, canal a canal en
sRGB) y ajusta cada color a la media de los sectores del render de Blender en ese color (`orbita.py`,
modo `ref`). Fila de arriba: el tinte; fila de abajo: Blender.

`RING_ARGB` (error medio por canal < 1):

| Color | ARGB |
|---|---|
| verde | `#ff559254` |
| naranja | `#ffdc6e0b` |
| rojo | `#ffb10d0b` |
| amarillo | `#ffe7bb0f` |
| azul | `#ff0d5aac` |

Lo único que el tinte no reproduce es el reflejo del color del anillo en el borde del globo, que en el
render de Blender es apenas visible. Que el reloj multiplique igual que PIL se comprueba en la tarea 6.

## En el reloj (tarea 6, 2026-11-26)

OnePlus Watch 3, Wear OS 5, WFF v2. Ciclo: `FACE=orbita scripts/watch.sh <serial> all orbita-vN`.

### v1 — `capturas/orbita-v1.png`
- Instala, se selecciona y dibuja. Superpuesta al boceto (`art/blender/build/ovl_watch.png`), coinciden
  anillo, números, globo, satélite, sub-esfera, textos curvados de la banda e icono de pila.
- Datos reales: 3915 pasos, batería 48 %, 66 BPM, glucosa 138 en blanco (Gluroo). La marca de pasos
  se coloca según `[STEP_PERCENT]`.
- **Fallo:** la zapatilla pisaba el sector de color (lo vio el usuario).

### v2 — `capturas/orbita-v2.png`, `orbita-v2b.png`
- Zapatilla a −45° y número desde −40°: queda sobre la banda blanca. Test
  `test_band_icons_stay_off_the_coloured_sectors`.
- **Color:** el usuario lo cambió a naranja en Personalizar y el tinte se aplica (captura v2). El
  enfoque A funciona en el reloj.
- **Fallo:** el pulso desaparecía con pulso 0. Forzando la rama «sin lectura» se vio la causa: el
  texto fijo `-- BPM` dentro de `TextCircular` con saltos de línea alrededor **no se dibuja** (el
  validador lo acepta). En línea, sí.

### v3 — `capturas/orbita-v3.png`
- «-- BPM» visible sin lectura. Test `test_fixed_font_text_is_inline`.
- **Entreno:** tocar los pasos abre «Entrenamiento libre» de OHealth (captura intermedia).
- El usuario lo da por bueno: «todo listo, me gusta».

### Glucosa con `fakeglucose` (2026-11-26) — `capturas/orbita-glu-*.png`
- **Fallo del proveedor falso, no de la esfera:** al elegirlo en Personalizar el selector se cerraba y
  dejaba el hueco vacío. El reloj pide una vista previa y androidx la rechaza si el valor de rango no
  lleva texto, título ni imagen (`IllegalArgumentException` en `getComplicationPreviewData`). Arreglado
  en `FakeState.range()` (lleva el valor también como texto).
- Resultados (Bluetooth apagado):

| Caso | Se ve | Bien |
|---|---|---|
| 112 | 112 blanco | sí |
| 39 | 39 rojo | sí |
| 69 | 69 rojo | sí |
| 70 | 70 blanco | sí |
| 180 | 180 blanco | sí |
| 181 | 181 ámbar | sí |
| 400 | 400 ámbar | sí |
| 401 | 400 ámbar (el proveedor limita a 20–400, como Gluroo) | sí |
| sin dato (`NoData`) | sub-esfera vacía | sí: nunca un valor viejo |

- **Sin dato real de Gluroo** (Bluetooth apagado, sin móvil) llega `NoDataComplicationData`: la esfera deja
  la sub-esfera vacía. El «--» gris sólo sale con el hueco vacío a propósito (`EMPTY`); WFF no tiene tipo
  `NO_DATA` (documentación de `Complication` y `ComplicationSlot`), así que no se puede dibujar otra cosa.

### Pendiente
- Pulso 0 con el reloj puesto: no confirmado que 0 sea siempre «sin lectura».
- Always-On: no está activado en el reloj; sin comprobar en pantalla.
