# agyFlow — plantilla reutilizable de desarrollo agéntico

Este repositorio mantiene una plantilla para copiar y adaptar a otros proyectos,
con ocho roles y fases activadas explícitamente por una persona. Incluye
instrucciones para agy y Codex, protocolo de entregas y formatos de evidencia.
Cada rol incluye una skill propia. El stack de referencia es Plane, Astro,
React, Next.js, Node.js, NestJS y diseño con Figma/Pencil según el proyecto.

Aquí se desarrolla y valida la plantilla. La aplicación, su arquitectura, PRD,
sprint, contratos, credenciales y despliegues pertenecen a cada proyecto receptor.
Su ausencia en agyFlow es esperada y no representa un defecto ni una tarea pendiente.

## Estructura

```text
AGENTS.md
.agents/
  agents/<nombre>/agent.md
  skills/<nombre>/SKILL.md
  mcp_config.example.json
config/skills.json
docs/protocolo.md
docs/agy-codex.md
docs/skills.md
docs/stack.md
docs/diagrams/
  agyflow-super-mvp.excalidraw
templates/
  PRD.md
  sprint_actual.md
  bug_report.md
  entrega.md
  project_setup.md
scripts/
  validate_squad.py
  handoff.py
  setup_receiver.py
  pipeline.py
tests/
  test_validate_squad.py
  test_handoff.py
  test_setup_receiver.py
  test_pipeline.py
.vscode/tasks.json
.github/workflows/validate-squad.yml
```

`architecture.md` pertenece al proyecto receptor y lo aporta el humano.
No se genera ni modifica automáticamente. Las plantillas no contienen
decisiones de negocio, contratos de API ni aprobaciones reales.

## Mantener esta plantilla

Revisá instrucciones, roles, documentación y ejemplos. Comprobá el paquete con:

```bash
python3 scripts/validate_squad.py
python3 -m unittest discover -s tests -v
```

El mantenimiento de agyFlow no requiere un sprint en Plane, contratos de una
aplicación ni activar las fases de producto. Conservá los formatos genéricos en
`templates/`; no guardes aquí datos o credenciales de un proyecto receptor.

## Usar la plantilla en otro proyecto
 
1. Podés inicializar automáticamente el proyecto receptor con:
   ```bash
   python3 scripts/setup_receiver.py --target /ruta/al/proyecto --frontend hybrid --backend nestjs --db supabase
   ```
   O copiar manualmente `AGENTS.md`, `.agents/`, `config/`, `docs/`, `templates/`, `scripts/` y `tests/`
   al proyecto receptor, integrando cambios sin pisar archivos existentes.
   Integrá también las exclusiones de `.gitignore` antes de añadir credenciales.
   Revisá con el humano el stack y las rutas que asumen los roles antes de usarlos.
   Copiar la plantilla no redefine la arquitectura de una aplicación existente.
2. Ejecutá `python3 scripts/validate_squad.py` para validar el paquete local.
3. Consultá `agy --help` y ejecutá `agy agents` desde la raíz. Confirmá que se
   descubran los ocho nombres del índice antes de invocar un rol.
   Si no se descubren, pedí en la sesión que lea el `agent.md` del rol y su skill:
   es una lectura explícita de instrucciones, no un registro nativo comprobado.
4. Consultá `agy mcp add --help` y `agy mcp list --help`. Configurá únicamente los
   servidores necesarios con los comandos, credenciales y versiones verificados
   para tu entorno. Usá `agy mcp list` para comprobar su registro; el registro
   por sí solo no prueba conexión ni acceso. Verificá una operación de lectura.
5. Revisá `docs/protocolo.md`, aportá la arquitectura y un brief, e invocá el rol
   correspondiente: por ejemplo, `agy --agent po-agent`. El PO crea el PRD;
   el humano lo valida antes de activar Scrum Master.
6. En el proyecto receptor, antes del trabajo que consume contratos, ejecutá
   `python3 scripts/validate_squad.py --project`. Los archivos requeridos por esa
   fase deben existir; no los reemplaces por documentos vacíos para superar el check.
   Backend puede definir los primeros contratos con arquitectura y tickets suficientes.
7. Registrá herramientas comprobadas, skills seleccionadas y responsables usando
   `templates/project_setup.md`. Comprobá cada cliente por separado. Las skills
   propias se incluyen; los complementos no se descargan durante la validación.

La ayuda del CLI local comprobada durante esta revisión incluye `agents`,
`mcp` y `--agent`; no lista `inspect`. La sintaxis y el descubrimiento de agentes
deben verificarse en cada instalación. Este paquete no acredita que el runtime
acepte su frontmatter hasta comprobar los agentes cargados.

## MCP y skills

Para usar agy y la extensión de Codex juntos, seguí [la guía de trabajo
compartido](docs/agy-codex.md). Incluye instrucciones para pasar tareas entre
sesiones y empezar con una sesión implementando y otra revisando.

`.agents/mcp_config.example.json` es una referencia de configuración, no un
archivo activo. Conserva ejemplos de Plane, n8n y Playwright con valores pendientes.
El esquema y los comandos de esos servidores requieren validación antes de uso.
DevOps Helper se omite porque no había un comando de arranque comprobado.

El mecanismo confirmado por la ayuda local para registrar servidores es
`agy mcp add`; no se presupone que el CLI cargue automáticamente esta plantilla
ni dónde guarda su configuración. No introduzcas secretos en el ejemplo.
`.gitignore` excluye `.agents/mcp_config.json` y archivos `.env` locales.

La asignación completa está en [docs/skills.md](docs/skills.md) y
`config/skills.json`: ocho procedimientos incluidos y complementos externos
condicionados a la tarea y versión del proyecto. Las referencias a Astro, React,
Next.js, NestJS, Impeccable, Figma/Pencil, Supabase, `webapp-testing` y n8n no son
una instalación activa. Leé las instrucciones seleccionadas antes de usar comandos.
`inheritMcp: true` no demuestra aislamiento entre servidores; verificá los
permisos del entorno. No se instalan herramientas ni se conectan cuentas como
parte de la validación local.

## Flujo y recuperación

El [mapa visual del SUPER MVP](docs/diagrams/README.md) reúne en un único lienzo
editable de Excalidraw el flujo, la operación de tareas, la estructura de la
plantilla y una propuesta de sistema de diseño. Incluye vistas previas SVG y PNG.

```text
Brief → PO → aprobación humana del PRD → Scrum Master
  → Diseño + contratos Backend
  → entregas listas → implementación Backend + Frontend
  → integrar producto + tests + preparación build/CI de QA y DevOps
  → QA aprobado para la revisión → DevOps → Staging
  → aprobación humana del artefacto y destino → Producción

QA rechazado → responsable de estado registra una reapertura sin duplicarla
  → activación explícita de corrección → QA
Tres rechazos consecutivos → escalado humano
```

El detalle de entradas, responsables, estados, reintentos y evidencias está en
`docs/protocolo.md`. Plane es la fuente de verdad. El humano elige Scrum en modo
manual o Automation como responsable único de espejo, estados y reaperturas.
QA siempre entrega su dictamen: aprobado termina la secuencia de reaperturas,
rechazado cuenta una sola por ejecución y bloqueado registra el impedimento.
n8n no es requisito para la operación manual. Cada fase requiere activación explícita.

## Alcance de la validación

El validador comprueba estructura, nombres, frontmatter básico, formato de la
plantilla MCP, documentación y asignaciones de skills con rutas portables.
Este es el modo de validación de agyFlow.
`--project` es una comprobación adicional para el proyecto receptor: agrega
presencia y contenido mínimo de documentos del proyecto y contratos TypeScript.
No debe usarse como criterio de aceptación de la plantilla. Si adaptás el stack
o las rutas en el destino, adaptá también esa comprobación a su arquitectura.
No valida semántica del runtime, conectividad, aprobación humana, calidad de
contratos ni que una aplicación pase sus pruebas. El protocolo es una regla
operativa; la sincronización y el contador deben implementarse y probarse en los
workflows reales antes de habilitar automatización.

## Resultado de la revisión local

- La validación del paquete pasa con los ocho agentes en las rutas documentadas.
- Las ocho skills incluidas pasan la validación de estructura. Las 28 pruebas
  locales cubren asignaciones rotas, archivos ausentes, JSON inválido, rutas no
  portables, handoffs entre agentes, scaffolding guiado, validación de Gherkin y pipeline interactivo.
- Se comprobó que `--project` detecta la ausencia de `architecture.md`, `PRD.md`,
  `sprint_actual.md` y contratos TypeScript en `packages/contracts/src`.
  Es una comprobación del destino; esos archivos no se requieren en esta plantilla.
- `agy agents` terminó con código cero pero sin mostrar una lista, incluso con
  terminal. Por eso el descubrimiento por el runtime sigue sin estar acreditado.
- No se conectaron servidores MCP ni se ejecutaron despliegues o workflows.
  Los recorridos de QA y reaperturas están definidos documentalmente; deben
  probarse con las herramientas del proyecto receptor antes de automatizarlos.
