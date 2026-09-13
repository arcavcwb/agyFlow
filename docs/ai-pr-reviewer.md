# AI PR Reviewer

## Propósito

Revisión automática opcional de PRs usando Gemini. Se ubica entre
implementación y QA como gate de calidad complementario.

## Posición en el flujo

```text
Implementación → PR candidata → [AI PR Reviewer] → QA → DevOps
```

La fase es **opcional**. Sin ella, el flujo sigue siendo:
Implementación → QA → DevOps.

## Permisos y límites

### El reviewer (script)
- Solo lectura: recibe el diff generado por el workflow.
- Emite un reporte JSON estructurado con hallazgos y un verdict.
- NO modifica archivos, NO hace commits, NO aprueba nada.
- Un resultado limpio NO equivale a QA aprobado.
- El esquema limita y valida los hallazgos; conteos y verdict se calculan
  localmente a partir de las severidades aceptadas.

### El workflow de CI
- Tiene `pull-requests: write` para postear el reporte como comentario.
- El reviewer en sí no usa este permiso; lo usa el step de GitHub Script.

### Bloqueo por hallazgos críticos
- Verdict `blocked` (≥1 hallazgo critical) → el job de CI falla.
- Un error técnico o de configuración también falla el job y no se presenta
  como una revisión satisfactoria.
- Un diff que exceda el presupuesto produce una revisión parcial y falla el job
  hasta dividir el PR o definir una revisión humana alternativa.
- El PR no debería avanzar a QA sin corrección o decisión humana.
- Verdicts `needs_review` y `clean` no bloquean el CI.

## Configuración

### GitHub Actions
1. Agregar `GEMINI_API_KEY` como **secret** del repositorio.
2. Agregar variable `ENABLE_AI_PR_REVIEW` = `true` en Settings → Variables.
3. El workflow `.github/workflows/ai-pr-review.yml` se activa en PRs.

El módulo queda deshabilitado mientras la variable no sea exactamente `true`.
Los secrets de GitHub no se entregan normalmente a workflows disparados desde
forks; en esos PR el job fallará si el módulo está habilitado. No cambies el
evento a `pull_request_target`, porque ejecutar código del PR con secretos
ampliaría la superficie de ataque.

### Ejecución local

```bash
pip install -r tools/ai-pr-reviewer/requirements.txt
export GEMINI_API_KEY="tu-key-aquí"
git diff main...HEAD > /tmp/pr.diff
python3 tools/ai-pr-reviewer/review_agent.py --diff /tmp/pr.diff
```

## Filtrado del diff

Se excluyen automáticamente:
- Lockfiles (`*.lock`, `*-lock.json`, `*-lock.yaml`)
- Archivos minificados (`*.min.js`, `*.min.css`)
- Source maps (`*.map`)
- Escenas editables (`*.excalidraw`)
- Binarios/assets (`*.png`, `*.jpg`, `*.gif`, `*.svg`, `*.ico`,
  `*.woff`, `*.woff2`, `*.ttf`, `*.eot`)

Diffs mayores a 50.000 caracteres (configurable con `--max-diff-chars`) se
truncan. El reporte indica que la revisión es parcial y devuelve código `3`; el
workflow no permite que esa muestra produzca un gate verde. El límite aproxima
el objetivo de 8k–15k tokens de entrada sin depender de un tokenizador concreto.

Antes del envío se ocultan formas comunes de API keys, bearer tokens y claves
privadas. Los marcadores permanecen visibles para que el modelo pueda reportar
el riesgo de haber versionado una credencial. Esta protección es defensiva y no
reemplaza un detector especializado de secretos.

## Privacidad

Al habilitar el módulo, el diff textual se transmite a la API de Gemini. El
responsable debe comprobar que las políticas del proyecto permiten enviar ese
código al proveedor. Para repositorios incompatibles con ese tratamiento,
mantené `ENABLE_AI_PR_REVIEW` deshabilitada.

## Relación con la auditoría de seguridad

Esta herramienta y la skill `agy-security-audit` son **independientes**.
Ambas cubren categorías similares (autenticación, RLS, secretos, CORS)
pero no comparten código ni prompt. Actualizar una no actualiza la otra.

## Relación con el protocolo

- Módulo opcional — no forma parte del flujo base de agyFlow.
- No aparece en `AGENTS.md` ni tiene `agent.md` propio.
- Su ausencia no afecta la validación base; una instalación parcial sí se
  considera inválida.
- Ver `tools/ai-pr-reviewer/policy.md` para la política completa.
