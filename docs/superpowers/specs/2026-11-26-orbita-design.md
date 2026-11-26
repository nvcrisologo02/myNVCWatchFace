# Esfera «NVC Órbita» — diseño

Fecha: 2026-11-26 · Estado: pendiente de aprobación del usuario (preguntas del revisor respondidas el mismo día).
Diseño del usuario: `docs/referencias/orbita-referencia.png`. Boceto aprobado (2026-11-26):
`docs/mockup/propuestas/orbita_3d.png` y los cinco colores en `docs/mockup/propuestas/orbita_colores.png`.

## 1. Intención

**Cuarta esfera**, fiel a un diseño que hizo el propio usuario: reloj deportivo de acero con un
globo plateado en relieve, un satélite y un anillo de color. Respecto a su imagen cambian tres
cosas:

- la batería pasa a donde estaban las calorías;
- la glucosa ocupa la sub-esfera central, donde estaba la batería;
- el color del anillo **se elige en el reloj** (verde, naranja, rojo, amarillo, azul…).

Como las otras esferas, tiene que parecer un reloj de verdad, con el arte hecho en Blender. Lo que
más pesa es la fidelidad a su diseño: el usuario corrigió cada desviación del boceto. **La
comparación se hace superponiendo imágenes, no mirándolas lado a lado.**

## 2. Objetivos, no objetivos y anti-objetivos

**Objetivos**
- Reproducir el boceto aprobado en el reloj.
- Ofrecer el color del anillo en «Personalizar», con cinco opciones de partida.
- Mostrar la glucosa grande y legible, en Always-On también.
- Mostrar la batería con icono y valor, los pasos y las pulsaciones en la banda.
- **Progreso de pasos:** la marca naranja recorre las barras según el porcentaje del objetivo diario.
- **Entreno de un toque:** tocar los pasos abre lo que el usuario asigne (OHealth, entrenamiento libre).
- Instalarse junto a las otras tres esferas, con paquete propio.

**No objetivos**: tendencia de la glucosa (el usuario no la quiere); escala o indicador de
glucosa (sólo el valor); calorías; **el tiempo** (no hay sitio en su diseño; decidido el 2026-11-26);
cambiar qué dato muestra la banda (pasos y pulsaciones son fijos).

**Anti-objetivos** (heredados): una glucosa vieja que parezca actual; una glucosa ilegible en
Always-On; gastar claramente más batería.

## 3. Restricciones

Las de las esferas anteriores (guía `docs/guia-nueva-esfera.md` §3 y §4): WFF v2, 466×466,
colores por `Condition`, tamaños y posiciones enteros, glucosa sólo como `RANGED_VALUE` de
Gluroo y nada pequeño entre las 5:30 y las 6:30. Novedades de esta esfera, comprobadas en la
documentación oficial:

- **Color elegible:** `<UserConfigurations><ColorConfiguration id="colorAnillo" …>` con
  `<ColorOption id colors="#AARRGGBB">`, de 1 a 100 opciones (Wear OS 4 o posterior). Se aplica
  con `tintColor="[CONFIGURATION.colorAnillo]"` en un `PartImage`.
- **Texto curvado:** existe `TextCircular` (Wear OS 4, ángulo 0 = 12 h, `direction` CLOCKWISE o
  COUNTER_CLOCKWISE). La documentación **no confirma** que se pueda usar dentro de una
  complicación (ver §7, riesgo 1).

## 4. Enfoques considerados (color del anillo)

- **A · Capa del anillo teñida por el reloj (elegido por el usuario).** El fondo lleva los
  sectores de color en plata neutra. Encima va un PNG sólo con los sectores, renderizado en
  blanco y gris con todo su sombreado, teñido con `tintColor`. El tinte multiplica, así que se
  conservan brillos y relieve. Una sola imagen sirve para todos los colores y añadir uno cuesta
  una línea.
- **B · Un fondo completo por color**, cambiado con `ListConfiguration`. Es el más realista,
  pero la documentación no explica cómo cambiar imágenes con él, pesa cinco veces más y cada
  color nuevo obliga a renderizar otro fondo. **Plan de reserva** si el tinte de A queda
  claramente peor.

## 5. Diseño

Coordenadas en píxeles del reloj relativas al centro (233, 233), con y hacia abajo. Las medidas
salen de superponer el boceto con la imagen del usuario (`art/blender/build/orbita_ref_grid.png`).

| Elemento | Posición y medidas | Origen |
|---|---|---|
| Reborde | gris moleteado (una raya por grado), r 226–233, filete pulido hacia dentro | fondo 3D |
| Banda | plata cepillada, r 200–226; **sectores de color** de 50° a 130° y de 230° a 310° | fondo 3D + capa teñida |
| Números | 2, 3, 4, 8, 9, 10 radiales en blanco sobre el color; «6» derecho en tinta oscura; Barlow Condensed 28 px a r 213, con sombra | fondo |
| Barras de pasos | grises, cada 2° de −14° a 54°, r 204–223 | fondo |
| Marca de progreso | naranja, r 201–226, 5 px; ángulo `−14 + 68 · clamp(porcentaje, 0, 100) / 100` | sprite dinámico |
| Zona oscura | negro mate, r 170–200, índices blancos r 180–193 (a las 12, r 177–196) | fondo |
| Globo | semiesfera r 170 en una ventana con filete pulido; costas vectoriales (Natural Earth) en **Mercator plano** encajado sobre la imagen del usuario (`OB_MAP` en `make_prints.py`) y abombado hacia el borde; tierra blanca martillada en relieve; mar laca negra | fondo |
| Satélite | PNG del usuario (`docs/referencias/satelite.png`) pasado a blanco y colocado (`art/satellite_sprite.py`, rotación 218°, 190 px, centro (112, 8)), con sombra | fondo |
| Sub-esfera de glucosa | centro (0, 134); aro plata con 36 rayas, r 46–62; disco negro r 46 | fondo |
| **Valor de glucosa** | centrado en (0, 134), Barlow Condensed **48 px**, sin flecha; blanco de 70 a 180, rojo por debajo de 70, ámbar por encima de 180; «--» gris sin dato | dinámico |
| Pasos | zapatilla + número a las 10:30 (centro en −33°), 28 px, tinta oscura, curvado; **dato del reloj** | dinámico |
| Toque de entreno | hueco de complicación **invisible** sobre la zona de los pasos; sólo recoge el toque y abre lo que el usuario asigne (por defecto vacío; él pone OHealth entrenamiento libre) | XML |
| **Batería** | icono de pila + «80%» centrado a las 7 (206°), 28 px, curvado; icono y texto rojos con batería baja | dinámico |
| Pulsaciones | «89 BPM» centrado a las 5 (149°), 28 px, curvado; **dato del reloj**; «--» sin lectura | dinámico |
| Agujas | blancas, hombro ancho junto al centro que se estrecha a un vástago hueco con punta redonda; horaria L 144, minutero L 200; contorno negro fino | 3D, sprites con sombra |
| Segundero | naranja fino, L 221, cola 43; tapa naranja r 8 con punto blanco | 3D, sprites |

**Color del anillo:** `ColorConfiguration` `colorAnillo` con verde (predeterminado), naranja,
rojo, amarillo y azul. Los valores de partida son los de `RING_COLOURS` en `orbita.py`, pasados
a sRGB y ajustados mirando el tinte en el PC.

**Pasos y pulsaciones:** fuentes de datos de la plataforma, no complicaciones (decisión del usuario,
2026-11-26). Los nombres exactos (pasos, objetivo o porcentaje, pulso) **se comprueban en la
documentación de fuentes de datos de WFF antes de usarlos** (regla 3). Si el pulso pide permiso, se
declara en el manifiesto y se acepta en el reloj.

**Glucosa:** `round([COMPLICATION.RANGED_VALUE_VALUE])` con una rama de `Condition` por color.
Hueco sólo `RANGED_VALUE`; proveedor por defecto el de rango de Gluroo.

**Always-On:** fondo negro. Se ven en tono tenue los números, los índices, el contorno del globo
y los continentes al 30 %, y las agujas en silueta blanca tenue. La glucosa se ve con su color.
Fuera: banda, barras, marca de progreso, satélite y segundero.

## 6. Construcción

Receta de la guía (§2):

- **Módulo:** `orbita/` (`com.nvc.orbita`, prefijo de recursos `orb_`).
- **Arte:** `scripts/render_3d.sh 256 orbita` produce:
  - el fondo de producción sin contenido dinámico;
  - la capa de sectores en blanco y gris;
  - los sprites de las agujas: `shoulder_hand` pasa de `orbita.py` a `hands.py`;
  - el modo ambiente.
- **XML:** `scripts/gen_orbita_xml.py`; nunca se edita a mano.
- **Instalación:** `FACE=orbita scripts/watch.sh`.

El boceto actual (`orbita.py` sin `bg`) es la referencia visual.

## 7. Riesgos

1. **Texto curvado.** Pasos, batería y pulsaciones son datos de la plataforma, así que
   `TextCircular` va fuera de complicaciones. Si aun así no se ve bien en el reloj: texto recto
   girado al ángulo de su posición.
2. **Fuentes de pasos y pulso:** si alguna no existe en WFF v2 o no da valor en el OnePlus, se
   vuelve a preguntar al usuario (complicación asignable como alternativa).
3. **Tinte del anillo:** multiplicar puede apagar los colores claros (amarillo). Se compara en el
   PC contra los renders por color antes de instalar. Si queda claramente peor, se pasa a B.
4. **Contraste de las agujas blancas sobre la tierra blanca:** el contorno negro y la sombra
   deberían bastar. Se comprueba en el reloj.
5. **Always-On:** sólo se puede verificar a ojo.

## 8. A criterio de quien construya

- Tonos finos de cada color.
- Iconos dibujados de zapatilla y pila.
- Si el segundero barre o salta.
- Tamaño exacto del grano martillado.
