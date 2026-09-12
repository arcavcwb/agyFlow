# Desarrollar con agy y Codex

Esta guía sirve tanto para mantener agyFlow como para desarrollar un producto que
adopte la plantilla. Para mantener agyFlow, asigná tareas y rutas en el encargo y
la entrega de cada sesión; no hace falta un sprint ni Plane. Para desarrollar un
producto, aplicá los roles, entradas y fuentes de estado de `docs/protocolo.md`.

agy y Codex son dos sesiones que pueden ejecutar los roles del squad. Asigná
un rol y una tarea concreta a cada sesión; los permisos siguen al rol, no al
modelo. No hace falta ejecutar los ocho roles simultáneamente.

## Primer modo de trabajo: implementación y revisión

1. El humano asigna una tarea a una sesión y una revisión a la otra. Puede
   empezar Codex implementando y agy revisando, o al revés.
2. Ambas leen `AGENTS.md` y esta guía. En trabajo de producto leen además
   `docs/protocolo.md` y el archivo del rol asignado en
   `.agents/agents/<rol>/agent.md` y la skill propia indicada en él, además de
   las entradas necesarias de la tarea. Los complementos se consultan en
   `config/skills.json` y se cargan según `docs/skills.md`.
   Si el rol no aparece en el selector del cliente, se puede pedir su lectura
   explícita como guía; eso no registra un subagente nativo ni instala sus MCP.
3. La sesión implementadora modifica solo su alcance y entrega archivos,
   revisión, comprobaciones, resultados y pendientes en su respuesta.
4. El humano pasa la entrega a la sesión revisora. Durante la revisión de esos
   archivos se pausa su edición, o se revisa una copia inmutable identificada.
   La revisora reporta hallazgos; no aplica correcciones a la vez que el autor.
5. El humano activa la corrección con el autor. Si la revisión es la fase QA,
   se aplican su dictamen y evidencia obligatorios de `docs/protocolo.md`.

La revisión informal puede comenzar antes del sprint. No acredita QA ni permite
saltarse las entradas del flujo de producto. Mientras Plane no esté configurado,
se pueden revisar esta plantilla y preparar documentos; no se simula un sprint
sincronizado ni se crean IDs remotos ficticios.

## Contexto compartido

Las sesiones deben releer los archivos relevantes después de cada entrega. No
se presupone acceso a la conversación, herramientas, credenciales o decisiones
no guardadas de la otra sesión. La coordinación inicial usa archivos y el
traspaso explícito del humano; esta guía no configura un puente entre clientes.

Codex descubre instrucciones de proyecto mediante `AGENTS.md`. Para una sesión
ya abierta, pedile expresamente que relea los archivos actualizados; la carga
inicial no es un mecanismo de sincronización permanente. Verificá por separado
qué instrucciones y herramientas cargó agy. [Documentación de OpenAI](https://learn.chatgpt.com/docs/agent-configuration/agents-md).

## Paralelismo cuando haya tareas independientes

- Para trabajo de producto, registrá en los tickets de Plane el rol, una etiqueta de sesión elegida por el
  humano (por ejemplo, `agy-1` o `codex-1`), alcance, dependencias y rutas. El
  escritor autorizado refleja esa asignación en el sprint; no se crea otro tablero.
- En una misma carpeta, cada archivo tiene un solo escritor. Incluí archivos
  compartidos como manifests, lockfiles y configuración en el reparto. No hagas
  cambios de rama, restauraciones ni formateos globales mientras la otra sesión
  escribe. Un conflicto exige releer y acordar el alcance, no sobrescribir.
- Asigná también responsable a cada servidor local, puerto y entorno de pruebas.
  Antes de reiniciar un proceso o modificar datos de prueba compartidos,
  coordiná con la otra sesión; dos carpetas no aíslan una misma base de datos.
- Si ambas necesitan modificar zonas que se cruzan, trabajá por turnos o usá
  worktrees separados con ramas distintas. Primero debe existir un repositorio
  Git válido y una base de trabajo acordada. Los worktrees separan archivos;
  después se integran los cambios y QA valida la revisión integrada.
  [Documentación de OpenAI sobre worktrees](https://learn.chatgpt.com/docs/environments/git-worktrees).
- La identidad de la herramienta no cambia la propiedad de los contratos, del
  PRD o del espejo del sprint. Cambiar de sesión no autoriza una nueva fase.

## Mensaje para iniciar agy como revisor de esta plantilla

```text
Estamos trabajando con Codex y agy en este mismo proyecto.
Leé AGENTS.md, docs/protocolo.md y docs/agy-codex.md.
Tu tarea actual es revisar la plantilla en modo de solo lectura.
Revisá README.md y las definiciones de .agents/agents/ y contrastá sus
instrucciones con la ayuda disponible de tu CLI.
Reportá contradicciones o capacidades que no puedas verificar, con archivo y línea.
No modifiques archivos ni actives otras fases. Esta revisión no es QA de producto.
Entregá los hallazgos en tu respuesta para compartirlos con Codex.
```

## Mensaje para asignar una implementación de producto

Completar los campos antes de enviarlo a cualquiera de las dos sesiones:

```text
Leé AGENTS.md, docs/protocolo.md, docs/agy-codex.md y el archivo del rol [ROL].
Implementá el ticket [ID Y ENLACE] en el alcance [RUTAS ASIGNADAS].
Tu etiqueta de sesión es [SESIÓN]. La otra sesión tiene asignado [OTRO ALCANCE].
Verificá las entradas de la fase y los contratos existentes antes de editar.
Al terminar, entregá revisión, archivos afectados, pruebas y resultados,
bloqueos y pendientes. No actives por tu cuenta la siguiente fase.
```
