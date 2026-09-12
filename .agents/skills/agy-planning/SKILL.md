---
name: agy-planning
description: Descomponer un PRD aprobado en tareas y dependencias para el Scrum Master de agyFlow, preparar la planificación en Plane y el espejo inicial del sprint.
---

# Planificación con dependencias

Las rutas mencionadas son relativas a la raíz del proyecto receptor.
Aplicá `docs/protocolo.md`; usá `templates/sprint_actual.md` para el espejo
inicial. Esta skill no amplía el acceso del rol al código de la aplicación.

## Procedimiento

1. Extraé historias y criterios de la revisión aprobada del PRD. Vinculá cada
   tarea a un resultado comprobable y evitá tareas sin criterio de terminación.
2. Separá decisiones de diseño, definición de contratos, implementación y
   verificación cuando produzcan entregas que otro rol deba consumir. Incluí
   preparación de build/CI y pruebas antes de fijar la revisión candidata.
3. Pedí a los roles técnicos las rutas y estimaciones que falten; no leas
   `apps/`, `packages/` ni directorios de backend para inferirlas.
4. Construí dependencias según la entrega necesaria: contrato publicado,
   referencia visual o tokens. Marcá una dependencia no aplicable con motivo.
   Dos tareas pueden correr juntas solo si sus entradas están disponibles y
   sus rutas de escritura no se superponen.
5. Con acceso y alcance autorizados en Plane, descubrí las herramientas y los
   identificadores reales de proyecto, ciclo y estado antes de usarlos.
   Buscá la clave documental `proyecto:historia:tarea` antes de crear un ticket.
6. Incorporá criterios, responsable, dependencias y rutas confirmadas al ticket.
   Referenciá las evidencias de entrega; no copies una señal de listo sin revisión.
7. Generá el espejo inicial desde la lectura remota confirmada y registrá la
   elección humana del responsable de estado: Scrum manual o Automation. Si
   te corresponde el modo manual, leé `.agents/skills/agy-sync-state/SKILL.md`.
   La asignación incluye espejo, transiciones, contador y reconciliación. Sin acceso a Plane,
   entregá el desglose documental como borrador, sin IDs remotos inventados.

## Ejemplo de desglose

Para una historia con nueva interacción y datos, proponé entregas separadas de
diseño y contrato. Frontend puede implementar la parte que ya tenga sus entradas
verificadas; la parte dependiente queda bloqueada hasta recibir esas revisiones.

Entregá un mapa historia → tareas → dependencias y las decisiones pendientes
que requieran negocio, diseño o backend. El mapa propone trabajo ejecutable;
no es una instrucción para activar otras sesiones automáticamente.
