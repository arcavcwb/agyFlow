---
name: agy-backend-contracts
description: Definir contratos y entregar cambios de servicios para el Backend de agyFlow, con implementación Node.js o NestJS según arquitectura y proveedores de datos opcionales.
---

# Contratos y servicios

Las rutas mencionadas son relativas a la raíz del proyecto receptor.
Aplicá `docs/protocolo.md`. Leé el contrato existente, los criterios del ticket
y las rutas y decisiones de backend en `architecture.md` antes de implementar.

## Procedimiento

1. Identificá entradas, salidas y errores que exige el comportamiento aprobado.
   Para cada campo, distinguí lo documentado de lo que requiere una decisión.
   Si faltan semántica, permisos o resultado esperado, explicitá ese bloqueo.
2. Extendé los schemas de `packages/contracts` o de la ruta confirmada por la
   arquitectura. Conservá convenciones y nombres existentes; no inventes una
   API pública a partir de una pantalla o de un ejemplo genérico del framework.
3. Clasificá los cambios por consumidores afectados: campos nuevos, eliminados,
   nulabilidad o errores pueden exigir coordinación incluso si compila el backend.
   Verificá ejemplos válidos e inválidos que representen reglas del ticket.
4. Entregá el contrato con revisión, exports/rutas y consumidores identificados
   antes de habilitar implementación que dependa de él.
5. Implementá el servicio en las rutas reales del proyecto. En Node.js,
   comprobá runtime y comandos disponibles. En NestJS, seguí módulos y capas
   existentes y mantené el contrato compartido como referencia de validación.
6. Si el proyecto usa Zod, una recomendación NestJS sobre DTOs o decoradores
   no autoriza convertir schemas ni mantener validaciones incompatibles.
   Usá la integración existente o proponé resolver explícitamente la discrepancia.
7. Verificá el comportamiento cambiado, incluidos permisos o errores relevantes,
   con las pruebas y herramientas del proyecto. Si usa Supabase o Postgres,
   cargá las skills pertinentes para ese trabajo; no los agregues como requisito.

## Ejemplo de cambio con consumidores

Cambiar un campo obligatorio a opcional puede afectar la interfaz aunque la
respuesta anterior siga siendo válida. Indicá qué consumidor debe aceptar su
ausencia y qué comportamiento aprobado debe mostrar antes de declarar listo.

Entregá revisión del contrato y servicio, consumidores afectados y evidencia.
Las rutas de servicios, migraciones y persistencia vienen del proyecto receptor.
