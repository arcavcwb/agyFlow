# AGENTS.md — Índice Maestro del Squad

Este archivo es el índice del squad. Verificá su carga en la versión instalada
de Antigravity CLI (`agy`). El resto del contexto se lee bajo demanda.

## Alcance: plantilla y proyecto receptor

En agyFlow se mantienen roles, protocolos, ejemplos y el validador reutilizables.
Las fases de producto que siguen se aplican al usar la plantilla en un proyecto
receptor. Mantener esta plantilla no requiere crear un PRD, un sprint, contratos
de aplicación ni conectar Plane. No reportes su ausencia aquí como un defecto.

En el proyecto receptor, leé su arquitectura y requerimientos reales antes de
ejecutar una fase. Adaptá las referencias de stack y rutas a las decisiones
humanas; no asumas que copiar este índice cambia la arquitectura del proyecto.

## Regla de cero asunción

Tu conocimiento del proyecto viene exclusivamente de los archivos que leas en la
sesión actual. Si un tipo, contrato o parámetro no está explícitamente definido en
`packages/contracts` o en la documentación leída, decilo — no lo asumas ni lo
inventes. Queda prohibido asumir contratos de API o estructuras de datos no
verificadas.

## Agentes del squad

Cada uno vive en `.agents/agents/<nombre>/agent.md` y se invoca con
`agy --agent <nombre>`. Verificá el descubrimiento con `agy agents` antes de operar:

| Agente | Dominio |
|---|---|
| `po-agent` | `PRD.md` e historias de usuario |
| `scrum-master-agent` | Plane, planificación y estado operativo manual si se asigna |
| `designer-agent` | Diseño, tokens y recursos de Figma/Pencil según proyecto |
| `frontend-dev-agent` | Astro, React y Next.js en las rutas de la arquitectura |
| `backend-dev-agent` | Contratos compartidos y servicios Node.js/NestJS; persistencia según proyecto |
| `qa-agent` | Pruebas, configuración asignada y `bug_report.md` |
| `devops-agent` | Preparación de build/CI/entorno y despliegue a Staging tras QA |
| `automation-agent` | Workflows opcionales y estado operativo si se asigna |

Ninguno tiene `mainAgent: true` — todos son `subagent: true`, invocables bajo
demanda. El squad no decide autónomamente qué fase ejecutar a continuación; el
protocolo de handoff (abajo) sigue siendo gatillado explícitamente.

## Reglas y contratos

- **Arquitectura y stack:** `architecture.md` — gobernanza humana, ningún agente
  lo modifica.
- **Contrato de tipos:** `packages/contracts` — el Backend Dev Agent escribe, el
  Frontend Dev Agent solo lee.
- **Estado del sprint:** `sprint_actual.md`
- **Requerimientos vigentes:** `PRD.md`
- **Reportes de QA:** `bug_report.md`
- **Coordinación y entregas:** `docs/protocolo.md` — leer antes de ejecutar una fase.
- **Trabajo con agy y Codex:** `docs/agy-codex.md` — leer si ambas sesiones participan.
- **Asignación de skills:** `config/skills.json` y `docs/skills.md`.
- **Stack de referencia:** `docs/stack.md` — versiones y rutas las define el proyecto receptor.
- **Plantillas iniciales:** `templates/` — no representan trabajo aprobado.

## Protocolo de handoff (resumen)

```
Humano → PO → validación humana del PRD → Scrum Master
  → [Diseño + definición de contratos por Backend]
  → contratos y tokens listos → [implementación Backend + Frontend]
  → integración de producto, pruebas y build/CI preparados por QA/DevOps
  → QA final → DevOps despliega a Staging → aprobación humana para Producción
  QA → responsable de estado (Scrum o Automation) registra dictamen
  QA rechazado → reapertura → activación explícita de corrección
```

El protocolo operativo está en `docs/protocolo.md`. `architecture.md` define
el stack y las decisiones del proyecto y sigue siendo de gobernanza humana.
Si ambos documentos se contradicen, reportá el conflicto antes de actuar.

## Configuración de herramientas

Plantilla de MCP: `.agents/mcp_config.example.json`; no contiene una instalación
activa. Registrá los servidores con el mecanismo confirmado por el CLI local.
Nunca guardes credenciales en archivos versionados ni asumas aislamiento por
`inheritMcp`. Los límites de rol no sustituyen permisos del entorno.
Cada rol lee su skill incluida desde la ruta indicada en `agent.md`; no se
presupone un campo de frontmatter para asignarlas en los dos clientes.
