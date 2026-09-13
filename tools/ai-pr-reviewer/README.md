# AI PR Reviewer

Herramienta opcional de revisión automática de PRs para agyFlow.

## Archivos
- `review_agent.py` — Script que envía el diff a Gemini y parsea hallazgos.
- `prompt.md` — Prompt del sistema con formato JSON obligatorio.
- `policy.md` — Política de permisos y restricciones.
- `requirements.txt` — Dependencia pinneada.

## Uso local

```bash
pip install -r tools/ai-pr-reviewer/requirements.txt
export GEMINI_API_KEY="..."
git diff main...HEAD > /tmp/pr.diff
python3 tools/ai-pr-reviewer/review_agent.py --diff /tmp/pr.diff
```

## Opciones

| Flag | Default | Descripción |
|------|---------|-------------|
| `--diff` | (requerido) | Archivo con el diff |
| `--output` | stdout | Reporte markdown |
| `--json-output` | (ninguno) | Respuesta JSON raw para debugging |
| `--model` | `gemini-3.6-flash` | Modelo a usar (o env `GEMINI_MODEL`) |
| `--max-diff-chars` | 50000 | Presupuesto máximo antes de marcar revisión parcial |

## Exit codes

| Código | Significado |
|--------|-------------|
| 0 | Clean o needs_review — sin hallazgos críticos |
| 1 | Error — key faltante, API falló, respuesta inválida |
| 2 | Blocked — al menos un hallazgo crítico |
| 3 | Partial — el diff excedió el presupuesto de contexto |

## Uso en CI

Ver `docs/ai-pr-reviewer.md` y `.github/workflows/ai-pr-review.yml`.

## Límites

- Solo lectura. No modifica archivos ni aprueba nada.
- No sustituye QA, aprobación humana ni despliegue.
- Lockfiles, diagramas editables, binarios y archivos minificados se excluyen del diff.
- Formas comunes de credenciales se ocultan antes del envío.
- Diffs largos se truncan y devuelven estado parcial; no generan un gate verde.
- El código visible del diff se procesa externamente mediante la API de Gemini;
  revisá la política del proyecto antes de habilitar el módulo.
- Ver `policy.md` para las reglas completas.
