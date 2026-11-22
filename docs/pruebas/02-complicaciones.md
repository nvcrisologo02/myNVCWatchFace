# Prueba 2 · Inspección de complicaciones (en curso, 2026-11-23)

**Estado: a medias.** Se conocen los proveedores y sus tipos; falta leer el contenido exacto que
manda cada uno (texto, mín/máx, tendencia, formato de la antigüedad).

## Hallazgo principal

**Gluroo tiene un proveedor de antigüedad de la lectura** (`BglTimeSinceProviderService`). La
decisión del diseño §5.5 (segunda complicación para la antigüedad) es viable y la glucosa no se
bloquea.

## Proveedores de Gluroo (`com.gluroo.app`, del manifiesto de su APK)

| Servicio (`com.gluroo.app.dev.providers.…`) | Tipos declarados |
|---|---|
| `GlucoseRangeDataProviderService` | SHORT_TEXT, LONG_TEXT, **RANGED_VALUE** |
| `BglRangeDataProviderService` | SHORT_TEXT, LONG_TEXT, **RANGED_VALUE** |
| `GlucoseDataProviderService`, `GlucoseAltDataProviderService`, `BglDataProviderService` | SHORT_TEXT, LONG_TEXT |
| **`BglTimeSinceProviderService`** | SHORT_TEXT, LONG_TEXT |
| `BglTimeDeltaProviderService` | SHORT_TEXT, LONG_TEXT |
| `BigBglImageComplicationProviderService`, `TirImageComplicationProviderService` | LARGE_IMAGE, SMALL_IMAGE |
| `Chart…ComplicationProviderService` (cuatro) | SMALL_IMAGE (y LONG_TEXT/LARGE_IMAGE uno) |
| `IOB…`, `COB…` | SHORT_TEXT, LONG_TEXT (y RANGED_VALUE los no «Alt») |

## Entrenamientos de OHealth (`com.heytap.wearable.sports`)

Un proveedor por deporte: `SportFreeTrainingComplicationService`, `SportOutDoorRunComplicationService`,
`SportInDoorRunComplicationService`, `SportOutDoorWalkComplicationService`, natación, bici,
elíptica, remo, etc. El que el usuario asignó en la prueba (`SportFreeTraining…`) llegó como
**MONOCHROMATIC_IMAGE**.

## Lo que se vio en el logcat del motor (`DWF:WearComplicationProvider`)

Asignación hecha por el usuario en la esfera de inspección:

| Hueco | Proveedor | Tipo recibido |
|---|---|---|
| 1 | rango de glucosa de Gluroo | RANGED_VALUE |
| 2 | tiempo desde la lectura de Gluroo | SHORT_TEXT |
| 3 | `BigBglImageComplicationProviderService` | SMALL_IMAGE (no es la de texto que se pidió) |
| 4 | `SportFreeTrainingComplicationService` | MONOCHROMATIC_IMAGE |

El usuario confirma que en el reloj los cuatro huecos se ven con datos.

## Cómo seguir

1. Conectar el reloj y usar **siempre el serial mDNS**
   `adb-H631104000081G14004R-e9DEII._adb-tls-connect._tcp.`: la IP cambia (.85, .88) y el puerto
   también; el serial no.
2. **Apagar el Bluetooth del reloj** mientras se trabaja: con el móvil cerca, Wear OS suelta el
   Wi-Fi cada pocos minutos y adb queda «offline».
3. Leer los valores con
   `adb -s <serial> logcat -d | grep DWF:WearComplicationProvider` (trae TEXT, TITLE y valores)
   y capturar con la pantalla encendida (la captura de las 00:08 salió negra con la esfera no
   visible).
4. Reasignar el hueco 3 a la glucosa en texto de Gluroo.
5. Completar este documento: texto exacto de cada campo, mín/máx del rango, cómo llega la
   tendencia y el formato de la antigüedad («3 min», «3m»…). Después restaurar `watchface.xml`.
