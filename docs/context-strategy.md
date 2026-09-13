# Estrategia de contexto y presupuesto de tokens

Esta política reduce contexto repetido sin rebajar los gates de calidad de
agyFlow. Se aplica tanto a una sola sesión como al trabajo conjunto entre agy y
Codex. Los presupuestos son objetivos operativos, no permisos para omitir una
entrada obligatoria ni límites que justifiquen inventar información.

## Principios

1. **Índice antes que corpus.** Empezá por `AGENTS.md`, el rol asignado y su
   skill principal. Usá esos índices para elegir la siguiente lectura.
2. **Contexto por tarea.** Leé el ticket, criterios y secciones de arquitectura,
   protocolo y stack que afecten el alcance actual. No cargues documentos
   completos cuando una sección identificable sea suficiente.
3. **Código por dependencia.** Abrí primero los archivos asignados, imports,
   contratos y pruebas directamente relacionados. Ampliá el radio solo ante una
   duda concreta o un impacto descubierto.
4. **Referencias en vez de copias.** Los handoffs transportan revisión, rutas,
   IDs, resultados y bloqueos. No duplican PRD, contratos, conversaciones ni
   reportes completos.
5. **Calidad antes que cuota.** Seguridad, autorización, contratos, migraciones
   y arquitectura pueden superar el objetivo cuando la evidencia necesaria lo
   exige. El agente registra por qué amplió el contexto.

## Lectura progresiva

Aplicá estas capas en orden y detené la expansión cuando ya exista evidencia
suficiente para ejecutar o reportar un bloqueo:

1. `AGENTS.md`, `.agents/agents/<rol>/agent.md` y la skill principal del rol.
2. Ticket o encargo, revisión candidata y handoff recibido.
3. Secciones relevantes del PRD, arquitectura, protocolo, stack y sprint.
4. Archivos asignados y sus dependencias directas: contratos, imports, pruebas,
   configuración o componentes consumidos.
5. Dependencias de segundo nivel solo si una comprobación, conflicto o riesgo
   concreto lo requiere.

No uses una conversación previa como fuente operativa. Si una decisión importa,
debe aparecer en el documento, ticket, contrato o evidencia referenciada.

## Paquetes mínimos por rol

Todos comienzan con el índice, su `agent.md`, su skill principal y el encargo.
Después agregan únicamente este paquete:

| Rol | Contexto inicial de la tarea |
|---|---|
| PO | Brief, PRD vigente si existe y restricciones de negocio referenciadas. Stack solo cuando condiciona una restricción ya decidida. |
| Scrum Master | Revisión aprobada del PRD, historias afectadas, sprint, tickets de Plane y mapa de dependencias/rutas. Arquitectura solo para planificar dependencias técnicas. |
| Designer | Historia y flujo asignados, superficie relevante de arquitectura, sistema visual vigente y referencias concretas de Figma/Pencil. |
| Backend | Historia y criterios afectados, arquitectura del servicio, contratos actuales y archivos/migraciones directamente relacionados. |
| Frontend | Historia y criterios afectados, arquitectura de la superficie, contratos consumidos, entrega visual y componentes/pruebas relacionados. |
| QA | Revisión candidata, diff, criterios afectados, handoffs, pruebas/configuración asociadas y evidencia del entorno. |
| DevOps | Revisión candidata, diff de build/configuración, arquitectura de despliegue, artefacto y dictamen QA correspondiente. |
| Automation | Evento, ticket, estado remoto vigente, espejo del sprint y contrato del workflow o conector afectado. |
| AI PR Reviewer | Solo prompt, política y diff filtrado. No carga conversaciones, repositorio completo, PRD, arquitectura ni diagramas. |

## Objetivos orientativos

Son estimaciones de contexto de entrada por tarea. Si el cliente muestra consumo,
registrá el valor real; si no, usá archivos y tamaño del diff como aproximación.

| Tipo de trabajo | Objetivo inicial |
|---|---:|
| Documentación o mantenimiento simple | 4k–8k tokens |
| PO y planificación | 8k–15k tokens |
| Diseño, Frontend o Backend acotado | 10k–18k tokens |
| QA o revisión por diff | 8k–15k tokens |
| Seguridad o decisión arquitectónica | 12k–20k tokens, ampliable con motivo |

Un objetivo excedido no invalida el trabajo. Sí exige evitar nuevas lecturas
masivas y explicar qué dependencia o riesgo obligó a ampliar el contexto.

## Diagramas y archivos generados

No leas `docs/diagrams/*.excalidraw`, `docs/diagrams/*.svg` ni
`docs/diagrams/*.png` salvo que la tarea sea crear, modificar o verificar esos
diagramas. Son material humano de análisis, no contexto operativo ni fuente de
verdad. Sus decisiones aprobadas se trasladan al PRD, `architecture.md`,
`docs/protocolo.md` o al documento de diseño aplicable. Los assets visuales del
producto sí se consultan cuando forman parte del alcance de Diseño, Frontend o QA.

También evitá lockfiles, bundles, source maps, snapshots extensos y archivos
generados salvo que el cambio, la prueba o el incidente los haga relevantes.

## MCP y herramientas externas

- Consultá primero el ticket, nodo, frame, archivo o recurso identificado; no
  descargues tableros, proyectos o documentos completos por defecto.
- Pedí campos y revisiones concretas. Conservá IDs o enlaces en el handoff en
  lugar de pegar el contenido recuperado.
- Cacheá mentalmente solo durante la sesión. Antes de actuar sobre estado remoto,
  releé la fuente porque otro agente o humano pudo modificarla.
- No hagas una segunda consulta si la primera ya contiene evidencia suficiente.

## Handoffs compactos

`handoff.json`, `candidate.json` y `templates/entrega.md` llevan identificadores,
revisiones, rutas, estados, comandos/resultados y pendientes. La siguiente sesión
abre las referencias que necesita; no recibe transcripciones ni archivos enteros.
Ante un cambio, compartí el nuevo diff o revisión y los bloques afectados.

## AI PR Reviewer

El reviewer filtra binarios, diagramas editables, lockfiles y generados, oculta
formas comunes de secretos y envía como máximo 50.000 caracteres del diff. Ese
máximo aproxima el objetivo de revisión sin depender de un tokenizador concreto.
Si el diff lo supera, el reporte queda marcado como parcial y el job falla: el PR
se divide o un humano define una revisión alternativa. Aumentar el límite es una
decisión explícita y no convierte una muestra parcial en revisión completa.

El reviewer encuentra problemas visibles en el diff. QA y las auditorías de
seguridad deben abrir las dependencias necesarias para verificar comportamiento,
contratos y permisos fuera del fragmento cambiado.

## Medición ligera

En la entrega basta registrar: fuentes principales consultadas, revisión o diff,
comprobaciones ejecutadas, resultado, ampliaciones de contexto relevantes y
pendientes. Compará por tipo de tarea el número de archivos, tamaño enviado al
reviewer, repeticiones y bloqueos. La meta es reducir relecturas y llamadas sin
convertir el conteo en otra fase del proceso.
