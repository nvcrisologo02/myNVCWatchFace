# Guía para hacer una esfera nueva (lecciones de NVC, Navigator y Nocturne)

Escrita el 2026-11-23, después de construir tres esferas para el OnePlus Watch 3. Su objetivo es
que la cuarta salga en una sesión: qué preguntar, qué copiar, qué medidas ya funcionan y qué
trampas evitar. Todo lo que aquí se da por bueno **se comprobó en el reloj**. Lo que sólo se probó
en el PC lo indica.

## 1. Lo que hay que preguntar al usuario (y lo que ya se sabe)

Estas cosas ya están decididas. No hay que volver a preguntarlas:

- **Una esfera por APK.** WFF admite un solo `watchface.xml` por paquete. Cada esfera es un
  módulo Gradle propio, `com.nvc.<cara>`, que en debug lleva el sufijo `.debug`. Todas conviven
  en el reloj.
- **Glucosa:** el proveedor «rango» de Gluroo (`GlucoseRangeDataProviderService`). Llega como
  `RANGED_VALUE` con un mínimo de 20 y un máximo de 400, y su `TEXT` es «185→», con la flecha
  como último carácter. El hueco admite **sólo `RANGED_VALUE`**: con más tipos, el usuario elegía
  por error el proveedor de texto. Los colores son rojo por debajo de 70, oro de 70 a 180 y
  ámbar por encima de 180. **No se muestra la antigüedad de la lectura**: lo decidió el usuario y
  asume el riesgo.
- **Actividad:** un hueco de complicación que el usuario asigna en el reloj. OHealth
  `SportFreeTraining…` llega como `MONOCHROMATIC_IMAGE` verde; se vuelve dorado con
  `HsbFilter hueRotate="115" saturate="0.7"`. Gluroo y OHealth no definen acción de toque: el toque
  abre lo que diga el proveedor.
- **Tiempo:** un hueco de `SHORT_TEXT` con icono más temperatura.
- **Estilo del usuario:** realista, de reloj de verdad, nunca «de dibujo». Arte hecho con Blender.
  Textos **grandes**: en cada esfera pidió agrandar la fecha, la glucosa, la batería y los
  contadores. Hay que empezar ya con los tamaños de §4.
- **Zona de las 6:** el reloj pinta ahí su punto de notificaciones. No se pone nada pequeño
  (fecha, texto) entre las 5:30 y las 6:30, justo por encima del bisel.

Lo único que hay que preguntar en cada esfera nueva:

1. Qué carácter tiene o en qué reloj real se inspira (la Navigator salió de su Citizen Promaster
   BY3006-53E).
2. Qué complicación especial lleva, si alguna: fase lunar, reserva de marcha, segundo huso…
3. Cuál es la paleta: caja, esfera y agujas.

Con eso se hace **un boceto 3D** (Blender en modo boceto, con contenido de ejemplo), se enseña,
se ajusta, se escribe el diseño corto en `docs/superpowers/specs/` y se construye.

## 2. Receta: de cero a instalada

Para una cara nueva `<cara>` (minúsculas) con el prefijo de recursos `<pre>_`:

1. **Módulo Gradle.** Copiar `nocturne/` a `<cara>/` **sin** `build/` ni `res/drawable-nodpi/`.
   Cambiar `namespace` y `applicationId` en `build.gradle.kts`, `app_name` en `values/strings.xml`
   y el `include(":<cara>")` en `settings.gradle.kts`. El manifiesto ya trae `hasCode=false` y la
   propiedad `com.google.wear.watchface.format.version = 2`; no se toca.
2. **Escena de Blender:** `art/blender/<cara>.py`. Se copia `nocturne.py` como plantilla, con
   los modos boceto y `bg`. Usa `watchkit.py` (`setup`, `lathe`, `cylinder`, `torus`, `box`,
   `radial_box`, `boolean_cut`, `finish_material`, `snail_material`, `logo`, `text_obj`). Los
   impresos (números, minutería, escalas) se dibujan en 2D en `art/blender/make_prints.py` (una
   función por cara) y se proyectan desde arriba sobre la esfera.
3. **Agujas:** se añade la cara a `FACES` en `art/blender/hands.py`. `cut_hands.py` recorta los
   sprites, crea las sombras y escribe `placement.json`; no hay que tocarlo.
4. **Always-On:** `art/blender/<cara>_aod.py`. Se copia `nocturne_aod.py`: fondo negro, impresos
   al 42 % y agujas en silueta de oro tenue.
5. **Scripts:**
   - añadir un `case` en `scripts/render_3d.sh`;
   - añadir el prefijo en `scripts/sync_face.sh`;
   - añadir el paquete en `scripts/watch.sh`.
6. **XML:** `scripts/gen_<cara>_xml.py`. Se copia `gen_nocturne_xml.py`, que lee
   `placement.json` y contiene las funciones `needle`, `shadowed` y `glucose_branch`. El XML se
   genera y **nunca se edita a mano**.
7. **Ciclo:**
   ```
   scripts/render_3d.sh 256 <cara>          # ~minutos; 64 muestras para iterar rápido
   python -I scripts/gen_<cara>_xml.py
   FACE=<cara> scripts/watch.sh <serial> all <cara>-v1
   ```
   `watch.sh all` hace sync, compila, valida, instala, selecciona y captura.
8. **Registro:** `docs/pruebas/NN-<cara>.md`, con una sección por versión y su captura. Hay que
   actualizar el diseño, el CLAUDE.md (Estado) y hacer un commit por versión.

## 3. WFF: lo comprobado en el reloj (Wear OS 5, WFF v2)

| Qué | Resultado |
|---|---|
| `[COMPLICATION.RANGED_VALUE_VALUE]` en `Condition`, en `Transform` de `endAngle` y en `Transform target="angle"` de una `PartImage` | funciona: así se hacen agujas de indicador |
| Color de un trazo (`Stroke color`) con expresión | **no** en v2: un `Condition` con una rama por color |
| `Font size`, `x`, `y` de agujas y `PartImage` | deben ser **enteros** (con 12.5 falla al cargar) |
| Dos `AnalogClock` | se puede: el primero, desplazado (2, 3), lleva las sombras |
| Alfa del PNG de fondo | se respeta: un hueco transparente deja ver lo que se dibuja debajo (disco lunar) |
| `[MOON_PHASE_POSITION]` | entero 0–28, días desde la luna nueva |
| `[BATTERY_IS_LOW]` | `true` al 20 % |
| `HsbFilter` en un `MONOCHROMATIC_IMAGE` | funciona: el icono verde se vuelve oro |
| Quitar un `ComplicationSlot` | las asignaciones del usuario **se desplazan por posición**: hay que reasignar en el reloj |
| Comentarios XML | no pueden contener `--` (el validador falla) |
| Always-On | `screencap` devuelve negro: sólo se comprueba **a ojo** en el reloj |

Antes de usar un elemento, atributo o fuente de datos nuevos, hay que buscarlo en la
documentación oficial de WFF (developer.android.com/training/wearables/wff) y pasar el validador.
Los tags de Watch Face Studio no son los de WFF.

## 4. Medidas que ya funcionan (reloj de 466 px, centro 233,233)

Son el punto de partida. Todas llegaron así después de que el usuario pidiera agrandar:

| Elemento | Tamaño que se lee bien |
|---|---|
| Valor de glucosa | número de **30 px** (Bodoni) o 20 px dentro de una ventana de 44×20 o más; flecha de 20 px |
| Fecha | ventana de **32×22** como mínimo con un número de 20 px; puede ir girada (30° a las 4, 45° a las 4:30) |
| Contadores (actividad, tiempo) | **r 44** o más; el icono, a 0,5–0,6 del diámetro |
| Ventanas de texto de complicación | 66×28 con texto de 20 px |
| Indicador de glucosa | r 56–62; deja **sitio libre debajo** para el número (en la Nocturne, el número de 30 px chocó con un abanico de r 74) |
| Reserva de batería | arco de ±50–60°, radio 34–44 |
| Agujas pequeñas | **blancas o de oro**: el acero pulido y el azulado se pierden sobre esferas oscuras |

## 5. Arte: Blender

- Blender 5.3.0 portátil: `C:\Users\criso\Apps\blender-5.3.0-windows-x64\blender.exe`. HDRI
  `C:\Users\criso\.claude\tools\blender\hdri\studio_small_09_2k.hdr` (Poly Haven, CC0).
- Cámara ortográfica cenital, `ortho_scale` 46,6: **1 unidad = 10 px del reloj**. El render sale a
  932×932 (2×). `wk.W(x, y)` convierte de px del reloj relativos al centro.
- Cycles con AgX y la semilla por defecto: **determinista**, dos renders dan los mismos bytes.
- El oro pulido se ve apagado si el estudio es oscuro: subir `key_energy` o satinar (roughness
  0,3).
- Fondo con un hueco: `film_transparent = True` en modo `bg` y `round_alpha.py` en lugar del
  recorte redondo opaco.
- Las fuentes deben ser redistribuibles (OFL): Bodoni Moda y Barlow Condensed ya están en `res/font/`,
  con su licencia en `docs/licencias/`. La Bodoni MT de Windows no se puede usar.
- Las sombras de las agujas las genera `cut_hands.py` (desenfoque); en el XML se dibujan con un
  desplazamiento (1, 2) para agujas de indicador y (2, 3) para las del reloj.
- Antes de instalar, se simula en el PC lo que gira: componer el fondo y el sprite girado con PIL
  para varios valores (días de la luna 0, 9, 14,8 y 22; glucosa 40, 70, 180 y 300).

## 6. Reloj y conexión

- Serial mDNS: `adb-H631104000081G14004R-e9DEII._adb-tls-connect._tcp` (a veces con un punto
  final). Si no conecta solo: `adb mdns services`, después `adb connect <ip>:<puerto>`, y usar
  esa `ip:puerto` como serial.
- **Bluetooth del reloj apagado** mientras se trabaja; si no, el reloj suelta el Wi-Fi.
- `-s <serial>` en todo: suele estar conectado también el Pixel 8 Pro.
- Seleccionar una esfera:
  `am broadcast -a com.google.android.wearable.app.DEBUG_SURFACE --es operation set-watchface --es watchFaceId <paquete>`.
  No está documentado, pero funciona.
- Captura: hay que esperar unos 4 s tras instalar, porque si no sale la animación de cambio de
  esfera. Si hay un diálogo delante, `KEYCODE_BACK`; `KEYCODE_HOME` sobre la esfera abre el
  lanzador.
- Valores de las complicaciones sin captura:
  `adb -s <serial> logcat -d | grep DWF:WearComplicationProvider`.
- Casos de glucosa (hipo, hiper, sin dato, extremos): `fakeglucose/` y
  `scripts/glucose_cases.sh`. **Todavía no se han pasado** en ninguna esfera.

## 7. Herramientas

- Compilar: `scripts/build.bat :<cara>:assembleDebug` (fija `JAVA_HOME` al JBR de Android Studio).
- Validador oficial: `C:\Users\criso\.claude\tools\android\wff-validator.jar` (compilado desde
  google/watchface con Gradle 9.7.1, porque su Gradle 8.9 no corre sobre el JDK 25). Uso:
  `java -jar wff-validator.jar 2 watchface.xml`; tiene que decir `PASSED`.
- `gradle.properties` lleva `kotlin.stdlib.default.dependency=false` (AGP 9 metía 2,4 MB de
  Kotlin en un paquete sin código).
- Tests del arte: `python -m pytest art/tests`, **sin** `-I`.
- Heredocs largos o `sed` con barras invertidas fallan en git-bash: se escribe un script con
  Write y se ejecuta.

## 8. Errores que no hay que repetir

1. Empezar con textos pequeños. El usuario siempre pidió más grande; hay que usar §4 desde el
   principio.
2. Poner la fecha a las 6, donde está el punto de notificaciones.
3. Usar agujas de acero o azuladas sobre una esfera oscura: no se ven en el reloj.
4. Dejar que el indicador y el número compitan por el mismo sitio. Hay que reservar el hueco del
   número primero y ajustar el arco después.
5. Admitir varios tipos de complicación en el hueco de glucosa.
6. Quitar un hueco sin avisar de que hay que reasignar las complicaciones en el reloj.
7. Dar algo por bueno sin una captura del reloj. Compilar y validar no basta.
8. Retocar PNG o XML a mano: todo sale de los scripts.
