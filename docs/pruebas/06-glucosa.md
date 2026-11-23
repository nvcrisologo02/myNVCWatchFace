# Prueba 6 · Sub-esfera de glucosa

**Estado (2026-11-23):** en el reloj con Gluroo real: 185 → aro entero y valor en ámbar, flecha «→» (captura `03-completa-v11.png`). Antigüedad retirada y hueco sólo RANGED_VALUE (diseño §10). Los casos con el proveedor falso siguen pendientes.

**Estado anterior:** construida y validada, sin probar en el reloj. La esfera completa pasa el
validador de WFF v2 y compila; el proveedor falso compila. Nada de esta lista se ha visto aún en
el reloj.

## Cómo está hecha

- **Hueco «Glucosa»** (centro (233, 321), r 44), tipos RANGED_VALUE, SHORT_TEXT y EMPTY.
  Proveedor por defecto: rango de glucosa de Gluroo.
  - RANGED_VALUE: `Condition` con tres ramas sobre `[COMPLICATION.RANGED_VALUE_VALUE]`:
    `< 70` rojo, `> 180` ámbar, resto oro. En v2 el color de un trazo no admite expresiones
    (sólo desde v4), por eso son tres ramas ya coloreadas.
  - Dentro del rango, el aro va de 0 a 360° con `clamp((v - 70) / 110, 0, 1) * 360`.
  - **Fuera del rango, el aro se dibuja entero en el color de aviso.** Decisión de construcción:
    con el aro «saturado a cero», una hipo no se vería roja en el aro, y el diseño pide que
    cambien el valor y el aro.
  - SHORT_TEXT: el texto tal cual, sin aro de progreso ni color.
  - EMPTY: «--» en gris y la pista del aro vacía.
- **Hueco «Tendencia»** (a la derecha del valor): último carácter del texto de la glucosa en
  texto de Gluroo, con `subText(…, textLength(…) - 1, textLength(…))`.
- **Hueco «Antigüedad»** (bajo el valor): «hace 3m»; vacío, «sin hora» en gris. Se ve también en
  Always-On.
- Always-On: el aro y el valor se mantienen (en rango, valor en gris claro; fuera, con el color
  de aviso atenuado); fuera «mg/dL».

## Casos (`scripts/glucose_cases.sh <serial>`)

Antes, en el reloj, asignar en la esfera NVC los tres proveedores «Glucosa falsa ·…».

| Caso | Entrada | Esperado | Resultado |
|---|---|---|---|
| normal | 112, 4 min, → | aro ~38 %, oro, «hace 4m», → | pendiente |
| límite-bajo | 70, 1 min | aro vacío, oro | pendiente |
| hipo | 55, 2 min, ↓ | aro entero y valor en rojo; rojo atenuado en ambiente | pendiente |
| hiper | 250, 3 min, ↑ | aro entero y valor en ámbar | pendiente |
| extremo-bajo / extremo-alto | 39 / 400 | rojo / ámbar, texto entero sin desbordar | pendiente |
| viejo | 112, 25 min | «hace 25m» visible en activo y en ambiente | pendiente |
| vacío | sin dato | «--» gris, sin flecha, sin color | pendiente |
| sin-antigüedad | antigüedad sin dato | «sin hora» en gris | pendiente |
| sólo texto | asignar el texto falso al hueco «Glucosa» | «112→» tal cual, sin aro | pendiente |

## Riesgos abiertos

- **No está documentado** que `[COMPLICATION.RANGED_VALUE_VALUE]` funcione dentro de
  `Condition`/`Transform`: el validador lo acepta, pero sólo el reloj lo confirma. Si no funciona,
  el plan B es una rama por color con `Variant`/alpha o subir de versión de WFF (no se puede: el
  reloj es v2).
- **La antigüedad puede ser texto fijo** (ver `02-complicaciones.md`, pendiente 1).
- Prioridad de toque entre huecos solapados: sin documentar; tarea 7.
