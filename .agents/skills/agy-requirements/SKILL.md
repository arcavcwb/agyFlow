---
name: agy-requirements
description: Refinar un brief en historias y criterios verificables para el PO de agyFlow, o revisar la consistencia de un PRD existente sin decidir su implementación.
---

# Requisitos verificables

Las rutas mencionadas son relativas a la raíz del proyecto receptor.
Aplicá `docs/protocolo.md` para entradas y entrega de la fase.
Usá `templates/PRD.md` si falta el documento; conservá el formato existente
cuando ya permita registrar problema, historias, exclusiones y dudas.

## Procedimiento

1. Separá hechos del brief, decisiones explícitas y preguntas abiertas.
   Asociá las decisiones a su fuente; una inferencia se mantiene como propuesta.
2. Identificá el actor, la necesidad y el resultado observable de cada historia.
   Si agrupa resultados que pueden aceptarse por separado, proponé dividirla.
3. Conservá IDs de historias existentes al reformularlas. Identificá qué
   criterios cambiaron para que planificación y QA puedan rastrear el impacto.
4. Escribí criterios Given/When/Then siguiendo la Regla de los 4 Escenarios
   Obligatorios por historia:
   a) Happy Path: flujo ideal exitoso.
   b) Sad Path / Error: datos inválidos o fallos con recuperación clara.
   c) Edge Case: límites de rango, temporizadores o condiciones de borde.
   d) Estado Vacío / Carga: representación visual inicial o en espera.
5. Revisá contradicciones entre historias, alcance y métricas. Una métrica
   propuesta debe distinguirse de una meta acordada y explicar cómo observarla.
6. Presentá el PRD con dudas que afecten la aceptación y decisiones que faltan.
   No conviertas una dependencia de negocio en un endpoint o modelo de datos.

## Ejemplo de refinamiento (4 Escenarios)

Para una historia de búsqueda:
- **Happy Path**: Dada una consulta con coincidencias, cuando termina la búsqueda, entonces muestra las tarjetas ordenadas por relevancia.
- **Sad Path**: Dada una consulta con caracteres no permitidos, cuando se envía, entonces la interfaz marca el campo en rojo y explica el formato requerido.
- **Edge Case**: Dada una consulta de más de 100 caracteres, cuando se introduce, entonces trunca al límite permitido e informa al usuario.
- **Estado Vacío**: Dada una búsqueda sin resultados, cuando concluye, entonces muestra una ilustración de estado vacío y sugiere términos alternativos.

Entregá la revisión del PRD y los IDs afectados. Las preguntas técnicas se
derivan al rol correspondiente sin inspeccionar código fuera del alcance PO.
