# Esfera NVC para OnePlus Watch 3 — diseño

Fecha: 2026-11-22 · Estado: diseño visual cerrado (maqueta v4), pendiente de plan de construcción.

## 1. Intención

Una esfera personal para el **OnePlus Watch 3** del usuario: negra y dorada, con un mapamundi en
bajo relieve y su logo «NVC zZz». Detrás de la estética hay dos necesidades prácticas:

1. **Ver la glucosa de un vistazo.** El usuario es diabético y usa un medidor continuo; su esfera
   actual ya muestra la glucosa en una complicación. En la nueva, la glucosa ocupa la sub-esfera
   central, la mayor, y tiene que seguir leyéndose en modo Always-On.
2. **Empezar un entrenamiento con un toque**, como hace hoy desde su esfera actual.

Uso personal: se instala por adb y no se publica en ninguna tienda.

## 2. Objetivos, no objetivos y anti-objetivos

**Objetivos**
- Reproducir la maqueta v4 aprobada (§5) en el reloj real.
- Glucosa legible de un vistazo, también en Always-On.
- Acceso de un toque a un entrenamiento.
- Construcción reproducible desde el repo: fondo generado por script, esfera escrita a mano en
  Watch Face Format, compilada e instalada con herramientas de línea de órdenes.

**No objetivos**
- Publicar en Google Play o en O-Health.
- Un editor de personalización (colores o estilos elegibles por el usuario).
- Leer la glucosa directamente de la app del medidor: llega sólo por complicación.
- Soportar otros relojes. WFF escala, pero sólo se diseña y se prueba para 466×466.

**Anti-objetivos** (sería un fracaso aunque «funcione»)
- **Mostrar un valor de glucosa antiguo sin que se note.** Es el más grave.
- Que la glucosa desaparezca o no se lea en Always-On.
- Que un toque en la zona donde se solapan las sub-esferas abra la complicación equivocada.
- Que gaste claramente más batería que la esfera actual del usuario.
- Dar algo por bueno sin haberlo instalado y probado en el reloj real.

## 3. Restricciones

| Tema | Hecho | Estado |
|---|---|---|
| Reloj | OnePlus Watch 3: AMOLED LTPO redonda 1,5", **466×466**, Wear OS 5 + RTOS, Snapdragon W5, 2 GB RAM | confirmado (fichas técnicas) |
| Versión de Wear OS del reloj del usuario | Salió con Wear OS 5; puede haber recibido 6 | **a comprobar en el reloj**: decide la versión de WFF |
| Formato | Desde enero de 2026 Wear OS sólo instala esferas en **Watch Face Format** (XML declarativo, sin código) | confirmado (blog de Android Developers, 2025-06) |
| Instalación | Sideload por adb con depuración inalámbrica. **Ninguna fuente confirma que el OnePlus Watch 3 admita esferas instaladas así**; la vía oficial de OnePlus es O-Health | **riesgo nº 1** |
| Complicaciones | El usuario ya usa en su esfera actual una complicación de glucosa y otra que lanza entrenamientos de OHealth → el reloj admite complicaciones de terceros | confirmado por el usuario |
| Toques | En WFF, al tocar una complicación se ejecuta la acción que define su proveedor; la esfera no fija qué app se abre. Para el botón de actividad se usa una complicación que el usuario asigna en el reloj | confirmado para WFS; para WFF, a confirmar si existe además una acción de lanzamiento propia |
| Herramientas | JDK, SDK, adb, apksigner, AGP/Gradle: ver el `CLAUDE.md` global del usuario. Proyecto de referencia Gradle: `C:\Users\criso\source\repos\TouchGuard` | disponible |
| Convenciones | Documentación y textos en español; código e identificadores en inglés; commits convencionales en inglés **sin atribución a Claude** | del usuario |

## 4. Enfoques considerados

- **A · Montar la esfera en Samsung Watch Face Studio** con los recursos preparados y una guía.
  Es la vía estándar, con editor visual, pero el montaje es manual, cada cambio vuelve a ser
  trabajo de ratón y el proyecto no se versiona con sentido.
- **B · Escribir la esfera directamente en Watch Face Format y compilarla con el SDK de Android.**
  Todo queda en el repo, el ciclo compilar → instalar → capturar → corregir se cierra sin la
  intervención del usuario, y el fondo ya sale de un script.

**Elegido: B** (decisión del usuario, 2026-11-22). Motivo: el cuello de botella es iterar sobre el
reloj real, y con B esa iteración no depende de clics del usuario. Watch Face Studio 1.9.9 queda
instalado (§9) por si sirve para comparar con lo que genera, pero no forma parte de la construcción.

## 5. Diseño visual decidido

Referencia visual: `docs/mockup/esfera.html` (abrir en el navegador; los PNG van al lado).
La maqueta publicada (privada, del usuario) es https://claude.ai/artifact/PvXZRq8zNUqaHptpFWUpkV.

### 5.1 Sistema de coordenadas

Unidades de diseño = **píxeles del reloj (466×466)**, origen arriba a la izquierda, centro en
(233, 233). Los recursos se exportan a **2×** (el fondo, 932×932). El generador trabaja con el
origen en el centro: un punto (x, y) del generador es (233 + x, 233 + y) aquí.

### 5.2 Regla de materiales

Una sola luz, arriba a la izquierda, para todo. **Todo lo negro está hundido en la esfera y sólo
sobresale el oro.**

| Pieza | Acabado |
|---|---|
| Esfera (océano) | negro satinado con un brillo suave arriba a la izquierda |
| Continentes | **bajo relieve**: fresados, fondo granallado más oscuro; sólo brillan las paredes que miran a la luz |
| Rayos (72, cada 5°) y puntos de minutería | grabados en la superficie; los rayos se cortan en la costa |
| Sub-esferas y ventanas | hundidas, con fondo liso (las sub-esferas, con caracoleado fino) |
| Índices, aros de sub-esferas y ventanas, logo | oro champán en relieve |
| Bisel exterior | gris metálico con cepillado concéntrico |

La costa está simplificada a escala de reloj: se descartan islas de menos de 6 unidades² y se
cierran canales de menos de ~1,7 unidades.

### 5.3 Geometría (coordenadas del reloj)

| Elemento | Posición y medidas |
|---|---|
| Bisel | anillo r 221–233 |
| Esfera | r ≤ 219,6 |
| Índices de 12, 3, 6 y 9 | dos barras radiales r 194–212, 2,3 de ancho, separadas ±1,9 del eje |
| Índices del resto de horas | una barra r 197–212, 2,6 de ancho |
| Puntos de minutería | r 207, radio 1,3; no hay punto en las horas |
| Logo NVC | centrado en (233, 127), 72 de ancho (proporción del original: 144×124 a 2×) |
| Ventana de fecha (3 h) | centro (371, 233), hueco 46×19, radio 4, marco dorado 1,6 |
| Ventana de batería (9 h) | centro (95, 233), mismas medidas |
| Sub-esfera izquierda · actividad | centro (161, 295), fondo r 36, aro hasta r 38,2 |
| **Sub-esfera central · glucosa** | centro (233, 321), fondo r 44, aro hasta r 46,4; **queda por encima**: su aro corta los de las laterales |
| Sub-esfera derecha · tiempo | centro (305, 295), fondo r 36, aro hasta r 38,2 |
| Mapa | proyección Mercator, meridiano central 10° E, 1,04 unidades por grado, latitudes 84° N a 57° S, centrado 11 unidades por encima del centro |

Todo lo anterior va **dentro de la imagen de fondo** (`art/out/bg_bajo.png`). Encima sólo van las
capas dinámicas de §5.4.

### 5.4 Capas dinámicas

**Paleta:** oro `#C9A86A`, oro claro `#E6CD95`, oro apagado (Always-On) `#6E5A33`, blanco
`#EFEDE7`, gris `#8C8A84`, pista del aro de glucosa `#1B1B1E`.
**Tipografía:** Barlow Condensed (Google Fonts, licencia SIL OFL), empaquetada en la esfera.

| Zona | Contenido en pantalla activa | Fuente del dato |
|---|---|---|
| Fecha (ventana 3 h) | «DOM» en oro + «22» en blanco, ~12,5 px | día de la semana abreviado y día del mes, en el idioma del reloj (español) |
| Batería (ventana 9 h) | icono de pila con relleno proporcional + «86%»; en **rojo** cuando está baja | porcentaje de batería |
| Actividad (izquierda) | el icono que mande la complicación asignada, centrado y algo desplazado hacia la izquierda, lejos del solape | complicación de imagen / atajo de app |
| **Glucosa (centro)** | aro de progreso r 38,5 (trazo 3) según el valor dentro del rango; valor grande (~31 px, peso 600); flecha de tendencia; unidad «mg/dL»; antigüedad de la lectura («hace 4 min») | complicación *Ranged Value*; si el proveedor sólo ofrece *Short Text*, número y texto sin aro |
| Tiempo (derecha) | icono + temperatura (~15 px), algo desplazados hacia la derecha | complicación *Short Text* con icono |
| Agujas | horaria y minutero dorados, ahusados, con sombra; segundero claro y fino con contrapeso en anillo; tapa central r 7 con aro dorado | hora del sistema |

Longitudes de agujas desde el centro: horaria hasta r 117, minutero hasta r 177, segundero hasta
r 189 con su anillo a 37 por el lado opuesto.

**Always-On** (fondo negro, sin imagen de fondo):
- índices como líneas finas en oro apagado;
- logo al 32 % de opacidad;
- fecha en oro apagado;
- glucosa: aro en oro apagado, valor en gris claro y flecha;
- agujas en contorno, sin segundero;
- fuera: batería, actividad, tiempo, rayos y mapa.

### 5.5 Estados de la glucosa

Decisiones provisionales del diseñador (marcadas ✎):

- ✎ **Sin dato** (complicación sin asignar, vacía o «sin datos»): «--» en gris en lugar del valor,
  aro sin progreso y sin flecha. Nunca se muestra un número inventado ni el último conocido.
- ✎ **Antigüedad en Always-On:** si el proveedor manda la antigüedad de la lectura, también se
  muestra en Always-On, en pequeño bajo el valor. Es el modo en que la complicación se refresca
  menos y donde más falta hace.

**Pendiente del usuario** (ver §7, riesgos 3, 8 y 9):
- qué app da la glucosa y qué hacer si no manda la antigüedad de la lectura;
- qué rango cubre el aro y si salirse de él cambia el color;
- qué hacer si la esfera no se puede instalar por adb.

## 6. Construcción (partes decididas)

1. **Fondo:** `art/render_bg.py` lo genera a partir de `art/data/ne_50m_land.geojson` (Natural
   Earth 1:50m, dominio público) y `art/src/logo-nvc.jpg`:
   ```
   python -I art/render_bg.py art/data/ne_50m_land.geojson art/src/logo-nvc.jpg art/out bajo
   ```
   Salida: `art/out/bg_bajo.png` (932×932) y `art/out/logo.png` (144×124, transparente, para
   Always-On). Es determinista: la misma entrada da el mismo fichero byte a byte. El modo `alto`
   (continentes en relieve) se conserva sólo para comparar.
2. **Esfera:** proyecto Android sin código (`hasCode=false`) con la esfera en
   `res/raw/watchface.xml` y sus recursos, compilado con Gradle como TouchGuard.
3. **Firma:** keystore de depuración para el desarrollo; si hace falta una de release, va fuera del
   repo en `C:\Users\criso\keystores\nvc-watchface\`, según las convenciones del usuario.
4. **Instalación y verificación:** adb por depuración inalámbrica al reloj, selección de la esfera y
   **captura con `adb exec-out screencap -p`** para comparar con la maqueta.

## 7. Riesgos y desconocidos, por orden

1. **¿Se puede instalar una esfera WFF por adb en el OnePlus Watch 3?** Si no, el enfoque entero
   cambia. Primera tarea: una esfera mínima instalada y seleccionada en el reloj.
2. **Versión de Wear OS del reloj** → qué versión de WFF se puede usar y, por tanto, qué
   elementos están disponibles. Mirarlo en el reloj antes de escribir el XML definitivo.
3. **Qué app da la glucosa y qué envía su complicación.** No se sabe aún qué app usa el usuario
   (se configura «desde el reloj o desde O-Health»). De ella depende:
   - si hay *Ranged Value* (aro) o sólo *Short Text*;
   - si la tendencia llega como flecha dentro del texto;
   - si la antigüedad de la lectura llega en algún campo.
   WFF no ofrece por sí mismo la hora de la última actualización de una complicación, así que el
   anti-objetivo de «valor viejo sin avisar» depende de lo que mande el proveedor. Si no manda
   nada, hay que decidir con el usuario qué hacer.
4. **Qué proveedor lanza los entrenamientos de OHealth** en la esfera actual, y con qué tipo de
   complicación (para elegir los tipos admitidos en la sub-esfera izquierda).
5. **Nombres de las fuentes de datos en WFF** para fecha y batería. Los *tags* comprobados en
   Watch Face Studio (`[DAY_WEEK_S]`, `[DAY_1_31]`, `[BATT_PER]`, `[BATT_IS_LOW]`) son de WFS y
   **no valen tal cual en WFF**, que tiene sus propios nombres.
6. **Prioridad de toque donde se solapan las sub-esferas.** Hay que comprobar en el reloj que el
   toque en la zona compartida va a la glucosa.
7. **Límite de píxeles encendidos en Always-On.** Medir sobre una captura del modo ambiente.
8. **Qué rango representa el aro de glucosa.** La maqueta usa 70–180 mg/dL fijos, que parece un
   rango objetivo; el rango que manda un proveedor *Ranged Value* suele ser el del sensor
   (~40–400), y con él un 112 normal dejaría el aro casi vacío. Si es el rango del usuario, la
   esfera calcula el aro con sus límites, no con los del proveedor.
9. **Qué hacer si no se puede instalar por adb.** Watch Face Studio no es salida: también instala
   por adb. Las alternativas reales son una pista de pruebas internas privada de Google Play
   (requiere cuenta de desarrollador) o parar.

## 8. Lo que queda a criterio de quien construya

- Cómo se generan las agujas (script como el del fondo, o formas de WFF) y su detalle fino.
- Tamaños exactos de letra, el rojo de batería baja y su umbral si WFF no da una señal de «batería
  baja».
- Si el segundero avanza a saltos o barre de forma continua (pesa en la batería).
- La versión de WFF, una vez conocida la de Wear OS.
- La estructura del proyecto Gradle, partiendo de TouchGuard.
- Si las sub-esferas llevan textos fijos («ACTIVIDAD») además de lo que manda el proveedor.

## 9. Entorno heredado

- **Watch Face Studio 1.9.9** está extraído (no instalado) en
  `C:\Users\criso\Apps\WatchFaceStudio_1.9.9\WatchFaceStudio.exe`. Su instalador oficial se cae en
  este Windows 11 26H2 por un plugin NSIS de 2018; se sacó con
  `7z e -tnsis <instalador> '$PLUGINSDIR\app-64.7z'` y luego `7z x`. No se actualiza solo.
- **Para lanzar cualquier app Electron desde una herramienta de Claude Code** (WFS, por ejemplo)
  hay que quitar antes `ELECTRON_RUN_AS_NODE`, que se hereda de VS Code; si no, arranca como Node
  y se cierra al instante sin ventana.
- **7-Zip 26.06** instalado con winget.
