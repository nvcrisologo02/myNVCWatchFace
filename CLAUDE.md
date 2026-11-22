# Instrucciones de trabajo — esfera NVC para OnePlus Watch 3

Esfera personal (Wear OS, Watch Face Format) para el **OnePlus Watch 3** del usuario: negra y
dorada, mapamundi en bajo relieve, logo «NVC zZz», glucosa en la sub-esfera central y acceso de
un toque a un entrenamiento. Uso personal, instalación por adb, sin tienda.

**Antes de proponer nada, lee el diseño:**
`docs/superpowers/specs/2026-11-22-nvc-watchface-design.md`. Ahí están las decisiones, la
geometría exacta, los riesgos por orden y lo que queda a tu criterio. La historia de cómo se
llegó a él está en `docs/traspaso.md`.

El usuario escribe en español; respóndele en español.

## Estado

Diseño cerrado. Plan en `docs/superpowers/plans/2026-11-22-nvc-watchface-build.md`.
**Tarea 1 hecha (2026-11-22):** el reloj (Wear OS 5.0, SDK 34) instala, selecciona por adb y
dibuja una esfera WFF v2 propia; detalle y trampas en `docs/pruebas/01-instalacion.md`.
**Tarea 2 a medias:** Gluroo sí tiene complicación de antigüedad (`BglTimeSince`) y de rango;
falta leer el contenido exacto de cada campo. Estado y pasos en `docs/pruebas/02-complicaciones.md`.
En el reloj está puesta la esfera de inspección (temporal) de `watchface.xml`.
Para trabajar: Bluetooth del reloj apagado (si no, suelta el Wi-Fi) y serial mDNS, no IP.

Ciclo completo: `scripts/watch.sh "<serial>" all <nombre-captura>`. Serial del reloj:
`adb-H631104000081G14004R-e9DEII._adb-tls-connect._tcp.` (con el punto final).

## Reglas

1. **Nada se da por bueno sin probarlo en el reloj real.** Compilar no basta: instalar,
   seleccionar la esfera, capturar con `adb exec-out screencap -p` y comparar con la maqueta.
   Di siempre dónde se probó y qué queda pendiente.
2. **El fondo no se retoca a mano.** Sale de `art/render_bg.py`; cualquier cambio va en el script
   y se regenera. Es determinista: la misma entrada da el mismo PNG byte a byte.
3. **No inventes nombres de WFF.** Elementos, atributos y fuentes de datos se comprueban en la
   documentación oficial de Watch Face Format antes de usarlos. Los *tags* de Watch Face Studio
   (`[BATT_PER]`, `[DAY_1_31]`…) no son los de WFF.
4. **La glucosa es dato de salud.** Un valor antiguo mostrado como actual es el peor fallo
   posible de esta esfera (anti-objetivo nº 1 del diseño).
5. Commits en inglés con prefijo convencional y **sin atribución a Claude** (regla global del
   usuario). Documentación y textos de la esfera en español.

## Reloj y conexión

- OnePlus Watch 3: 466×466, Wear OS 5 de fábrica (la versión actual del reloj del usuario está
  **por comprobar**; decide la versión de WFF).
- Conexión por **depuración inalámbrica** (opciones de desarrollador del reloj). Su serial adb
  aún no se conoce: `adb devices` antes de nada.
- Suele haber más dispositivos conectados (Pixel 8 Pro `3C150DLJG00005`, emulador): usa
  `-s <serial>` en **todos** los comandos adb.
- Toolchain Android (JDK, SDK, adb, apksigner, versiones de AGP/Gradle que funcionan, trampas
  de MSYS): en el `CLAUDE.md` global del usuario. Proyecto Gradle de referencia:
  `C:\Users\criso\source\repos\TouchGuard`.

## Estructura

| Ruta | Qué es |
|---|---|
| `docs/superpowers/specs/` | diseño aprobado |
| `docs/traspaso.md` | crónica de la sesión de diseño y decisiones |
| `docs/mockup/esfera.html` | maqueta interactiva v4 (abrir en el navegador) |
| `docs/referencias/` | imágenes originales del usuario: referencia inicial, su esfera base y su logo |
| `art/render_bg.py` | generador del fondo |
| `art/data/ne_50m_land.geojson` | costas de Natural Earth 1:50m (dominio público) |
| `art/src/logo-nvc.jpg` | logo original, entrada del generador |
| `art/out/` | salida del generador: `bg_bajo.png` (el elegido), `bg_alto.png` (sólo comparación), `logo.png` |

Regenerar el fondo:

```
python -I art/render_bg.py art/data/ne_50m_land.geojson art/src/logo-nvc.jpg art/out bajo
```

## Trampas ya conocidas

- **`ELECTRON_RUN_AS_NODE`** se hereda de VS Code en las herramientas de Claude Code. Cualquier
  app Electron lanzada desde ellas (Watch Face Studio incluido) arranca como Node pelado y se
  cierra al instante. Quítala antes: `Remove-Item Env:\ELECTRON_RUN_AS_NODE`.
- **Watch Face Studio 1.9.9** está extraído, no instalado, en
  `C:\Users\criso\Apps\WatchFaceStudio_1.9.9\`: su instalador se cae en este Windows 11 26H2. No
  forma parte de la construcción (se eligió escribir WFF a mano), pero sirve para comparar.
- Las complicaciones de WFS no tienen «acción»: el toque abre lo que define el proveedor. Para el
  botón de actividad se usa una complicación que el usuario asigna en el reloj.
