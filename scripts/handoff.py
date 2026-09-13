#!/usr/bin/env python3
"""Assist handoffs between agyFlow squad agents according to protocol and agy-codex guidelines."""

import argparse
import json
from pathlib import Path
import sys

AGENTS = {
    "po-agent", "scrum-master-agent", "designer-agent", "backend-dev-agent",
    "frontend-dev-agent", "qa-agent", "devops-agent", "automation-agent",
}

# These are local evidence fields, not API fields from Plane or a client runtime.
PRECONDITIONS = {
    "po-agent": ["brief"],
    "scrum-master-agent": ["prd_approval", "plane"],
    "designer-agent": ["architecture", "ticket", "design_reference"],
    "backend-dev-agent": ["architecture", "ticket"],
    "frontend-dev-agent": ["architecture", "ticket", "contracts", "design"],
    "qa-agent": ["architecture", "ticket", "candidate", "criteria", "environment", "tests"],
    "devops-agent": ["architecture", "ticket", "qa", "artifact"],
    "automation-agent": ["architecture", "ticket", "plane", "state_owner"],
}


def load_evidence(text):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"Campo JSON duplicado: {key}")
            result[key] = value
        return result
    try:
        data = json.loads(text, object_pairs_hook=unique)
    except (ValueError, TypeError) as exc:
        raise ValueError("Se requiere evidencia JSON explícita; el texto libre no acredita precondiciones.") from exc
    if not isinstance(data, dict) or type(data.get("schema_version")) is not int or data["schema_version"] != 1:
        raise ValueError("Se requiere un objeto con schema_version: 1.")
    return data


def specified(value):
    return (isinstance(value, str) and bool(value.strip())
            and value.strip().lower() not in {"pendiente", "por asignar", "unknown", "todo"})


def build_prompt(target_role: str, ticket: str, routes: str,
                 from_role: str = None, session: str = "agy-1",
                 other_session: str = "Ninguno asignado", context: str = None) -> str:
    if target_role not in AGENTS:
        raise ValueError(f"Rol desconocido: {target_role}. Roles válidos: {', '.join(sorted(AGENTS))}")

    lines = [
        f"Leé AGENTS.md, docs/protocolo.md, docs/agy-codex.md, docs/stack.md y el archivo del rol .agents/agents/{target_role}/agent.md.",
        f"Tu rol asignado es [{target_role}].",
        f"Ejecutá la tarea de tu rol para [{ticket}] en el alcance asignado: [{routes}].",
        f"Tu etiqueta de sesión es [{session}]. La otra sesión tiene asignado: [{other_session}].",
    ]

    if from_role:
        lines.append(f"Entrega previa procedente de: [{from_role}].")

    if context:
        lines.append(f"Contexto o revisión de entrada:\n{context.strip()}")

    lines.extend([
        "Verificá las entradas de la fase y los contratos existentes antes de editar.",
        "Al terminar, entregá tu respuesta usando la estructura de templates/entrega.md (revisión, archivos afectados, comprobaciones, bloqueos y pendientes).",
        "No actives por tu cuenta la siguiente fase.",
    ])

    return "\n".join(lines)


def check_preconditions(role: str, text: str, *, revision=None, qa_run=None, ticket=None) -> tuple[bool, list[str]]:
    if role not in AGENTS:
        return False, [f"Rol desconocido: {role}"]
    try:
        data = load_evidence(text)
    except ValueError as exc:
        return False, [str(exc)]
    errors = []
    if data.get("target_role") != role:
        errors.append("target_role no coincide con el destinatario.")
    if not specified(data.get("ticket")):
        errors.append("Falta ticket o identificador del encargo.")
    if ticket is not None and data.get("ticket") != ticket:
        errors.append("El ticket no coincide con la candidata vigente.")
    if not specified(data.get("revision")):
        errors.append("Falta revisión de entrada.")
    inputs = data.get("inputs")
    if not isinstance(inputs, dict):
        return False, errors + ["inputs debe ser un objeto."]
    phase = data.get("phase", "delivery")
    if not isinstance(phase, str) or phase not in {"delivery", "preparation"} or (phase == "preparation" and role not in {"qa-agent", "devops-agent"}):
        return False, errors + ["phase inválida para el rol."]
    required = PRECONDITIONS[role]
    if phase == "preparation":
        required = ["architecture", "ticket"]
    for name in required:
        item = inputs.get(name)
        if not isinstance(item, dict):
            errors.append(f"Falta evidencia: {name}.")
            continue
        if name in {"contracts", "design", "design_reference"} and item.get("status") == "not_applicable":
            if not specified(item.get("reason")):
                errors.append(f"{name}: no aplica requiere motivo.")
            continue
        expected = "approved" if name in {"qa", "prd_approval"} else "ready"
        if item.get("status") != expected:
            errors.append(f"{name}: estado requerido {expected}; recibido {item.get('status')!r}.")
        if not specified(item.get("reference")) or not specified(item.get("revision")):
            errors.append(f"{name}: requiere reference y revision identificables.")
    # Compare with an independent candidate supplied by the caller, never with an old report in the prose.
    if phase == "delivery" and role in {"qa-agent", "devops-agent"}:
        if not specified(revision) or not specified(qa_run) or not specified(ticket):
            errors.append("Se requiere candidata externa: ticket, revision y qa_run vigentes.")
        if data.get("revision") != revision or data.get("qa_run") != qa_run:
            errors.append("Revisión o ejecución QA desactualizada.")
        for name in (["qa", "artifact"] if role == "devops-agent" else ["candidate"]):
            item = inputs.get(name, {})
            if not isinstance(item, dict):
                continue
            if item.get("revision") != revision:
                errors.append(f"{name}: no corresponde a la revisión candidata.")
            if name == "qa":
                if item.get("qa_run") != qa_run:
                    errors.append("qa: ejecución desactualizada.")
                if item.get("pending_checks") != [] or item.get("blockers") != []:
                    errors.append("qa: declarar listas vacías de pending_checks y blockers para entregar.")
    return not errors, errors


def get_template(role: str = None, session: str = "agy-1") -> str:
    template_path = Path(__file__).resolve().parents[1] / "templates/entrega.md"
    content = template_path.read_text(encoding="utf-8") if template_path.exists() else ""
    if role:
        content = content.replace("Rol y etiqueta de sesión:", f"Rol y etiqueta de sesión: {role} ({session})")
    return content


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: prompt
    prompt_parser = subparsers.add_parser("prompt", help="Generar prompt de handoff para activar el siguiente agente")
    prompt_parser.add_argument("--to", required=True, dest="target_role", help="Rol destinatario (ej. frontend-dev-agent)")
    prompt_parser.add_argument("--ticket", required=True, help="ID y descripción/enlace del ticket")
    prompt_parser.add_argument("--routes", required=True, help="Rutas asignadas exclusivamente al agente")
    prompt_parser.add_argument("--from", dest="from_role", default=None, help="Rol que realizó la entrega previa")
    prompt_parser.add_argument("--session", default="agy-1", help="Etiqueta de la sesión actual (default: agy-1)")
    prompt_parser.add_argument("--other-session", default="Ninguno asignado", help="Alcance de la sesión paralela")
    prompt_parser.add_argument("--context", default=None, help="Contexto adicional o entregas previas")

    # Subcommand: check
    check_parser = subparsers.add_parser("check", help="Verificar precondiciones de entrada para un rol")
    check_parser.add_argument("--role", required=True, help="Rol que se quiere activar")
    check_parser.add_argument("--input", dest="input_file", help="Archivo JSON de evidencias; por defecto stdin")
    check_parser.add_argument("--revision", help="Revisión candidata vigente (QA y despliegue)")
    check_parser.add_argument("--qa-run", help="Ejecución QA vigente")
    check_parser.add_argument("--ticket", help="Ticket de la candidata vigente")

    # Subcommand: template
    template_parser = subparsers.add_parser("template", help="Emitir template de entrega.md pre-rellenado")
    template_parser.add_argument("--role", default=None, help="Rol asignado para pre-completar")
    template_parser.add_argument("--session", default="agy-1", help="Etiqueta de sesión")

    args = parser.parse_args()

    if args.command == "prompt":
        try:
            print(build_prompt(
                target_role=args.target_role,
                ticket=args.ticket,
                routes=args.routes,
                from_role=args.from_role,
                session=args.session,
                other_session=args.other_session,
                context=args.context,
            ))
        except ValueError as err:
            print(f"ERROR: {err}", file=sys.stderr)
            return 1

    elif args.command == "check":
        try:
            content = Path(args.input_file).read_text(encoding="utf-8") if args.input_file else sys.stdin.read()
        except (OSError, UnicodeError) as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1
        ok, errors = check_preconditions(args.role, content, revision=args.revision, qa_run=args.qa_run, ticket=args.ticket)
        if ok:
            print(f"OK: Declaraciones consistentes para {args.role}; verificar fuentes y permisos antes de actuar.")
            return 0
        else:
            for err in errors:
                print(f"ERROR: {err}", file=sys.stderr)
            return 1

    elif args.command == "template":
        print(get_template(role=args.role, session=args.session))

    return 0


if __name__ == "__main__":
    sys.exit(main())
