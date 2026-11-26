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
