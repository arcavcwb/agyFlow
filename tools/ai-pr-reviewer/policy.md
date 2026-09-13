# AI PR Reviewer — Política de permisos

## Acceso permitido
- Leer el diff del pull request.
- Leer archivos del repositorio (checkout de solo lectura).
- Emitir un reporte de hallazgos como comentario del PR o archivo local.

## Acceso prohibido
- Modificar archivos del repositorio.
- Hacer commits, pushes o merges.
- Aprobar o rechazar pull requests.
- Aprobar PRD, QA o cualquier fase del protocolo.
- Desplegar a cualquier entorno.
- Sustituir la aprobación humana en cualquier gate.
- Intentar reconstruir valores marcados como credenciales ocultadas.

## Gestión de la API key
- `GEMINI_API_KEY` se configura EXCLUSIVAMENTE como:
  - Secret de GitHub Actions, O
  - Variable de entorno local (no versionada).
- NUNCA debe aparecer en archivos versionados, workflows, logs ni outputs.
- El validador rechaza formas de `GEMINI_API_KEY` hardcodeadas en los archivos
  distribuidos del módulo y su workflow.
- Antes de llamar a Gemini, el script oculta formas comunes de API keys, bearer
  tokens y claves privadas. Esta detección reduce exposición accidental, pero no
  garantiza identificar todos los secretos.

## Tratamiento externo del código
- Al habilitar el módulo, el contenido textual del diff se envía a la API de
  Gemini para su análisis. El responsable del repositorio debe confirmar que
  sus reglas de privacidad y tratamiento de código permiten ese envío.
- El módulo está deshabilitado por defecto mediante `ENABLE_AI_PR_REVIEW`.
- No se debe habilitar en repositorios cuyo código o datos no puedan enviarse al
  proveedor configurado.

## Permisos del workflow de CI
- El workflow necesita `pull-requests: write` para postear el reporte como
  comentario. Esto es una escritura del *workflow*, no del *reviewer*.
  El reviewer en sí sigue siendo de solo lectura: recibe un diff y emite
  texto. La acción de GitHub que postea el comentario es un paso separado.
- `contents: read` para acceder al checkout.
- Con el módulo habilitado, un error de configuración, red o API falla el job:
  un CI verde siempre implica que el reviewer terminó su ejecución.

## Severidades y bloqueo
- Un hallazgo de severidad **critical** produce un verdict **blocked** que
  impide el avance del PR a QA hasta que:
  - Se corrija el hallazgo, O
  - Un humano descarte el hallazgo explícitamente.
- Hallazgos high/medium generan verdict **needs_review** (informativo).
- Hallazgos low/info generan verdict **clean**.
- Un reporte limpio (sin hallazgos) NO equivale a QA aprobado.

## Relación con la auditoría de seguridad
- Esta herramienta y `agy-security-audit` son independientes.
- Ambas cubren categorías similares (autenticación, RLS, Zod, secretos,
  CORS) pero no comparten código ni se sincronizan automáticamente.
- Actualizar una no actualiza la otra.

## Relación con el protocolo
- Esta herramienta es opcional. No forma parte del flujo base de agyFlow.
- No aparece en AGENTS.md ni tiene agent.md propio.
- Su ausencia no afecta la validación base. Si alguno de sus archivos está
  presente, el validador exige que el módulo esté completo y configurado de
  forma coherente.
