# agyFlow

agyFlow es una plantilla reutilizable para desarrollar un **SUPER MVP** con un
squad de agentes: PO, Scrum Master, Designer, Frontend, Backend, QA, DevOps y
Automation. Su foco es entregar rápido sin perder cuatro cosas que suelen romper
un MVP acelerado: calidad visual, seguridad, arquitectura clara y simplicidad de
implementacion.

Este repo no es una aplicacion de producto. Aqui se mantienen los roles, skills,
protocolo, plantillas, diagramas y validadores que despues se copian a un proyecto
receptor. El PRD real, la arquitectura, los tickets, contratos, credenciales,
entornos y despliegues pertenecen al proyecto receptor.

## Que incluye

- Ocho agentes bajo `.agents/agents/<nombre>/agent.md`.
- Una skill propia por agente bajo `.agents/skills/<nombre>/SKILL.md`.
- Protocolo operativo con gates humanos, handoffs, QA y recuperacion.
- Plantillas para PRD, sprint, setup, handoff, candidata y reporte de QA.
- Scripts locales para validar la plantilla, inicializar receptores, revisar
  evidencias y simular el recorrido.
- Diagramas Excalidraw/Excalidash para analizar el flujo y el sistema visual.
- Guia para trabajar con agy y Codex en paralelo.
- Reviewer opcional de pull requests con Gemini, deshabilitado por defecto.

El stack de referencia contempla Plane, Astro, React, Next.js, Node.js, NestJS,
Figma/Pencil, Supabase y n8n segun lo decida cada proyecto. Mencionarlos aqui
no significa que esten instalados ni conectados.

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
docs/herramientas-locales.md
docs/ai-pr-reviewer.md
docs/demo-flujo.html
docs/diagrams/
  agyflow-super-mvp.excalidraw
  agyflow-flujo-completo.excalidraw
templates/
  PRD.md
  sprint_actual.md
  bug_report.md
  entrega.md
  project_setup.md
  handoff.json
  candidate.json
scripts/
  validate_squad.py
  handoff.py
  setup_receiver.py
  pipeline.py
  demo_workflow.py
tools/ai-pr-reviewer/
  review_agent.py
  prompt.md
  policy.md
tests/
  test_validate_squad.py
  test_handoff.py
  test_setup_receiver.py
  test_pipeline.py
.vscode/tasks.json
.github/workflows/validate-squad.yml
.github/workflows/ai-pr-review.yml
```

`architecture.md` no vive en esta plantilla. Lo aporta el humano en cada proyecto
receptor. `setup_receiver.py` solo crea `architecture.proposed.md` para revision.

## Validar

Para comprobar que la plantilla sigue consistente:

```bash
python3 scripts/validate_squad.py
python3 -m unittest discover -s tests -q
```

Para ver el flujo con datos simulados:

```bash
python3 scripts/demo_workflow.py
```

Tambien podes abrir `docs/demo-flujo.html` en el navegador. La demo ejecuta los
controles locales, pero sus aprobaciones, referencias de diseno, QA y despliegues
son simulados.

## Usar la plantilla en otro proyecto

1. Revisá primero la vista previa y después inicializá el proyecto receptor:

   ```bash
   python3 scripts/setup_receiver.py --target /ruta/al/proyecto --frontend hybrid --backend nestjs --db supabase --dry-run
   python3 scripts/setup_receiver.py --target /ruta/al/proyecto --frontend hybrid --backend nestjs --db supabase
   ```

   Se genera `architecture.proposed.md` para revisión humana; no se escribe
   `architecture.md` ni se inventan contratos. Los conflictos se conservan por
   defecto. `--force` actualiza archivos del paquete con respaldo por archivo,
   sin borrar directorios ni sustituir documentos de producto existentes.

2. Ejecutá `python3 scripts/validate_squad.py` para validar el paquete local.

3. Confirmá los agentes en el cliente local:

   ```bash
   agy --help
   agy agents
   ```

   Si el runtime no muestra los agentes, pedí a la sesion que lea explicitamente
   `AGENTS.md`, el `agent.md` del rol y su skill. Eso permite operar con las
   instrucciones aunque el descubrimiento nativo no este acreditado.

4. Configurá solo los MCP necesarios:

   ```bash
   agy mcp add --help
   agy mcp list --help
   ```

   El ejemplo `.agents/mcp_config.example.json` no contiene credenciales ni es
   una instalacion activa. Despues de registrar un MCP, comproba una lectura real.

5. Aporta `architecture.md`, brief inicial y herramientas verificadas. Luego
   activa el primer rol, por ejemplo:

   ```bash
   agy --agent po-agent
   ```

   El PO refina el PRD. Scrum Master no se activa hasta que el humano apruebe
   el contenido exacto del PRD.

6. En el receptor, usa `python3 scripts/validate_squad.py --project` antes de
   fases tecnicas. Este modo espera documentos y contratos del proyecto real; no
   se deben crear archivos vacios solo para pasar el check.

7. Registrá herramientas comprobadas, skills seleccionadas y responsables usando
   `templates/project_setup.md`. Comprobá cada cliente por separado. Las skills
   propias se incluyen; los complementos no se descargan durante la validación.

## Flujo

El recorrido operativo esta documentado en `docs/protocolo.md` y representado en
`docs/diagrams/`. La version corta es:

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

Las fases se activan explicitamente. Plane es la fuente de verdad del estado. El
humano elige un unico responsable de estado operativo: Scrum Master en modo manual
o Automation si existe una automatizacion verificada. n8n es opcional.

## Herramientas locales

`scripts/handoff.py` valida snapshots JSON de evidencia entre roles. Ya no intenta
deducir aprobaciones leyendo texto libre.

```bash
python3 scripts/handoff.py check --role frontend-dev-agent --input handoff.json
```

`scripts/pipeline.py` diagnostica la siguiente fase segun PRD, aprobacion local,
arquitectura y evidencia disponible. `advance` propone la siguiente accion; no
registra aprobaciones ni ejecuta agentes.

```bash
python3 scripts/pipeline.py --root /ruta/al/proyecto check-prd
python3 scripts/pipeline.py --root /ruta/al/proyecto status
python3 scripts/pipeline.py --root /ruta/al/proyecto advance
```

La guia completa esta en `docs/herramientas-locales.md`.

## Agy + Codex

Para usar agy en Antigravity y Codex en paralelo, segui `docs/agy-codex.md`.
La idea recomendada es simple: una sesion implementa una tarea concreta y la otra
revisa protocolo, arquitectura, seguridad, QA o handoff. Ambas deben leer las
mismas fuentes del proyecto y respetar el mismo responsable por archivo.

## Skills

La asignacion completa esta en `docs/skills.md` y `config/skills.json`. Las skills
incluidas son:

| Agente | Skill incluida |
|---|---|
| `po-agent` | `agy-requirements` |
| `scrum-master-agent` | `agy-planning` |
| `designer-agent` | `agy-design-handoff` |
| `frontend-dev-agent` | `agy-frontend-delivery` |
| `backend-dev-agent` | `agy-backend-contracts` |
| `qa-agent` | `agy-qa-evidence` |
| `devops-agent` | `agy-build-release` |
| `automation-agent` | `agy-sync-state` |

La skill `agy-security-audit` queda disponible para revisiones de seguridad de QA
y Backend. Las skills externas dependen del proyecto y de las herramientas
instaladas en ese entorno.

## Reviewer opcional de PR

`tools/ai-pr-reviewer` analiza el diff de un pull request mediante Gemini antes
de QA. Se habilita de forma explícita con la variable de repositorio
`ENABLE_AI_PR_REVIEW=true` y el secret `GEMINI_API_KEY`. El workflow falla ante
hallazgos críticos y también cuando la revisión no puede completarse. Su reporte
es evidencia auxiliar: no aprueba QA ni reemplaza la revisión humana.

El diff se procesa mediante un proveedor externo. Antes de habilitarlo, revisá
las reglas de privacidad del proyecto. La configuración, limitaciones y política
completas están en `docs/ai-pr-reviewer.md`.

## Diagramas

`docs/diagrams/agyflow-flujo-completo.excalidraw` muestra la operacion completa
en seis marcos: filosofia, squad, handoff, reglas operativas, CLI y uso practico.
`docs/diagrams/agyflow-super-mvp.excalidraw` sirve para discutir el flujo, la
estructura y el sistema de diseno. Ambos pueden importarse en Excalidraw o
Excalidash; las vistas SVG/PNG son solo previsualizaciones.

## Limites

El validador comprueba estructura, nombres, frontmatter básico, formato de la
plantilla MCP, documentación, asignaciones de skills con rutas portables y la
integridad del reviewer opcional cuando alguno de sus archivos está presente.
`--project` agrega presencia y contenido minimo de documentos del receptor. No
valida semantica del runtime, conectividad, aprobaciones humanas, calidad de
contratos ni que una aplicacion pase sus pruebas.

`handoff.py` y `pipeline.py` comprueban consistencia local de evidencias. No
autentican personas, no consultan Plane, no ejecutan QA real y no despliegan.

## Estado actual

- La validación del paquete pasa con los ocho agentes en las rutas documentadas.
- La suite local cubre asignaciones rotas, archivos ausentes, JSON inválido, rutas
  no portables, evidencia de handoff, conservación de archivos al adoptar la
  plantilla, estructura de escenarios y diagnóstico del pipeline. Incluye casos
  de QA rechazado o antiguo y cambios de PRD tras una aprobación registrada.
- Se comprobó que `--project` detecta la ausencia de `architecture.md`, `PRD.md`,
  `sprint_actual.md` y contratos TypeScript en `packages/contracts/src`.
  Es una comprobación del destino; esos archivos no se requieren en esta plantilla.
- `agy agents` terminó con código cero pero sin mostrar una lista, incluso con
  terminal. Por eso el descubrimiento por el runtime sigue sin estar acreditado.
- No se conectaron servidores MCP ni se ejecutaron despliegues o workflows.
  Los recorridos de QA y reaperturas están definidos documentalmente; deben
  probarse con las herramientas del proyecto receptor antes de automatizarlos.
