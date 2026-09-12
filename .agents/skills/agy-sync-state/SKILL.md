---
name: agy-sync-state
description: Sincronizar estado autorizado desde Plane al sprint y reconciliar eventos de QA para el responsable operativo (Scrum manual o Automation) en agyFlow, con n8n solo si el proyecto lo utiliza.
---

# Sincronización y reconciliación

Las rutas mencionadas son relativas a la raíz del proyecto receptor.
Aplicá `docs/protocolo.md` para propiedad del espejo, claves de eventos y estados.
Usá `templates/sprint_actual.md` como referencia de la proyección local.

## Procedimiento

1. Confirmá quién escribe el espejo, alcance autorizado y conexión de Plane.
   Descubrí herramientas, campos y estados remotos reales. Las claves del
   protocolo son convenciones documentales, no un esquema supuesto de su API.
2. Leé el estado remoto antes de generar la proyección local y registrá fecha
   y referencias. Si la lectura es parcial, no sustituyas un espejo completo
   por ese resultado ni lo marques como una sincronización exitosa.
3. Antes de mutar un ticket por un evento de QA, identificá su revisión e ID de
   ejecución, comprobá el historial y releé su estado. Reconciliá eventos
   pendientes y cambios concurrentes antes de aplicar una nueva transición.
   Un dictamen de otra revisión o ejecución QA anterior queda en historial
   sin efectos sobre el estado vigente. Otro ID de ejecución no cuenta como reapertura sin nueva entrada a QA.
4. Tratá un reintento como continuación del mismo evento. Si una herramienta
   agotó el tiempo, consultá si la mutación se aplicó antes de repetirla.
   Si la lectura tampoco permite determinarlo, conservá el pendiente y reportalo.
   Registrá aprobado con su revisión y cierre de secuencia; rechazado cuenta
   una reapertura por ejecución distinta; bloqueado conserva el contador.
   Al tercer rechazo, registrá escalado y detené reasignaciones automáticas.
5. Actualizá el espejo completo de forma atómica solo desde datos remotos
   confirmados. Si no hay conectividad, preservá la última sincronización exitosa
   y reportá el fallo sin inventar IDs ni confirmar transiciones.
6. Si se usa n8n, verificá herramientas y credenciales disponibles antes de
   construir el workflow. Validá su lógica con eventos controlados dentro del
   alcance permitido; crear un JSON no demuestra que se haya ejecutado en remoto.
7. Entregá resultado de sincronización, eventos aplicados o pendientes y la
   evidencia de reconciliación. Las notificaciones requieren canal autorizado;
   una entrega en la sesión no debe presentarse como mensaje externo enviado.

## Ejemplo de respuesta ambigua

Tras un timeout al registrar una reapertura, buscá la clave del mismo evento.
Si ya está aplicado, reflejá su resultado sin incrementar otra vez el contador.
Si no podés verificarlo, reportá la operación pendiente para reconciliación.

El contador y escalado siguen el protocolo. Esta skill no activa correcciones
ni instala un motor de automatización cuando el proyecto no lo haya elegido.
