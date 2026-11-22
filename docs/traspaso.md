# Traspaso de la sesión de diseño (2026-11-22)

El proyecto nació en una sesión de Claude Code abierta en otro repo (`yi-camaras`). Este
documento recoge lo que pasó allí y que no está en el diseño: el porqué de algunas decisiones y
las pruebas que ya se hicieron. Lo vigente es el diseño; esto es contexto.

## Cronología de decisiones

1. **Punto de partida.** El usuario quería hacer una esfera con Samsung Watch Face Studio, a
   partir de una referencia negra y dorada con mapamundi
   (`docs/referencias/01-referencia-inicial.png`).
2. **El reloj no es Samsung.** Es un OnePlus Watch 3. Se comprobó que Watch Face Studio sigue
   valiendo (exporta Watch Face Format), que el lienzo de WFS es fijo de 450×450 y que no se puede
   fijar desde la esfera qué app abre un toque.
3. **Contenido.** Fuera el logo de la referencia; la sub-esfera de hora digital y pasos se cambia
   por la **glucosa** (el usuario es diabético y ya la ve en su esfera actual); y hace falta un
   botón para empezar actividades de OHealth.
4. **Maqueta v1:** mapa de puntos, botón de actividad donde iba el logo, tres sub-esferas abajo.
5. **v2:** el usuario aporta su propia esfera base (`02-esfera-base-usuario.jpg`) y su logo
   (`03-logo-nvc-original.jpg`). Pide relieve coherente (en su render unos continentes estaban en
   relieve y otros hundidos), oro en las horas, el logo arriba y **sólo tres sub-esferas**. Se
   regenera el mapa desde datos geográficos reales con una única luz. La fecha y la batería pasan a
   ventanas a las 3 y a las 9 porque no necesitan complicación.
6. **v3:** pide probar el mapa en **bajo relieve** y una sub-esfera central más grande, montada sobre
   las otras dos. La glucosa pasa al centro (propuesta aceptada).
7. **v4 (cerrada):** bajo relieve, logo un 25 % más pequeño. Las agujas y el Always-On de la
   maqueta se dan por buenos.
8. **Cómo construirla:** se descartó montarla a mano en Watch Face Studio y se eligió escribir el
   Watch Face Format directamente y compilarlo con el SDK de Android, para poder iterar sobre el
   reloj real sin depender de clics.

## Pruebas y hallazgos que no conviene repetir

- **Watch Face Studio no se instala en este PC.** El instalador oficial 1.9.9 (firma de Samsung
  válida, descarga íntegra) muere a los 3,3 s con `0xc0000005` en el `System.dll` de NSIS, un
  plugin compilado el 2018-12-15, en Windows 11 26H2. Se descartaron, cada uno con su prueba, la
  descarga corrupta, el antivirus, Exploit Protection y los modos de compatibilidad. Es una app
  Electron empaquetada con electron-builder; se extrajo con 7-Zip y funciona. Detalle en el
  diseño, §9.
- **En esa prueba apareció la trampa de `ELECTRON_RUN_AS_NODE`** (ver `CLAUDE.md`), que hacía
  parecer roto un WFS que estaba bien.
- **El relieve se hace con un único mapa de alturas y una única luz**, no pieza a pieza. Así
  ningún elemento contradice a otro, que era justo el defecto del render del usuario.
- **El detalle de costa de Natural Earth es excesivo a escala de reloj.** Sin simplificar, el
  archipiélago ártico canadiense e Indonesia se veían como un enjambre de gotas brillantes. Por eso
  existen `MIN_ISLAND` y `COAST_SMOOTH` en el generador.
- En bajo relieve, el brillo fuerte de las paredes parecía cromado líquido; se rebajó a un bisel
  satinado.

## Para la primera sesión en este repo

Pega esto como primer mensaje:

> Lee `CLAUDE.md` y el diseño en `docs/superpowers/specs/`. Vamos a planificar la construcción de
> la esfera: empieza por la prueba de instalación en el OnePlus Watch 3, que es el riesgo nº 1.
