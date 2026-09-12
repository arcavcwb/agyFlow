#!/usr/bin/env python3
"""Validate squad packaging without network calls, credentials or mutations."""

import argparse
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlparse


AGENTS = {
    "po-agent", "scrum-master-agent", "designer-agent", "backend-dev-agent",
    "frontend-dev-agent", "qa-agent", "devops-agent", "automation-agent",
}


def frontmatter(content, relative, errors):
    """Read the flat scalar header used by this template, not arbitrary YAML."""
    match = re.match(r"\A---\n(.*?)\n---(?:\n|$)", content, re.S)
    if not match:
        errors.append(f"{relative}: falta frontmatter delimitado")
        return {}
    fields = {}
    for line in match.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, separator, value = line.partition(":")
        if not separator or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", key) or key in fields:
            errors.append(f"{relative}: campo inválido o duplicado: {key}")
            continue
        fields[key] = value.strip().strip('"\'')
    return fields


def validate_skills(root, read, errors):
    relative = "config/skills.json"
    raw = read(relative)
    if not raw:
        return
    try:
        registry = json.loads(raw)
    except json.JSONDecodeError:
        errors.append(f"{relative}: JSON inválido")
        return
    if not isinstance(registry, dict):
        errors.append(f"{relative}: se requiere un objeto")
        return
    if type(registry.get("schema_version")) is not int or registry["schema_version"] != 1:
        errors.append(f"{relative}: schema_version no soportado")
    sections = {}
    for section in ("agents", "bundled", "external"):
        value = registry.get(section)
        if not isinstance(value, dict):
            errors.append(f"{relative}: {section} debe ser un objeto")
            value = {}
        sections[section] = value
    assignments, bundled, external = (sections[k] for k in ("agents", "bundled", "external"))
    if set(assignments) != AGENTS:
        errors.append(f"{relative}: asignaciones incompletas o agentes desconocidos")
    used_core = set()
    for name, assignment in assignments.items():
        if not isinstance(assignment, dict):
            errors.append(f"{relative}: asignación inválida: {name}")
            continue
        core = assignment.get("core")
        if not isinstance(core, str) or core not in bundled:
            errors.append(f"{relative}: core desconocida: {name}")
        else:
            if core in used_core:
                errors.append(f"{relative}: core asignada a varios agentes: {core}")
            used_core.add(core)
            content = read(f".agents/agents/{name}/agent.md")
            expected = f".agents/skills/{core}/SKILL.md"
            if expected not in content:
                errors.append(f"{name}: falta referencia a su skill {core}")
        optional = assignment.get("optional")
        if not isinstance(optional, list) or not all(isinstance(k, str) for k in optional):
            errors.append(f"{relative}: optional inválido: {name}")
        elif len(set(optional)) != len(optional) or any(k not in external for k in optional):
            errors.append(f"{relative}: optional duplicado o desconocido: {name}")
    if set(bundled) != used_core:
        errors.append(f"{relative}: skills incluidas sin asignación válida")
    for skill, entry in bundled.items():
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", skill) or len(skill) > 64:
            errors.append(f"{relative}: nombre de skill inválido: {skill}")
            continue
        if not isinstance(entry, dict):
            errors.append(f"{relative}: entrada bundled inválida: {skill}")
            continue
        path = entry.get("path")
        expected = f".agents/skills/{skill}/SKILL.md"
        if path != expected:
            errors.append(f"{relative}: ruta no portable o incorrecta: {skill}")
            continue
        version = entry.get("version")
        if not isinstance(version, str) or not re.fullmatch(r"\d+\.\d+\.\d+", version):
            errors.append(f"{relative}: versión bundled inválida: {skill}")
        content = read(path)
        if content:
            fields = frontmatter(content, path, errors)
            if fields.get("name") != skill or not fields.get("description"):
                errors.append(f"{path}: name o description inválido")
    for skill, entry in external.items():
        if not isinstance(entry, dict):
            errors.append(f"{relative}: entrada external inválida: {skill}")
            continue
        source, condition = entry.get("source"), entry.get("when")
        try:
            url = urlparse(source) if isinstance(source, str) else None
            valid_url = url and url.scheme == "https" and url.hostname and not url.username
        except ValueError:
            valid_url = False
        if not valid_url or not isinstance(condition, str) or not condition.strip():
            errors.append(f"{relative}: origen o condición externa inválidos: {skill}")
        status, revision = entry.get("status"), entry.get("revision")
        if status == "candidate":
            valid = revision is None
        elif status == "pinned":
            valid = isinstance(revision, str) and bool(re.fullmatch(r"[0-9a-f]{40}", revision))
        else:
            valid = False
        if not valid:
            errors.append(f"{relative}: estado o revisión externa inválidos: {skill}")


def validate(root: Path, project: bool) -> list[str]:
    root = root.resolve()
    errors = []

    def read(relative):
        try:
            path = root / relative
            if not path.resolve().is_relative_to(root):
                errors.append(f"{relative}: ruta fuera de la raíz del paquete")
                return ""
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError, RuntimeError) as exc:
            errors.append(f"{relative}: no se pudo leer ({exc})")
            return ""
        if not content.strip():
            errors.append(f"{relative}: archivo vacío")
        return content

    index = read("AGENTS.md")
    for relative in (
        "README.md", "docs/protocolo.md", "docs/agy-codex.md", "docs/skills.md",
        "docs/stack.md", "templates/PRD.md", "templates/sprint_actual.md",
        "templates/bug_report.md", "templates/entrega.md", "templates/project_setup.md",
    ):
        read(relative)

    directory = root / ".agents/agents"
    discovered = {p.parent.name for p in directory.glob("*/agent.md")}
    for name in sorted(AGENTS - discovered):
        errors.append(f"Agente faltante: .agents/agents/{name}/agent.md")
    for name in sorted(discovered - AGENTS):
        errors.append(f"Agente fuera del índice esperado: {name}")
    for name in sorted(AGENTS & discovered):
        relative = f".agents/agents/{name}/agent.md"
        content = read(relative)
        fields = frontmatter(content, relative, errors)
        if fields.get("name") != name or fields.get("subagent") != "true":
            errors.append(f"{relative}: name o subagent no coincide")
        if fields.get("mainAgent") == "true":
            errors.append(f"{relative}: mainAgent no está permitido en este squad")
        if not fields.get("description"):
            errors.append(f"{relative}: falta description")
        if "docs/protocolo.md" not in content:
            errors.append(f"{relative}: no referencia el protocolo")
        if "docs/stack.md" not in content:
            errors.append(f"{relative}: no referencia stack.md")
        if "templates/entrega.md" not in content:
            errors.append(f"{relative}: no referencia templates/entrega.md")
        if f"`{name}`" not in index:
            errors.append(f"AGENTS.md: falta {name}")

    validate_skills(root, read, errors)

    relative = ".agents/mcp_config.example.json"
    raw = read(relative)
    if raw:
        try:
            config = json.loads(raw)
            servers = config.get("mcpServers") if isinstance(config, dict) else None
            if not isinstance(servers, dict) or not servers:
                errors.append(f"{relative}: falta objeto mcpServers no vacío")
            else:
                for name, server in servers.items():
                    if not isinstance(server, dict):
                        errors.append(f"{relative}: servidor inválido: {name}")
                        continue
                    command = server.get("command")
                    args = server.get("args")
                    if not isinstance(command, str) or not command.strip() or "<" in command:
                        errors.append(f"{relative}: comando pendiente o inválido: {name}")
                    if not isinstance(args, list) or not all(isinstance(a, str) for a in args):
                        errors.append(f"{relative}: args inválidos: {name}")
        except json.JSONDecodeError:
            errors.append(f"{relative}: JSON inválido")

    if project:
        for relative in ("architecture.md", "PRD.md", "sprint_actual.md"):
            read(relative)
        contracts = root / "packages/contracts/src"
        candidates = [p for p in contracts.glob("**/*.ts") if p.is_file()]
        if not candidates:
            errors.append("packages/contracts/src: faltan contratos TypeScript para consumidores")
        else:
            contents = [read(str(p.relative_to(root))) for p in candidates]
            if not any(c.strip() for c in contents):
                errors.append("packages/contracts/src: no hay contratos con contenido")

    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1],
                        help="Raíz de la plantilla o de su copia en el proyecto receptor")
    parser.add_argument("--project", action="store_true",
                        help="Comprobar entradas técnicas del proyecto receptor; no se requiere en la plantilla")
    args = parser.parse_args()
    errors = validate(args.root.resolve(), args.project)
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if errors:
        print(f"Validación fallida: {len(errors)} problema(s).", file=sys.stderr)
        return 1
    print("Validación local correcta. No acredita conexión MCP ni aprobación de fases.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
