# Protocolo operativo del squad

Este protocolo describe el desarrollo de un producto en el proyecto receptor
de agyFlow. Mantener los roles, ejemplos, documentación o validador de la plantilla
no activa estas fases ni requiere crear un PRD, sprint, contratos o conectar Plane.
Las entradas y permisos que siguen corresponden al flujo de producto.
No modifica ni sustituye las decisiones humanas de `architecture.md`.
Las fases se activan explícitamente por el humano; entregar un resultado no
autoriza al agente a iniciar la fase siguiente ni a desplegar a producción.

Cuando participan agy y Codex, cada sesión ejecuta un rol y alcance asignados;
el nombre de la herramienta no amplía sus permisos. Aplicá además
`docs/agy-codex.md` para compartir contexto y coordinar archivos y procesos.

## Preparación y entradas

El humano aporta `architecture.md` antes de las fases técnicas. El PO puede
trabajar antes con un brief; las ambigüedades quedan abiertas en el PRD.
Copiar una plantilla no constituye aprobación. Una aprobación debe identificar
persona, fecha, alcance y revisión exacta o evidencia de la instrucción humana.
Un cambio del alcance aprobado requiere nueva validación de ese alcance.

| Fase | Entrada obligatoria | Entrega y condición de salida |
|---|---|---|
| PO | Brief de negocio | PRD con historias identificables y criterios Given/When/Then; aprobación humana antes de planificación |
| Scrum Master | PRD aprobado y acceso comprobado a Plane | Tickets con responsables, dependencias, criterios y claves estables; espejo del sprint actualizado |
| Preparación técnica | Arquitectura y tareas asignadas | DevOps prepara build/CI/entorno y QA prepara pruebas/configuración; no requiere QA aprobado ni autoriza despliegue |
| Diseño | Ticket, arquitectura y referencias disponibles | Tokens y rutas concretas, revisión de entrega y dependencias visuales resueltas |
| Backend: contratos | Ticket, arquitectura y contratos existentes si los hay | Schemas verificables, rutas, revisión y consumidores afectados; señal de contratos listos |
| Implementación | Ticket y arquitectura; Frontend además necesita contratos y tokens listos que correspondan a su tarea | Cambios identificados por revisión, comandos ejecutados, resultados y limitaciones |
| QA: ejecución final | Revisión integrada e inmutable de producto, pruebas y configuración; criterios del PRD y entorno disponible | Siempre `bug_report.md`, incluso si no hay fallos; resultado aprobado, rechazado o bloqueado |
| DevOps: despliegue | QA aprobado para la revisión exacta a desplegar y arquitectura | Evidencia de build, artefacto identificado, despliegue a Staging y comprobación del servicio |
| Producción | Aprobación humana explícita para artefacto y destino | Solo el despliegue autorizado y su evidencia |

Los contratos pueden crearse por primera vez por Backend si el ticket y la
arquitectura definen lo necesario. La ausencia de contratos no autoriza al
Frontend a inventarlos. Una dependencia no aplicable se registra con motivo.
Diseño y definición de contratos pueden correr en paralelo. Frontend consume
las entregas listas; no debe empezar código dependiente de una entrega pendiente.
La preparación de build y pruebas puede avanzar sobre tareas asignadas mientras
se implementa. Antes del dictamen final se integran producto, pruebas y
configuración y se identifica la revisión candidata. Escribir el reporte como
evidencia posterior no modifica esa revisión; cualquier cambio de código o
configuración que afecte al artefacto exige una nueva validación.

## Entrega entre agentes

Cada agente entrega en su respuesta: ticket e historia, revisión de entrada y
salida, archivos afectados, comprobaciones y resultados, dependencias pendientes,
bloqueos y siguiente rol propuesto. El siguiente rol espera activación explícita.
El coordinador registra referencias a esa evidencia en Plane y en el espejo.
Los agentes de implementación no editan el estado del sprint directamente.
Usá `templates/entrega.md` como formato de traspaso en la respuesta. No exige
crear otro archivo ni ampliar los permisos de escritura del rol.

Un contrato cambiado invalida la señal de listo de los consumidores afectados:
Backend identifica el cambio, el coordinador registra el bloqueo y Frontend
revalida antes de integrar. Se asigna un único escritor por archivo durante
trabajo paralelo; Scrum Master registra las rutas antes de habilitar tareas.
Ante una colisión, se detiene la escritura de ese archivo y se pide reasignación.

## Estado y permisos de escritura

Plane es la fuente de verdad del estado de los tickets. `sprint_actual.md` es
un espejo; el código, el PRD y las evidencias de QA conservan sus propios dueños.

| Actor | Escritura permitida |
|---|---|
| PO | `PRD.md` |
| Scrum Master | Planificación en Plane; estado operativo y espejo si es su responsable asignado |
| Diseño | Archivos visuales asignados; sin lógica de componentes |
| Backend | Contratos y archivos de backend definidos en la arquitectura |
| Frontend | Aplicaciones y archivos de interfaz asignados; contratos de solo lectura |
| QA | `tests/`, `bug_report.md` y configuración de pruebas en rutas asignadas |
| DevOps | Archivos de build, despliegue y evidencia en `docs/deployments/` |
| Automation | `workflows/`; estado operativo autorizado en Plane y espejo si es su responsable asignado |

Scrum Master crea el espejo inicial. Al planificar, el humano asigna un único
responsable de estado operativo: Scrum Master en operación manual, o Automation
si existe una automatización habilitada y verificada. No se exige n8n para operar
manualmente con Plane. La asignación abarca sincronización, transiciones de estado,
deduplicación, contador de reaperturas y escalado; queda registrada en el sprint.
Si Automation es responsable, Scrum cambia planificación en Plane y solicita
sincronización. Un cambio de responsable transfiere el conjunto: se detiene al
anterior, se reconcilian sus operaciones pendientes y se registra la instrucción
humana. No se ejecutan dos procesadores de estado o del espejo simultáneamente.
Scrum lee la arquitectura y los mapas de rutas entregados por los responsables
técnicos para asignar archivos sin inferir ubicaciones ni leer código de producto.
QA coordina manifests y lockfiles con su escritor asignado; si necesita cambios
fuera de su alcance, entrega la modificación requerida a ese responsable.

Antes de crear tickets, Scrum Master consulta Plane por la clave estable
`<proyecto>:<historia>:<tarea>` registrada en su descripción. El espejo local no
basta para deduplicar. Si hay varias coincidencias, se bloquea la creación.
Los nombres de campos y herramientas reales se descubren en el MCP; estas claves
son convenciones documentales y no presuponen un esquema de API de Plane.

Cada sincronización registra fecha UTC y referencias remotas. Antes de escribir
un cambio en Plane, se vuelve a leer el ticket; si cambió desde la lectura
anterior, se reconcilia primero. El espejo se reemplaza completo y atómicamente
solo después de confirmar la lectura remota. Un fallo deja el espejo anterior
sin presentarlo como actualizado y se comunica al humano. Sin conexión no se
confirman transiciones ni se inventan IDs remotos.

## QA, reaperturas y reintentos

QA siempre registra revisión, entorno, criterios cubiertos, comandos o pasos,
resultados, evidencia y pruebas pendientes. No ejecutado significa bloqueado,
nunca aprobado. Cero bugs reportados por sí solo no acredita una prueba exitosa.
Cada fallo incluye severidad, reproducción, esperado, observado y responsable
propuesto. QA no corrige producto ni modifica tickets directamente.

QA entrega los tres posibles dictámenes al responsable de estado operativo.
Este registra `aprobado` con su revisión, `rechazado` como retorno a corrección,
y `bloqueado` como impedimento sin incrementar el contador. Una aprobación
termina la secuencia de reaperturas; conserva el historial. El registro de un
dictamen no activa la fase siguiente ni autoriza desplegar.

El responsable de estado operativo procesa cada resultado con una clave estable
`<ticket>:<revision>:<ejecucion-qa>`. Primero consulta en Plane si ya se registró
esa clave. Mantiene en el ticket un historial con clave, contador y estado
`pendiente` o `aplicado`; solo un procesador actúa sobre el ticket a la vez.
Un reintento reanuda la operación pendiente, verifica el estado remoto y no
incrementa de nuevo el contador. Si no puede determinar si se aplicó, escala
para reconciliación en vez de repetir la escritura a ciegas.
Antes de aplicar sus efectos, contrasta revisión e ID de ejecución del evento con
la candidata y ejecución QA actuales del ticket. Un dictamen tardío se conserva como historial
sin cambiar estado, contador ni aprobación vigente. Un nuevo ID de ejecución no
es suficiente para contar otra reapertura si el ticket ya está en corrección:
debe existir una nueva entrada a QA registrada para esa ejecución.

El contador vive en Plane y se refleja en el sprint. Cada ejecución de QA
rechazada distinta que devuelve el ticket a corrección cuenta una reapertura.
Al llegar a tres consecutivas, el ticket pasa al estado lógico `escalado` y no
se reasigna automáticamente. QA aprobado para la revisión corregida termina la
secuencia; un desbloqueo manual exige evidencia humana y conserva el historial.
La notificación usa únicamente un canal autorizado; si no hay uno, se informa
en la sesión y se deja pendiente. Nunca se da por enviada sin confirmación.

Los estados lógicos son `pendiente`, `bloqueado`, `listo`, `en_curso`, `en_qa`,
`correccion`, `escalado`, `qa_aprobado` y `staging`. Scrum Master documenta su
correspondencia con los estados reales de Plane antes de usarlos. No son nombres
de estados remotos que se puedan asumir disponibles.

| Transición lógica | Evidencia necesaria |
|---|---|
| `pendiente` / `bloqueado` → `listo` | Entradas resueltas, dependencias y asignación registradas |
| `listo` / `correccion` → `en_curso` | Activación explícita del trabajo asignado |
| `en_curso` → `en_qa` | Revisión candidata integrada y activación de QA con ID de ejecución |
| `en_qa` → `bloqueado` | Impedimento documentado; conserva el contador |
| `en_qa` → `correccion` / `escalado` | Rechazo vigente no procesado; tercera reapertura lleva a escalado |
| `en_qa` → `qa_aprobado` | Dictamen aprobado vigente; termina la secuencia de reaperturas |
| `qa_aprobado` → `staging` | Despliegue autorizado del artefacto correspondiente y comprobación exitosa |

Resolver un bloqueo de pruebas vuelve a preparar `en_qa` con revisión y ejecución
identificadas, sin forzar otra implementación si no cambió producto. Salir de
`escalado` requiere la instrucción humana y la reconciliación documentadas.
Un cambio de revisión tras aprobación invalida `qa_aprobado` y devuelve el ticket
a preparación/QA según el trabajo pendiente; no se reutiliza para desplegar.

## Evidencia de despliegue

DevOps comprueba que el reporte esté aprobado, cubra los criterios requeridos,
no tenga bloqueantes abiertos ni verificaciones obligatorias pendientes y
corresponda exactamente a la revisión del artefacto. Rechaza reportes ausentes
o desactualizados. Cualquier cambio del producto después de QA exige revalidar
la revisión nueva; una copia editable sin identificación verificable no alcanza.
En Git se usa el commit y se comprueba que no haya cambios de producto sin
registrar. Sin Git hace falta un identificador inmutable verificable del artefacto.

Registra revisión, identificador del artefacto, resultado de build, destino,
fecha, comprobación posterior y referencia de QA en `docs/deployments/`.
Si falla Staging, reporta el fallo y sigue el procedimiento de recuperación de
la arquitectura; no improvisa acciones destructivas. La aprobación de producción
debe referenciar ese artefacto y el destino exacto.

## Herramientas no disponibles

Los asistentes locales se describen en `docs/herramientas-locales.md`. Sus JSON
son exportaciones opcionales de evidencia, con rutas asignadas al coordinador;
no sustituyen Plane, las fuentes originales, los permisos ni la activación humana.
La aprobación registrada del PRD se vincula a su contenido exacto. Ningún resultado
de consistencia de estos asistentes acredita por sí solo un QA o despliegue real.

Las skills propias asignadas están en `config/skills.json`; su uso se explica
en `docs/skills.md`. El stack de referencia está en `docs/stack.md`.
Una mención de skill o MCP no demuestra que esté instalado. Confirmá las
herramientas disponibles y sus parámetros antes de usarlas. Si falta una
herramienta necesaria, declaralo y no simules ejecución. Las tareas documentales
independientes pueden continuar. Este protocolo no implementa una automatización:
los workflows reales deben construirse y verificarse contra las herramientas
disponibles antes de habilitar sincronización o reaperturas automáticas.
