#!/usr/bin/env python3
"""Assist handoffs between agyFlow squad agents according to protocol and agy-codex guidelines."""

import argparse
from pathlib import Path
import sys

AGENTS = {
    "po-agent", "scrum-master-agent", "designer-agent", "backend-dev-agent",
    "frontend-dev-agent", "qa-agent", "devops-agent", "automation-agent",
}

PRECONDITIONS = {
    "po-agent": ["brief"],
    "scrum-master-agent": ["prd", "aprobac"],
    "designer-agent": ["ticket"],
    "backend-dev-agent": ["ticket"],
    "frontend-dev-agent": ["contrato", "list"],
    "qa-agent": ["revisi"],
    "devops-agent": ["qa", "aproba"],
    "automation-agent": ["plane"],
}


def build_prompt(target_role: str, ticket: str, routes: str,
                 from_role: str = None, session: str = "agy-1",
                 other_session: str = "Ninguno asignado", context: str = None) -> str:
    if target_role not in AGENTS:
        raise ValueError(f"Rol desconocido: {target_role}. Roles válidos: {', '.join(sorted(AGENTS))}")

    lines = [
        f"Leé AGENTS.md, docs/protocolo.md, docs/agy-codex.md, docs/stack.md y el archivo del rol .agents/agents/{target_role}/agent.md.",
        f"Tu rol asignado es [{target_role}].",
        f"Implementá el ticket [{ticket}] en el alcance de rutas asignado: [{routes}].",
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


def check_preconditions(role: str, text: str) -> tuple[bool, list[str]]:
    if role not in AGENTS:
        return False, [f"Rol desconocido: {role}"]

    required_keywords = PRECONDITIONS.get(role, [])
    lowered = text.lower()
    missing = []

    for kw in required_keywords:
        if kw not in lowered:
            missing.append(kw)

    if missing:
        return False, [f"Faltan evidencias o palabras clave requeridas para {role}: {missing}"]
    return True, []


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
    check_parser.add_argument("--input", dest="input_file", help="Ruta al archivo de entrega o sprint a comprobar")

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
        if args.input_file:
            content = Path(args.input_file).read_text(encoding="utf-8")
        else:
            content = sys.stdin.read()
        ok, errors = check_preconditions(args.role, content)
        if ok:
            print(f"OK: Precondiciones satisfechas para {args.role}.")
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
