# NVC Navigator — plan de construcción

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Construir la esfera «NVC Navigator» como segundo paquete WFF instalable junto a la NVC.

**Architecture:** Módulo Gradle sin código `navigator/` con su `watchface.xml`; arte de Blender
(fondo sin contenido dinámico, agujas y agujas pequeñas como sprites con sombra) y capa ambiente
de luminiscente generada con PIL. Reutiliza `scripts/watch.sh` con `FACE=navigator`.

**Spec:** `docs/superpowers/specs/2026-11-23-navigator-design.md`

## Global Constraints

- WFF v2, 466×466, `minSdk 34`, `hasCode=false`, `applicationId com.nvc.navigator`.
- Nombres de WFF sólo los ya verificados en la NVC (documentación oficial y esquema v2).
- Tamaños de letra y `x`/`y` de agujas enteros. Validador WFF v2 en verde antes de instalar.
- Arte determinista desde scripts; nada retocado a mano.
- Commits en inglés, convencionales, sin atribución a Claude.

## Review Focus

1. Glucosa sin dato: aguja en reposo (−135°), «--» gris, sin color.
2. Glucosa fuera de escala (39, 400): aguja saturada en los extremos, no da la vuelta.
3. Batería baja: aguja de reserva en rojo.
4. Always-On: sólo luminiscente y glucosa; nada del fondo.
5. La esfera NVC sigue instalada y funcionando (paquetes distintos).

### Task 1: Módulo `navigator` y script de instalación
- [ ] `navigator/build.gradle.kts` y manifiesto copiados de `watchface/` con `namespace`/`applicationId` `com.nvc.navigator`; `include(":navigator")`.
- [ ] `scripts/watch.sh`: variable `FACE` (`watchface` por defecto, `navigator`) que decide módulo, paquete, XML y APK.
- [ ] Compila con un `watchface.xml` mínimo. Commit.

### Task 2: Arte de producción
- [ ] `make_prints.py`: `navigator_print_bg.png` sin los contenidos de muestra (iconos, temperatura).
- [ ] `navigator.py` modo `bg`: sin agujas, sin cristal, sin número de glucosa ni de fecha.
- [ ] `hands.py`/`cut_hands.py` con `--face navigator`: horaria, minutero, segundero (rojo con punta), aguja del manómetro, aguja de reserva (acero y roja), tapas; sombras.
- [ ] `art/blender/navigator_aod.py` (PIL): esfera ambiente con luminiscente de índices y escala de glucosa atenuada; agujas ambiente con su franja de luminiscente.
- [ ] `scripts/render_3d.sh navigator` deja todo en `art/out/navigator/`; comprobado determinista. Commit.

### Task 3: `navigator/src/main/res/raw/watchface.xml`
- [ ] Fondo y ambiente; reserva (aguja por `Transform angle`, roja con `BATTERY_IS_LOW`); fecha girada 45°.
- [ ] Contadores: actividad (icono con giro de tono) y tiempo, como en la NVC.
- [ ] Glucosa: aguja con `Transform angle` sobre el valor; ventana con `TEXT` y color por `Condition`; sin dato «--».
- [ ] Agujas con sombra (segundo reloj desplazado); ambiente.
- [ ] Validador en verde. Commit.

### Task 4: En el reloj
- [ ] Instalar, seleccionar, capturar; comparar con `navigator_3d.png`.
- [ ] Casos de Review Focus que se puedan forzar (proveedor falso para glucosa).
- [ ] Registro en `docs/pruebas/05-navigator.md`. Commit.
