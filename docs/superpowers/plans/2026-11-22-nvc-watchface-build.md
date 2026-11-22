# Esfera NVC — plan de construcción

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construir la esfera NVC de la maqueta v4 en Watch Face Format, instalarla por adb en el
OnePlus Watch 3 del usuario y verificarla con capturas del reloj real.

**Architecture:** Proyecto Gradle sin código (`hasCode=false`) cuyo único contenido es
`res/raw/watchface.xml` y sus recursos (fondo generado por script, agujas, fuente). Un segundo
módulo, sólo de depuración, publica complicaciones de glucosa falsas para forzar los estados que
Gluroo no permite provocar (hipo, hiper, vacío, viejo). Un script cierra el ciclo
compilar → validar → instalar → seleccionar → capturar.

**Tech Stack:** Watch Face Format (versión según la de Wear OS del reloj), AGP 9.4.0, Gradle 9.7.1,
Kotlin 2.4.10 (sólo el módulo de pruebas), Python 3.11 + Pillow (arte), adb por depuración
inalámbrica.

**Spec:** `docs/superpowers/specs/2026-11-22-nvc-watchface-design.md` (léelo entero; este plan
remite a sus secciones).

## Global Constraints

- Pantalla 466×466; recursos a 2× (fondo 932×932). Geometría exacta: diseño §5.3.
- Paleta: oro `#C9A86A`, oro claro `#E6CD95`, oro apagado `#6E5A33`, blanco `#EFEDE7`, gris `#8C8A84`, pista `#1B1B1E`.
- Tipografía Barlow Condensed (SIL OFL), empaquetada en la esfera, con su licencia en el repo.
- Glucosa: aro 70–180 mg/dL calculado por la esfera; oro dentro, rojo < 70, ámbar > 180; sin dato «--» en gris; nunca un valor inventado ni el último conocido (§5.5).
- **No se inventan nombres de WFF**: cada elemento, atributo, fuente de datos o expresión se comprueba en la documentación oficial (developer.android.com/training/wearables/wff) antes de escribirlo; se apunta el enlace en un comentario del XML la primera vez que se usa.
- El fondo sólo sale de `art/render_bg.py`; no se edita a mano.
- Todo comando adb lleva `-s <serial del reloj>`; con MSYS, `MSYS_NO_PATHCONV=1` en rutas del dispositivo.
- `JAVA_HOME` = JBR de Android Studio; Gradle se lanza con un `.bat` (trampas en el `CLAUDE.md` global).
- Commits en inglés con prefijo convencional y **sin atribución a Claude**; documentación y textos en español.
- Nada se da por hecho sin captura del reloj real; cada tarea apunta en `docs/pruebas/` dónde se probó y qué queda pendiente.

## Review Focus

1. **Lectura vieja mostrada como actual**: con la complicación falsa en modo «viejo» (lectura de hace 25 min), la antigüedad debe verse en pantalla activa y en Always-On. Prueba en la tarea 6.
2. **Complicación de glucosa vacía o sin asignar**: «--» gris, aro vacío, sin flecha, sin color. Prueba en la tarea 6.
3. **Toque en la zona de solape** entre la sub-esfera central y una lateral, y sobre el hueco de antigüedad: debe abrir siempre la glucosa. Prueba en la tarea 7.
4. **Hipoglucosa en Always-On**: un 55 debe verse rojo apagado en ambiente, no oro. Prueba en la tarea 6.
5. **Valores extremos**: 39 y 400 saturan el aro sin desbordarlo ni romper el texto (3 cifras caben). Prueba en la tarea 6.

---

## Estructura de ficheros

| Ruta | Responsabilidad |
|---|---|
| `settings.gradle.kts`, `build.gradle.kts`, `gradle/`, `gradlew*`, `.gitignore` | copiados de TouchGuard y adaptados |
| `watchface/build.gradle.kts` | módulo de la esfera, sin código |
| `watchface/src/main/AndroidManifest.xml` | `hasCode=false`, propiedad de versión WFF, `uses-feature` de reloj |
| `watchface/src/main/res/raw/watchface.xml` | la esfera |
| `watchface/src/main/res/xml/watch_face_info.xml` | metadatos (vista previa, editable) |
| `watchface/src/main/res/drawable-nodpi/` | `bg_bajo.png`, `logo.png`, agujas, vista previa |
| `watchface/src/main/res/font/` | Barlow Condensed |
| `fakeglucose/` | módulo de depuración: proveedor de complicaciones falsas de glucosa |
| `art/render_hands.py` + `art/tests/test_render_hands.py` | generador determinista de agujas |
| `scripts/watch.sh` | compilar, validar, instalar, seleccionar y capturar |
| `docs/pruebas/` | registro de pruebas en el reloj, con capturas |

---

### Task 1: Prueba de instalación de una esfera mínima (puerta del proyecto)

Si esta tarea falla, **se para todo** (diseño §7, riesgo 9): se documenta el fallo y se vuelve a
decidir con el usuario. No se empieza la tarea 2.

**Files:**
- Create: `settings.gradle.kts`, `build.gradle.kts`, `gradle/libs.versions.toml`, `gradle/wrapper/`, `gradlew`, `gradlew.bat`, `.gitignore`, `local.properties` (gitignored)
- Create: `watchface/build.gradle.kts`, `watchface/src/main/AndroidManifest.xml`, `watchface/src/main/res/raw/watchface.xml`, `watchface/src/main/res/xml/watch_face_info.xml`, `watchface/src/main/res/drawable-nodpi/preview.png`, `watchface/src/main/res/values/strings.xml`
- Create: `scripts/watch.sh`
- Create: `docs/pruebas/01-instalacion.md`

**Interfaces:**
- Produces: `scripts/watch.sh <serial> [build|install|select|shot <nombre>|all]`; las capturas van a `docs/pruebas/capturas/<nombre>.png`.
- Produces: application id `com.nvc.watchface` (debug: `com.nvc.watchface.debug`).
- Produces: versión de WFF elegida, apuntada en `docs/pruebas/01-instalacion.md` y en el manifiesto.

- [ ] **Step 1: Conectar el reloj.** Activar depuración inalámbrica en el reloj, `adb pair <ip:puerto>` con el código y `adb connect <ip:puerto>`. `adb devices -l` debe listar el reloj además del Pixel/emulador. Apuntar el serial.
- [ ] **Step 2: Leer la versión del sistema.** `adb -s <serial> shell getprop ro.build.version.sdk` y `getprop ro.build.version.release`, y la versión del servicio de esferas (`dumpsys package com.google.wear.watchface.runtime` u homólogo; comprobar el nombre del paquete en la documentación de WFF). Elegir la versión de WFF más alta que admita y apuntarla.
- [ ] **Step 3: Proyecto Gradle.** Copiar de TouchGuard los ficheros de la lista y quitar Compose, Kotlin y dependencias. `watchface/build.gradle.kts`: plugin `com.android.application`, `namespace = "com.nvc.watchface"`, `minSdk = 33`, `compileSdk = 37` + `compileSdkMinor = 1`, `targetSdk` el que pida la documentación de WFF para esa versión, sin dependencias, debug con `applicationIdSuffix = ".debug"`.
- [ ] **Step 4: Manifiesto y esfera mínima.** Manifiesto según la guía oficial «Watch Face Format setup» (`hasCode=false`, `uses-feature` de reloj, propiedad de versión de WFF). `watchface.xml` de 466×466 con fondo negro y la hora digital en oro `#C9A86A`, nada más. Vista previa 466×466 negra con el logo.
- [ ] **Step 5: Script.** `scripts/watch.sh` con `JAVA_HOME` exportado, `./gradlew.bat :watchface:assembleDebug`, validación con el validador oficial de WFF (descargarlo de su repositorio de GitHub de Google a `C:\Users\criso\.claude\tools\android\`, nunca al repo) e `adb -s` para instalar. Para seleccionar, usar el comando de depuración documentado por Google para fijar una esfera por adb; si no hay, seleccionarla a mano en el reloj y decirlo.
- [ ] **Step 6: Compilar y validar.** `scripts/watch.sh <serial> build`. Esperado: APK en `watchface/build/outputs/apk/debug/` y el validador sin errores.
- [ ] **Step 7: Instalar y seleccionar.** `scripts/watch.sh <serial> install` y `select`. Esperado: `Success` y la esfera en el selector del reloj. Si falla: guardar la salida completa y `adb logcat -d` en `docs/pruebas/01-instalacion.md`, commit, y **parar**.
- [ ] **Step 8: Capturar.** `scripts/watch.sh <serial> shot 01-minima`. Esperado: PNG 466×466 con la hora en oro.
- [ ] **Step 9: Registro y commit.** Rellenar `docs/pruebas/01-instalacion.md` (serial, versiones, WFF elegido, resultado, captura). Actualizar el «Estado» de `CLAUDE.md` y la fila de versión de Wear OS del diseño §3.

```bash
git add -A ':!myNVCWatchFace.code-workspace'
git commit -m "feat: minimal WFF watch face installed on the watch"
```

### Task 2: Inspección de complicaciones en el reloj (puerta de la glucosa)

Resuelve los riesgos 3 y 4 con datos reales: qué tipos y campos mandan Gluroo y el lanzador de
entrenamientos de OHealth.

**Files:**
- Modify: `watchface/src/main/res/raw/watchface.xml` (temporal: esfera de inspección)
- Create: `docs/pruebas/02-complicaciones.md`

**Interfaces:**
- Consumes: `scripts/watch.sh` (tarea 1).
- Produces: en `02-complicaciones.md`, por proveedor: nombre exacto, tipos admitidos y qué campo trae valor, mín/máx, tendencia y antigüedad. Esa tabla decide los tipos de las tareas 6 y 7.

- [ ] **Step 1: Esfera de inspección.** Cuatro huecos de complicación grandes, cada uno admitiendo todos los tipos que WFF permite, que pinten en texto cada campo disponible (texto, título, valor, mín, máx…), con nombres de campo verificados en la documentación.
- [ ] **Step 2: Asignar en el reloj** las complicaciones de Gluroo («Big BG», «CGM (Range)» y cualquier otra que ofrezca) y la de entrenamientos que usa hoy el usuario. Capturar cada una.
- [ ] **Step 3: Cruzar con el sistema.** `adb -s <serial> shell dumpsys` del servicio de complicaciones para ver los proveedores y sus tipos. Apuntar los resultados.
- [ ] **Step 4: Decidir la antigüedad.** Si alguna complicación de Gluroo trae antigüedad u hora de la lectura, apuntar cuál y en qué campo. **Si ninguna la trae, parar la parte de glucosa y volver a decidir con el usuario** (diseño §5.5). Las tareas 3 a 5 pueden seguir mientras tanto.
- [ ] **Step 5: Restaurar** `watchface.xml` a la versión de la tarea 1, registro y commit (`docs: complication inspection results`).

### Task 3: Fondo y capa estática

**Files:**
- Create: `watchface/src/main/res/drawable-nodpi/bg_bajo.png`, `logo.png` (copiados de `art/out/`)
- Modify: `watchface/src/main/res/raw/watchface.xml`
- Modify: `scripts/watch.sh` (paso `build` regenera el fondo y comprueba que no cambia)

- [ ] **Step 1:** El paso `build` ejecuta `python -I art/render_bg.py art/data/ne_50m_land.geojson art/src/logo-nvc.jpg art/out bajo`, copia `bg_bajo.png` y `logo.png` al módulo y falla si `git diff --exit-code art/out` cambia.
- [ ] **Step 2:** Fondo a pantalla completa (932×932 escalado a 466×466) sólo en pantalla activa; en Always-On, negro con el logo al 32 % de opacidad centrado en (233, 127), 72 de ancho.
- [ ] **Step 3:** Compilar, instalar, capturar `03-fondo` y `03-fondo-aod` (forzar ambiente con el comando de depuración documentado o esperando al apagado). Comparar con `docs/mockup/esfera.html` a la misma escala: el logo y las ventanas deben caer en su sitio con un error de ±1 px.
- [ ] **Step 4:** Registro en `docs/pruebas/03-fondo.md` y commit (`feat: background and ambient logo`).

### Task 4: Agujas

**Files:**
- Create: `art/render_hands.py`, `art/tests/test_render_hands.py`
- Create: `watchface/src/main/res/drawable-nodpi/hand_hour.png`, `hand_minute.png`, `hand_second.png`, sus versiones `_aod` en contorno, `hand_cap.png`

**Interfaces:**
- Produces: `render_hands(out_dir: Path) -> list[Path]`; CLI `python -I art/render_hands.py art/out`.

- [ ] **Step 1: Test.**

```python
def test_hands_are_deterministic(tmp_path):
    a = render_hands(tmp_path / "a"); b = render_hands(tmp_path / "b")
    assert [p.read_bytes() for p in a] == [p.read_bytes() for p in b]

def test_hand_lengths_match_spec(tmp_path):
    # imágenes a 2×, pivote en el centro de una caja de 466×466 (×2)
    paths = {p.stem: p for p in render_hands(tmp_path)}
    assert reach_px(paths["hand_hour"]) == pytest.approx(117 * 2, abs=2)
    assert reach_px(paths["hand_minute"]) == pytest.approx(177 * 2, abs=2)
    assert reach_px(paths["hand_second"]) == pytest.approx(189 * 2, abs=2)
    assert counter_px(paths["hand_second"]) == pytest.approx(37 * 2, abs=2)
```

`reach_px` / `counter_px`: distancia del píxel opaco más lejano al pivote, hacia arriba y hacia abajo.

- [ ] **Step 2:** `python -I -m pytest art/tests -v` → falla (no existe el módulo).
- [ ] **Step 3:** Implementar con Pillow: horaria y minutero dorados ahusados con sombra; segundero claro y fino con contrapeso en anillo; tapa r 7 con aro dorado (diseño §5.4). Mismo modelo de luz que el fondo.
- [ ] **Step 4:** Test en verde.
- [ ] **Step 5:** Agujas en `watchface.xml` (horaria, minutero, segundero sólo activo; en Always-On las de contorno). Segundero a saltos de 1 s salvo que la medición de la tarea 8 permita barrido.
- [ ] **Step 6:** Capturar `04-agujas` a una hora fija si el reloj permite fijarla por depuración; si no, anotar la hora de la captura y comprobar ángulos. Commit (`feat: generated hands`).

### Task 5: Ventanas de fecha y batería

**Files:**
- Create: `watchface/src/main/res/font/barlow_condensed_semibold.ttf`, `docs/licencias/OFL-BarlowCondensed.txt`
- Modify: `watchface/src/main/res/raw/watchface.xml`

- [ ] **Step 1:** Buscar en la referencia de WFF las fuentes de datos de día de la semana abreviado, día del mes, porcentaje de batería y, si existe, batería baja. Apuntarlas en el XML con su enlace.
- [ ] **Step 2:** Fecha en la ventana de (371, 233): día en oro y número en blanco, ~12,5 px, en el idioma del reloj. Batería en (95, 233): icono con relleno proporcional y «86%»; rojo cuando esté baja (señal de WFF, o umbral ≤ 15 % si no existe).
- [ ] **Step 3:** En Always-On, sólo la fecha, en oro apagado.
- [ ] **Step 4:** Capturar `05-ventanas` y comprobar que «MIÉ», «SÁB» y dos cifras caben en el hueco de 46×19. Commit (`feat: date and battery windows`).

### Task 6: Sub-esfera de glucosa

Requiere la decisión de antigüedad de la tarea 2.

**Files:**
- Create: `fakeglucose/build.gradle.kts`, `fakeglucose/src/main/AndroidManifest.xml`, `fakeglucose/src/main/java/com/nvc/fakeglucose/FakeGlucoseService.kt`, `.../FakeGlucoseReceiver.kt`
- Modify: `settings.gradle.kts`, `watchface/src/main/res/raw/watchface.xml`
- Create: `docs/pruebas/06-glucosa.md`

**Interfaces:**
- Produces: proveedor «Glucosa falsa» con los mismos tipos que Gluroo (según la tarea 2). Su estado se fija por broadcast, sólo en debug:
  `adb -s <serial> shell am broadcast -a com.nvc.fakeglucose.SET -n com.nvc.fakeglucose/.FakeGlucoseReceiver --ei value <mg/dL> --ei age_min <min> [--ez empty true]`
  y fuerza la actualización de la complicación.
- Produces: el proveedor falso de antigüedad, si Gluroo la da en una complicación aparte, con el mismo formato que la de Gluroo.

- [ ] **Step 1: Proveedor falso.** Módulo Android en Kotlin con la librería de origen de datos de complicaciones de AndroidX (versión estable actual en Google Maven; no inventar). Sólo se instala en el reloj para pruebas, nunca forma parte de la esfera.
- [ ] **Step 2: Casos de prueba** (escribirlos en `06-glucosa.md` antes de implementar; cada uno es broadcast + captura activa + captura ambiente):

| Caso | Entrada | Esperado |
|---|---|---|
| normal | 112, 4 min | aro ~38 % (112 en 70–180), oro, «hace 4 min» |
| límite bajo | 70, 1 min | aro vacío, oro |
| hipo | 55, 2 min | aro vacío, valor y aro rojos; rojo apagado en ambiente |
| hiper | 250, 3 min | aro lleno, ámbar |
| extremos | 39 y 400 | aro saturado, texto entero, sin desbordar |
| viejo | 112, 25 min | antigüedad visible en activo y en ambiente |
| vacío | `--ez empty true` | «--» gris, aro vacío, sin flecha, sin color |
| sin antigüedad | hueco de antigüedad sin asignar | «sin hora» en gris |
| sólo texto | complicación de tipo texto | texto tal cual, sin aro ni color |

- [ ] **Step 3: Implementar** en `watchface.xml`: hueco de glucosa centrado en (233, 321); aro r 38,5, trazo 3, pista `#1B1B1E`, progreso `clamp((v-70)/110, 0, 1)` con la sintaxis de expresiones de WFF verificada; color por condición sobre el valor; valor ~31 px peso 600, flecha, «mg/dL»; hueco de antigüedad pequeño bajo el valor; Always-On según §5.4 y §5.5.
- [ ] **Step 4: Ejecutar los nueve casos** con el proveedor falso. Todos en verde con captura, o se corrige antes de seguir.
- [ ] **Step 5: Probar con Gluroo real** asignado en el reloj: captura `06-gluroo` y comparación con el valor del móvil.
- [ ] **Step 6:** Commit (`feat: glucose sub-dial with range colors and reading age`).

### Task 7: Sub-esferas de actividad y tiempo, y prioridad de toque

**Files:**
- Modify: `watchface/src/main/res/raw/watchface.xml`, `watchface/src/main/res/xml/watch_face_info.xml`
- Create: `docs/pruebas/07-toques.md`

- [ ] **Step 1:** Actividad en (161, 295), r 36, con los tipos que admite el lanzador de OHealth según la tarea 2; icono desplazado a la izquierda. Tiempo en (305, 295), texto corto con icono, desplazado a la derecha. Proveedores por defecto si WFF los permite.
- [ ] **Step 2:** Orden y límites de toque para que la central gane en el solape y cubra el hueco de antigüedad (mecanismo verificado en la documentación).
- [ ] **Step 3: Pruebas de toque** con `adb -s <serial> shell input tap x y`, mirando qué app queda en primer plano (`dumpsys activity activities`): (233, 321), (233, 340) sobre la antigüedad, (196, 300) y (270, 300) en los solapes, (161, 295) y (305, 295). Esperado: los cuatro primeros abren Gluroo; los dos últimos, OHealth y el tiempo.
- [ ] **Step 4:** Capturas, registro y commit (`feat: activity and weather complications with tap priority`).

### Task 8: Always-On, batería y cierre

**Files:**
- Create: `docs/pruebas/08-cierre.md`
- Modify: `CLAUDE.md` (Estado), `README.md` (nuevo: cómo regenerar, compilar e instalar)

- [ ] **Step 1: Píxeles encendidos en ambiente.** Sobre la captura de ambiente, porcentaje de píxeles no negros con PIL. Comparar con el límite que fije la documentación de WFF/Wear OS y apuntarlo.
- [ ] **Step 2: Batería.** Con la esfera puesta 24 h de uso normal, comparar el consumo con el de la esfera actual del usuario (`dumpsys batterystats`, misma franja). Si gasta claramente más, quitar el barrido del segundero y repetir.
- [ ] **Step 3: Comparación final** con la maqueta v4, lado a lado (activo y ambiente), en `08-cierre.md`.
- [ ] **Step 4: Prueba de reinicio**: reiniciar el reloj y comprobar que la esfera sigue seleccionada y la glucosa vuelve a aparecer.
- [ ] **Step 5:** README, Estado en `CLAUDE.md`, commit (`docs: final verification on the watch`) y push con el visto bueno del usuario.
