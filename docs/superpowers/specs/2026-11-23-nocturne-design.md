# Esfera «NVC Nocturne» — diseño

Fecha: 2026-11-23 · Estado: pendiente de aprobación del usuario.
Boceto aprobado como dirección: `docs/mockup/propuestas/nocturne_3d.png`.

## 1. Intención

**Tercera esfera** para alternar con la NVC y la Navigator: un reloj de vestir clásico pensado
desde cero alrededor del «zZz» del logo (el sueño, la noche). Caja de oro pulido, esfera azul
noche con guilloché, números romanos, **fase lunar real** y agujas Breguet de oro. Como las
otras dos: que parezca un reloj, no un dibujo; arte de Blender. Mantiene la glucosa de un
vistazo (también en Always-On) y el toque para entrenar.

## 2. Objetivos, no objetivos y anti-objetivos

**Objetivos**
- Reproducir el boceto 3D en el reloj, con la luna moviéndose según la fase real.
- Glucosa legible: aguja de acero azulado en un abanico (retrógrado) y el número debajo, con
  color por rango.
- Instalable junto a las otras dos (paquete propio).

**No objetivos**: personalización; segundero en Always-On.

**Anti-objetivos** (heredados): glucosa vieja que parezca actual (sin antigüedad, decisión del
usuario, diseño NVC §10); glucosa ilegible en Always-On; gastar claramente más batería.

## 3. Restricciones

Las de la NVC y la Navigator (WFF v2, 466×466, colores por `Condition`, `Transform angle`
comprobado, sólo `RANGED_VALUE` en la glucosa, tamaños enteros). Nuevo aquí:

- **Fase lunar:** `[MOON_PHASE_POSITION]`, entero 0–28, días desde la última luna nueva
  (versión 1; developer.android.com/training/wearables/wff/common/attributes/source-type).

## 4. Enfoques considerados

- **A · Disco lunar clásico detrás de una apertura** (elegido). Un disco azul con estrellas y dos
  lunas opuestas gira media vuelta por ciclo, detrás de una ventana con las dos «jorobas»
  doradas que tapan la luna en luna nueva. Es el mecanismo real de los relojes con fase lunar.
  Necesita que el fondo tenga un hueco transparente en la apertura y que el disco se dibuje
  debajo.
- **B · Ocho imágenes de la luna** (una por `MOON_PHASE_TYPE`). Más fácil, pero no es como funciona
  un reloj y salta de golpe.

## 5. Diseño

Coordenadas en píxeles del reloj, centro (233, 233), y hacia abajo.

| Elemento | Posición y medidas | Origen |
|---|---|---|
| Caja / bisel | oro amarillo pulido, r 213–233, perfil redondeado | fondo 3D |
| Esfera | azul noche lacado; **clous de Paris** en el centro (r < 150); anillo de horas liso r 150–213 con filete de oro en r 150 | fondo 3D |
| Números | romanos Bodoni Moda impresos en oro a r 178 (sin VI, que es la fecha; **III y IX añadidos el 2026-11-23**: caben fuera de los contadores); minutería de vía de tren r 202,6–209 | fondo 3D |
| **Fase lunar** | **ventana concéntrica con la esfera** (2026-11-23, a petición del usuario): franja r 100–140 alrededor del centro, ±40°, cerrada por dos jorobas de oro r 22 en sus extremos; disco detrás que gira alrededor del centro del reloj, con dos lunas r 17 a r 120 | fondo con hueco + disco dinámico |
| Logo NVC | (233, 191), 54 de ancho, oro | fondo 3D |
| Contador 9 h · actividad + reserva | centro **(141, 243), r 44** (agrandado el 2026-11-23; era (143, 241), r 36), hundido con caracoleado, aro de oro; arco de reserva −60°…+60° arriba; icono abajo | fondo; icono y aguja dinámicos |
| Contador 3 h · tiempo | centro **(325, 243), r 44** (agrandado el 2026-11-23) | fondo; icono + temperatura dinámicos |
| **Glucosa** | abanico retrógrado con pivote **(233, 265), r 62** (compactado el 2026-11-23 para que no choque con el valor de 30 px; era (233, 273), r 74), de 40 (a 240°) a 300 (a 120°); zonas rojo < 70, oro 70–180, ámbar > 180; marcas 70 y 180 | escala en el fondo; aguja azulada dinámica |
| Valor de glucosa | (233, 359), número Bodoni **30 px** (era 20) + flecha de 20 px; color por rango; «mg/dL» impreso debajo | dinámico |
| Fecha | **ventana a las 4** en el anillo de horas, (387, 322), **32×22** girada 30°, número de 20 px (agrandada el 2026-11-23; era 22×16), en lugar del IIII (2026-11-23: a las 6 chocaba con el punto de notificaciones del reloj); el VI vuelve | ventana en el fondo; número dinámico |
| Agujas | Breguet de oro (anillo «pomme» cerca de la punta): horaria hasta r 112, minutero r 172; segundero de oro fino | 3D, sprites con sombra |

**Fase lunar:** el disco gira `angle = 90 + [MOON_PHASE_POSITION] * 180 / 29.53` (media vuelta por
lunación): en luna nueva las lunas están a las 3 y las 9, fuera de la ventana; la creciente entra
por la joroba izquierda, la llena queda a las 12 y la menguante sale por la derecha.

**Glucosa:** aguja con `angle = 240 - 120 * (clamp(v, 40, 300) - 40) / 260` (se satura en los
extremos). Número `round(v)` + último carácter del `TEXT` (flecha), con `Condition` de color.
Sin dato: aguja en 240° (reposo) y «--» en gris.

**Batería:** aguja de la reserva `angle = -60 + 1.2 * clamp(BATTERY_PERCENT, 0, 100)`, roja con
`BATTERY_IS_LOW`.

**Always-On:** negro; números romanos, minutería, aro de la apertura y luna en oro tenue; agujas
en contorno de oro tenue; escala de glucosa atenuada, su aguja y el número con su color. Fuera:
guilloché, contadores, fecha, segundero.

## 6. Construcción

Como la Navigator: módulo `nocturne/` (`com.nvc.nocturne`), arte con
`scripts/render_3d.sh 256 nocturne` (fondo de producción con el hueco de la apertura en alfa,
disco lunar, agujas Breguet, aguja azulada, agujas de reserva, ambiente), XML generado con
`scripts/gen_nocturne_xml.py`, instalación con `FACE=nocturne scripts/watch.sh`.

## 7. Riesgos

1. Fondo con transparencia (hueco de la apertura) sobre el disco lunar: comprobar que el
   reloj respeta el alfa del PNG de fondo.
2. Contraste de la aguja azulada sobre el azul noche (en el boceto apenas se veía): si no se lee,
   aguja de oro o azul más claro con filo pulido.
3. Oro pulido apagado si el estudio queda oscuro (visto en los bocetos): satinar.
4. Always-On sólo verificable a ojo.

## 8. A criterio de quien construya

Tamaños finos de letra, tono exacto del azul, si el segundero barre o salta.
