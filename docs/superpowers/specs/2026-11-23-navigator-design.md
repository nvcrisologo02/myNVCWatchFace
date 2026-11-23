# Esfera «NVC Navigator» — diseño

Fecha: 2026-11-23 · Estado: pendiente de aprobación del usuario.
Boceto aprobado como dirección: `docs/mockup/propuestas/navigator_3d.png`.

## 1. Intención

Una **segunda esfera** para el OnePlus Watch 3, para alternar con la NVC actual. Cronógrafo de
piloto clásico inspirado en el Citizen Promaster del usuario (BY3006-53E): bisel de acero con
escala de 24 horas, esfera antracita con acabado sol, índices de acero con luminiscente. Lo que el
usuario pide por encima de todo: **que parezca un reloj, no un dibujo**. Por eso todo el arte sale
de Blender, como el fondo actual desde hoy.

Mantiene lo práctico de la NVC: glucosa de un vistazo, también en Always-On, y un toque para
empezar un entrenamiento.

## 2. Objetivos, no objetivos y anti-objetivos

**Objetivos**
- Reproducir el boceto 3D en el reloj real, con el mismo realismo.
- Glucosa legible al instante: aguja sobre un manómetro con zonas de color y el número en una ventana.
- Instalable junto a la NVC (otro paquete), elegible desde el selector del reloj.

**No objetivos**
- Personalización por el usuario (colores, estilos).
- Escala de 24 horas funcional (el bisel es decorativo, como un bisel fijo).

**Anti-objetivos** (heredados de la NVC)
- Un valor de glucosa que parezca actual sin serlo. Igual que en la NVC, el usuario aceptó no
  mostrar la antigüedad (diseño NVC §10); la aguja y el número vienen de la misma complicación.
- Que la glucosa no se lea en Always-On.
- Gastar claramente más batería que la NVC.

## 3. Restricciones

Las mismas que la NVC (diseño NVC §3): Wear OS 5.0, **WFF v2**, 466×466, instalación por adb,
complicaciones de terceros admitidas. Lo aprendido en el reloj que aplica aquí:

- En v2 el color de un trazo no admite expresiones: los colores por rango van en ramas de
  `Condition` (ya funciona en la NVC).
- `[COMPLICATION.RANGED_VALUE_VALUE]` funciona dentro de `Condition` y `Transform` (comprobado).
- Gluroo manda rango 20–400 y en `TEXT` la glucosa con la flecha («185→»).
- El hueco de glucosa sólo admite `RANGED_VALUE`.
- Tamaños de letra enteros; `x`/`y` de las agujas enteros.
- Sombra de agujas: segundo `AnalogClock` desplazado (funciona en la NVC).

## 4. Enfoques considerados

- **A · Arte 3D en Blender + capas dinámicas WFF** (como la NVC desde hoy). El fondo lleva todo lo
  fijo; encima van agujas renderizadas, aguja del manómetro, número de glucosa, fecha e iconos.
- **B · Dibujar el manómetro y la reserva con formas de WFF** (arcos y líneas). Más ligero, pero
  se ve plano, justo lo que el usuario rechaza.

**Elegido: A.** Es lo que da el aspecto de reloj y la tubería ya existe.

## 5. Diseño

Coordenadas en píxeles del reloj, centro (233, 233), y hacia abajo.

| Elemento | Posición y medidas | Origen |
|---|---|---|
| Bisel 24 h | anillo r 212,5–233, acero cepillado, números grabados en negro | fondo 3D |
| Rehaut (minutería) | anillo inclinado r 196–211,5, negro mate con minutos en blanco | fondo 3D |
| Esfera | r ≤ 196, antracita con acabado sol; mapa en acero satinado con relieve | fondo 3D |
| Índices | acero pulido aplicado con luminiscente; doble a las 12; cortos a las 3 y 9 | fondo 3D |
| Logo NVC | (233, 111), 60 de ancho, oro aplicado; «NAVIGATOR» debajo | fondo 3D |
| **Reserva de marcha = batería** | pivote (233, 203), arco −50°…+50°, r 26–33, 0 y 100 | escala en el fondo; aguja dinámica |
| Contador 9 h · actividad | centro (138, 233), r 42, hundido con caracoleado, aro de acero | fondo; icono por complicación |
| Contador 3 h · tiempo | centro (328, 233), r 42 | fondo; icono + temperatura por complicación |
| **Contador 6 h · glucosa** | centro (233, 328), r 48; escala 40–300 en 270° (−135°…+135°); zonas rojo < 70, oro 70–180, ámbar > 180; marcas 70 y 180 | escala en el fondo; aguja y número dinámicos |
| Ventana de glucosa | (233, 354), 34×16, marco de acero; número + flecha, color por rango | dinámica |
| Fecha | ventana a las 4:30, r 160, 24×16 girada 45°, disco blanco con el día | ventana en el fondo; número dinámico girado |
| Agujas | espada de acero facetado con luminiscente: horaria hasta r 118, minutero r 176; segundero rojo fino con punta redonda | 3D, sprites con sombra |

**Glucosa:** la aguja del manómetro gira con
`angle = -135 + 270 * (clamp(v, 40, 300) - 40) / 260` (se satura en los extremos). El número de
la ventana usa el `TEXT` de la complicación («148→») con color por `Condition`: rojo < 70,
ámbar > 180, oro en rango. Sin dato: aguja en reposo a −135°, ventana con «--» en gris.

**Batería:** aguja de la reserva con `angle = -50 + clamp(BATTERY_PERCENT, 0, 100)`; en rojo
cuando `BATTERY_IS_LOW`.

**Always-On** («como un reloj a oscuras»): negro, sólo brilla en verde el luminiscente de índices
y agujas; además la escala de glucosa atenuada, su aguja y el número con su color. Fuera: fondo,
bisel, mapa, contadores laterales, fecha, segundero.

**Toques:** actividad y tiempo por sus complicaciones; la glucosa no abre nada (Gluroo no define
acción).

## 6. Construcción

1. Módulo Gradle nuevo `navigator/`, sin código, `applicationId` `com.nvc.navigator`
   (debug `.debug`), mismo manifiesto que `watchface/`.
2. Arte: `art/blender/navigator.py` pasa de boceto a producción: render del fondo **sin**
   agujas ni contenido dinámico (sin icono, temperatura, número de glucosa ni fecha); agujas y
   aguja del manómetro con `hands.py`/`cut_hands.py` generalizados; capa ambiente de luminiscente
   renderizada aparte. Todo desde `scripts/render_3d.sh navigator`.
3. `navigator/src/main/res/raw/watchface.xml` a mano, reutilizando los bloques de la NVC
   (complicaciones, `Condition` de glucosa, batería, sombras).
4. `scripts/watch.sh` acepta qué esfera compilar e instalar.

## 7. Riesgos

1. `Transform target="angle"` sobre una `PartImage` con el valor de una complicación: no probado
   (el `endAngle` de un arco sí). Si falla, la aguja del manómetro se hace con un `Arc` fino.
2. El texto de fecha girado 45°: `PartText` admite `angle`; comprobar que se ve nítido.
3. Batería y fluidez con dos relojes (sombras) y más capas.
4. Always-On sin poder capturarlo (ver prueba 4 de la NVC): validación a ojo del usuario.

## 8. A criterio de quien construya

- Tamaños exactos de letra y el rojo/ámbar exactos (mismos que la NVC salvo motivo).
- Si el segundero barre o salta.
- Cómo se ilumina el render para que el acero no quede apagado (lo visto en los bocetos).
