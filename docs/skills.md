# Skills asignadas al squad

`config/skills.json` es el registro de esta plantilla, no una configuración
nativa de agy o Codex. Cada `agent.md` pide leer su skill propia explícitamente;
esto permite reutilizar las instrucciones aunque el cliente no descubra roles
o skills automáticamente. El descubrimiento y los permisos se prueban por sesión.

| Agente | Skill incluida | Procedimiento |
|---|---|---|
| `po-agent` | `agy-requirements` | Refinar requisitos y criterios verificables |
| `scrum-master-agent` | `agy-planning` | Descomponer historias y preparar tareas en Plane |
| `designer-agent` | `agy-design-handoff` | Entregar diseño, tokens y estados de interfaz |
| `frontend-dev-agent` | `agy-frontend-delivery` | Consumir contratos y diseño según framework |
| `backend-dev-agent` | `agy-backend-contracts` | Definir contratos e implementar servicios |
| `qa-agent` | `agy-qa-evidence` | Elegir pruebas y producir un dictamen trazable |
| `devops-agent` | `agy-build-release` | Preparar build y comprobar el artefacto a desplegar |
| `automation-agent` | `agy-sync-state` | Reconciliar estado y procesar eventos sin duplicarlos |

Las ocho skills se distribuyen en `.agents/skills/<nombre>/SKILL.md`. Son
procedimientos propios: no incluyen manuales completos de frameworks ni instalan
dependencias. Los límites de rol permanecen en `agent.md` y la coordinación en
`docs/protocolo.md`. Las rutas mencionadas en las skills parten de la raíz del
proyecto receptor; sus plantillas y protocolos se distribuyen con ellas.

## Complementos por tarea

El registro contiene candidatos externos con origen y condición de uso. Algunos
IDs representan colecciones o documentación, no nombres de skills instalables.
`candidate` y `revision: null` significan que no se ha fijado una revisión ni
instalado el complemento como parte de este paquete.
Si un proyecto usa `status: pinned`, el registro exige un commit Git de 40
caracteres hexadecimales en `revision`. Eso identifica la referencia seleccionada,
no demuestra que esté descargada ni habilitada en un cliente.

- Diseño: [Impeccable](https://github.com/pbakaus/impeccable) y los procedimientos
  del proveedor para [Figma](https://developers.figma.com/docs/figma-mcp-server/create-skills/).
  [Pencil](https://docs.pencil.dev/getting-started/ai-integration) queda condicionado
  a identificar la herramienta y comprobar sus capacidades reales.
- Frontend: [guía oficial para trabajar con Astro](https://docs.astro.build/en/guides/build-with-ai/)
  y [Vercel React Best Practices](https://github.com/vercel-labs/agent-skills/tree/main/skills/react-best-practices)
  según el componente. Para [Next.js](https://github.com/vercel/next.js/tree/canary/skills),
  elegí workflows y documentación compatibles con la versión del proyecto.
- Backend: [NestJS Best Practices de Kadajett](https://github.com/Kadajett/agent-nestjs-skills)
  es comunitaria; revisar sus reglas de DTO, validación y ejecución TypeScript
  antes de adoptarla. Las [skills de Supabase](https://github.com/supabase/agent-skills)
  solo se seleccionan si la tarea usa ese servicio o Postgres.
- Frontend y QA: [webapp-testing](https://github.com/anthropics/skills/tree/main/skills/webapp-testing)
  para comprobaciones de navegador. El runner de pruebas del proyecto conserva
  sus convenciones; esta referencia no obliga a migrar la suite a otro lenguaje.
- Automation: [n8n-skills](https://github.com/czlonkowski/n8n-skills) cuando n8n
  esté elegido y configurado; no es requisito para operar Plane manualmente.

Leé solo el complemento que cambie decisiones de la tarea actual. Si falta uno
opcional, usá la skill propia y documentación vigente cuando permitan completar
el trabajo. Si falta una capacidad indispensable, entregá el bloqueo concreto.
Plane, Figma y Pencil necesitan herramientas de acceso verificadas además de
instrucciones; una skill no concede una conexión o credenciales.

## Adopción en el proyecto receptor

Seleccioná paquete y skill concretos, revisá sus instrucciones, compatibilidad
y licencia antes de redistribuirlos, y fijá una revisión reproducible. Registrá
la comprobación en el formato `templates/project_setup.md`. Una copia local de
Astro u otra skill fuera del repositorio no forma parte de esta distribución.
No copies rutas absolutas de un equipo al registro compartido.

El validador verifica la integridad de las asignaciones y archivos incluidos.
No descarga fuentes ni certifica calidad, licencia o compatibilidad de candidatos.
