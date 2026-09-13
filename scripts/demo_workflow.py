#!/usr/bin/env python3
"""Run an isolated, explicitly simulated reservation-story walkthrough. No network or deployment."""
import argparse
import html
import json
from pathlib import Path
import tempfile

from handoff import PRECONDITIONS, check_preconditions
from pipeline import detect_phase, record_prd_approval
from setup_receiver import scaffold_receiver

PRD = '''# PRD — SIMULACIÓN: reservar una cita

Este documento es un ejemplo educativo, no un requisito aprobado de un producto.

### [US-01] Reservar un horario disponible
Como cliente quiero elegir un horario para obtener una reserva confirmada.

1. Happy Path:
   Dado un horario disponible, cuando confirmo mis datos, entonces veo la confirmación.
2. Sad Path / Error:
   Dado un dato obligatorio ausente, cuando confirmo, entonces veo el error y conservo lo escrito.
3. Edge Case:
   Dado un horario ocupado por otra reserva, cuando confirmo, entonces puedo elegir otro sin duplicar reservas.
4. Estado Vacío / Carga:
   Dado que no hay horarios, cuando consulto una fecha, entonces veo un estado vacío y puedo cambiarla.
'''


def evidence(role, revision='demo-rev-1', qa_run='demo-qa-1'):
    """Synthetic declarations for examples/tests only; not approval or execution evidence."""
    inputs = {name: {'status': 'approved' if name in {'qa', 'prd_approval'} else 'ready',
                     'reference': f'SIMULACIÓN/{name}', 'revision': revision}
              for name in PRECONDITIONS[role]}
    if 'qa' in inputs:
        inputs['qa'].update(qa_run=qa_run, blockers=[], pending_checks=[])
    return dict(schema_version=1, target_role=role, ticket='SIM-US-01', revision=revision,
                qa_run=qa_run, inputs=inputs)


def run_demo():
    events = []
    with tempfile.TemporaryDirectory(prefix='agyflow-demo-') as directory:
        root = Path(directory) / 'receiver'
        scaffold_receiver(root, frontend='next', backend='node', db='none', copy_squad=False)
        events.append(('Inicialización', 'Conserva gobernanza',
                       f'architecture.md existe: {(root / "architecture.md").exists()}; se genera solo architecture.proposed.md.'))
        (root / 'PRD.md').write_text(PRD, encoding='utf-8')
        def status(title):
            phase, detail, actor = detect_phase(root)
            events.append((title, phase, detail + ' Actor propuesto: ' + actor))
        status('Historia con cuatro escenarios; todavía sin aprobación')
        record_prd_approval(root, 'PERSONA FICTICIA — SIMULACIÓN', 'US-01 de ejemplo', 'Evidencia sintética del recorrido educativo')
        status('Aprobación simulada guardada; falta decisión de arquitectura')
        (root / 'architecture.md').write_text('# SIMULACIÓN de entrada humana\nSin aplicación ni despliegue real.\n')
        status('Planificar y comprobar Plane antes del trabajo real')
        for role, title in [('backend-dev-agent', 'Declaración simulada: definir contratos'),
                            ('designer-agent', 'Declaración simulada: preparar diseño'),
                            ('frontend-dev-agent', 'Declaración simulada: implementar interfaz')]:
            (root / 'handoff.json').write_text(json.dumps(evidence(role)))
            status(title)
        candidate = dict(schema_version=1, ticket='SIM-US-01', revision='demo-rev-1', qa_run='demo-qa-1')
        (root / 'candidate.json').write_text(json.dumps(candidate))
        data = evidence('qa-agent')
        (root / 'handoff.json').write_text(json.dumps(data))
        status('Candidata y ejecución identificadas para QA')
        data = evidence('devops-agent')
        data['inputs']['qa']['status'] = 'rejected'
        (root / 'handoff.json').write_text(json.dumps(data))
        status('Rechazo vigente: bloquear entrega a Staging')
        data['inputs']['qa']['status'] = 'approved'
        (root / 'handoff.json').write_text(json.dumps(data))
        status('Aprobación simulada: consistencia para revisar entrega; no se despliega')
        candidate.update(revision='demo-rev-2', qa_run='demo-qa-2')
        (root / 'candidate.json').write_text(json.dumps(candidate))
        status('Nueva candidata: el QA anterior deja de servir')
        (root / 'PRD.md').write_text(PRD + '\nCambio de alcance simulado.\n')
        status('Cambio de PRD: requiere nueva aprobación')
        ok, errors = check_preconditions('devops-agent', 'QA no aprobado. No desplegar.')
        events.append(('Texto ambiguo', 'BLOCKED' if not ok else 'ERROR', '; '.join(errors)))
    return events


def report(events):
    cards = ''.join(f'<article><span class="state">{html.escape(state)}</span><h2>{html.escape(title)}</h2><p>{html.escape(detail)}</p></article>'
                    for title, state, detail in events)
    return '''<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>agyFlow · Demostración del flujo</title><style>
*{box-sizing:border-box}body{margin:0;background:#f1f5f8;color:#183044;font:17px/1.6 system-ui,sans-serif}main{max-width:1050px;margin:auto;padding:48px 24px}header{margin-bottom:32px}h1{font-size:clamp(30px,5vw,48px);line-height:1.15}h2{font-size:20px;margin:10px 0}p{margin:8px 0}.badge{color:#715320;background:#fff0c9;padding:8px 14px;border-radius:8px;display:inline-block}section{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:16px}article{background:white;padding:24px;border:1px solid #d5e0e7;border-radius:14px}.state{font:14px ui-monospace,monospace;color:#166657;overflow-wrap:anywhere}footer{margin-top:32px;color:#536979}code{background:#e0e8ee;padding:3px 7px;border-radius:4px}
</style><main><header><span class="badge">SIMULACIÓN LOCAL · sin agentes, conexiones ni despliegues</span><h1>Una historia, controles visibles.</h1><p>Ejemplo: reservar una cita. Este recorrido ejecuta los comprobadores de agyFlow con datos ficticios. Las declaraciones de diseño, implementación y QA son simuladas; no acreditan un producto construido.</p><p>Flujo conceptual del usuario: elegir servicio → consultar horario → confirmar datos → ver reserva. Estados: carga, vacío, error y horario ocupado.</p></header><section>''' + cards + '''</section><footer><p>La aprobación se vincula al SHA-256 del PRD. QA se compara con ticket, revisión y ejecución vigentes. Cada fase real conserva su activación humana y sus fuentes de evidencia.</p><p>Repetir: <code>python3 scripts/demo_workflow.py</code></p></footer></main></html>'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--html', type=Path, help='Guardar informe visual de la simulación')
    args = parser.parse_args()
    events = run_demo()
    print('SIMULACIÓN LOCAL — no acredita trabajo ni aprobaciones reales.\n')
    for title, state, detail in events:
        print(f'{title}\n  {state}: {detail}\n')
    if args.html:
        args.html.parent.mkdir(parents=True, exist_ok=True)
        args.html.write_text(report(events), encoding='utf-8')
        print(f'Informe: {args.html}')


if __name__ == '__main__':
    main()
