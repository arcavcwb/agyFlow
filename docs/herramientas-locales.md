# Herramientas locales y recorrido de ejemplo

Estos comandos ayudan a preparar y revisar declaraciones de evidencia. No ejecutan
agentes, no consultan Plane, no autentican la identidad del aprobador y no despliegan.
La activación humana, la comprobación de fuentes y los límites de `docs/protocolo.md`
continúan siendo obligatorios. Los JSON siguientes son convenciones locales de
agyFlow; no representan campos de API de Plane ni configuración de MCP.

## Ver la demostración

Abrir [el recorrido visual](demo-flujo.html), o ejecutar:

```bash
python3 scripts/demo_workflow.py
```

El ejemplo usa una historia de reserva de citas con camino exitoso, error de datos,
concurrencia y ausencia de horarios. Genera fixtures en una carpeta temporal que se
elimina al terminar. Las aprobaciones, referencias de diseño y dictámenes son
**simulados**, no acreditan entrevistas, implementación, QA o despliegue de un producto.
El código del comprobador sí se ejecuta y muestra cómo bloquea rechazos, revisiones
antiguas y cambios de alcance. Para regenerar la vista:

```bash
python3 scripts/demo_workflow.py --html docs/demo-flujo.html
```

## Inicializar un proyecto receptor

El m\u00e9todo recomendado es `npx degit` desde GitHub:

```bash
npx degit arcavcwb/agyFlow mi-proyecto
cd mi-proyecto
python3 scripts/validate_squad.py
```

`degit` copia el contenido del repo sin historial git y omitiendo los archivos
internos declarados en `.degitignore`. Es equivalente a `setup_receiver.py`
pero en un solo comando y sin depender de Python ni de una copia local de agyFlow.

## Inicializar sin perder archivos (alternativa)

Si el proyecto receptor ya existe y prefer\u00eds fusionar los archivos de agyFlow
en lugar de scaffoldear desde cero, us\u00e1 `setup_receiver.py`:

```bash
python3 /ruta/a/agyFlow/scripts/setup_receiver.py --target /ruta/al/proyecto --frontend next --backend node --db none --dry-run
python3 /ruta/a/agyFlow/scripts/setup_receiver.py --target /ruta/al/proyecto --frontend next --backend node --db none
```

Las opciones de stack son preferencias, no instalaciones ni decisiones aprobadas.
Si se omiten, quedan por definir. Se distribuyen roles, skills, guías, plantillas,
scripts, tests y configuración de CI. Las reglas de `.gitignore` se integran;
la configuración MCP activa y las credenciales no se copian.

- Se copian archivos faltantes dentro de directorios existentes.
- Los conflictos se conservan por defecto y requieren integración manual.
- `--force` actualiza archivos distribuidos con respaldo previo en
  `.agyflow-backups/setup-*/`; no elimina directorios ni archivos ajenos al paquete.
- Los archivos `PRD.md`, `sprint_actual.md` y los borradores generados existentes
  se conservan incluso con `--force`. `architecture.md` nunca se escribe.
- Se genera `architecture.proposed.md` para revisión humana. No se inventa
  `BaseEntity` ni se crean contratos para superar la validación.
- Los destinos dentro del árbol de la plantilla y los enlaces simbólicos en rutas
  de escritura se rechazan. La copia es atómica por archivo; no es una transacción
  del proyecto completo. Ante una interrupción se puede revisar y volver a ejecutar.

El receptor recién inicializado puede pasar el validador de **paquete**. Todavía
necesita las entradas reales para `--project` y las fases de producto.

## Evidencia explícita de entrega

`handoff.py prompt` prepara instrucciones; `template` mantiene el formato narrativo
`templates/entrega.md`. `check` ahora recibe JSON, no intenta deducir aprobaciones
buscando palabras en un reporte.

Copiar `templates/handoff.json` a `handoff.json` del receptor y completar según
la entrega asignada. Esta exportación opcional la prepara el coordinador dentro de
su alcance, a partir de las fuentes vigentes; no crea un segundo dueño del estado.
Cada entrada requiere `status`, `reference` y `revision` identificables:

| Rol | Claves requeridas en `inputs` |
|---|---|
| PO | `brief` |
| Scrum | `prd_approval`, `plane` |
| Designer | `architecture`, `ticket`, `design_reference` |
| Backend | `architecture`, `ticket` |
| Frontend | `architecture`, `ticket`, `contracts`, `design` |
| QA final | `architecture`, `ticket`, `candidate`, `criteria`, `environment`, `tests` |
| DevOps: entrega | `architecture`, `ticket`, `qa`, `artifact` |
| Automation | `architecture`, `ticket`, `plane`, `state_owner` |

`status` debe ser `ready`, excepto `qa` y `prd_approval`, que requieren `approved`.
Un `pending`, `rejected` o `blocked` impide la entrega que lo requiere. Las entradas
`contracts`, `design` y `design_reference` permiten `not_applicable` con `reason`.
Para preparación de QA o DevOps usar `phase: "preparation"`: requiere arquitectura
y ticket, y no autoriza despliegue. El valor predeterminado es `delivery`.

```bash
python3 scripts/handoff.py check --role frontend-dev-agent --input handoff.json
```

Para QA final o entrega de DevOps se requiere además una candidata independiente:

```bash
python3 scripts/handoff.py check --role devops-agent --input handoff.json --ticket PROJ-1 --revision REVISION-VIGENTE --qa-run EJECUCION-VIGENTE
```

El JSON lleva esos mismos `ticket`, `revision` y `qa_run`. Las entradas `candidate`,
`artifact` y `qa` deben referenciar la revisión candidata; `qa` además declara su
`qa_run`, `pending_checks: []` y `blockers: []`. Cambiar la candidata exige actualizar
la evidencia; escribir `approved` no ejecuta pruebas ni valida el contenido de una URL.
Antes del despliegue DevOps debe comprobar el artefacto y las fuentes reales como
establece el protocolo. Los parámetros del comando son declaraciones del operador.

## Diagnóstico del pipeline y aprobación del PRD

```bash
python3 scripts/pipeline.py --root /ruta/al/proyecto check-prd
python3 scripts/pipeline.py --root /ruta/al/proyecto status
python3 scripts/pipeline.py --root /ruta/al/proyecto advance
```

`check-prd` revisa cuatro secciones numeradas por historia, con Dado/Cuando/Entonces
en cada una y sin campos de ejemplo entre corchetes. Es un control estructural local,
no un parser completo de Gherkin ni una evaluación de la calidad de los criterios.

`advance` solo explica la próxima acción. Para registrar una aprobación humana
**ya otorgada** al contenido actual del PRD:

```bash
python3 scripts/pipeline.py --root /ruta/al/proyecto approve-prd --person "PERSONA REAL" --scope "ALCANCE APROBADO" --evidence "REFERENCIA A LA INSTRUCCIÓN HUMANA"
```

El registro incluye fecha UTC y SHA-256 del PRD, en
`.agyflow/approvals/prd-<sha256>.json`. No altera PRD ni arquitectura y no activa
agentes. No sobrescribe un registro existente. Cambiar el contenido del PRD exige
una aprobación nueva; la metadata registra la declaración, no autentica la identidad.

Tras comprobar estructura y registro de PRD, `status` requiere `architecture.md`
y una entrega explícita en `handoff.json`. Para QA/DevOps compara además
`candidate.json` (formato en `templates/candidate.json`) con la entrega. El responsable
de integración identifica la candidata y el coordinador refleja la información
vigente: estos archivos son snapshots locales, no una sincronización automática.
Un reporte narrativo viejo no determina la siguiente fase. El comando devuelve 1
ante evidencia malformada/inconsistente; las fases pendientes normales se muestran
con su actor propuesto. No usar el código de salida de `status` como permiso de deploy.
