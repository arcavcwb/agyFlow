#!/usr/bin/env python3
"""Diagnose declared workflow evidence; never launch agents or deploy services."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

# Supports both CLI execution and the repository's importlib-based test runner.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from handoff import AGENTS, check_preconditions, load_evidence, specified


GHERKIN_SCENARIOS = [
    ("happy", ["happy path", "camino ideal", "camino feliz", "flujo ideal"]),
    ("error", ["sad path", "error", "validación", "validacion", "fallo"]),
    ("edge", ["edge case", "límite", "limite", "borde", "tiempo", "concurrencia"]),
    ("empty_or_loading", ["vacío", "vacio", "carga", "loading", "empty"]),
]


def check_prd_gherkin(prd_path: Path) -> tuple[bool, list[str]]:
    if not prd_path.exists():
        return False, [f"No se encontró el archivo {prd_path}"]

    content = prd_path.read_text(encoding="utf-8")
    if not content.strip() or "Pendiente de brief" in content:
        return False, ["El PRD está en estado borrador o pendiente de brief."]

    errors = []
    # Find stories like ### [US-...] or ### US-...
    stories = re.split(r"(?=###\s+\[?(?:US|HU|HISTORIA|STORY)-)", content, flags=re.IGNORECASE)
    story_blocks = [s for s in stories if re.match(r"###\s+\[?(?:US|HU|HISTORIA|STORY)-", s.strip(), re.IGNORECASE)]

    if not story_blocks:
        errors.append("No se detectaron historias de usuario identificables (ej. ### [US-01] Título).")
        return False, errors

    for block in story_blocks:
        header = block.strip().splitlines()[0]
        block_lower = block.lower()

        # This is a local structure check, not a complete Gherkin parser.
        clean = re.sub(r"[*`_]", "", block_lower)
        scenarios = re.split(r"(?m)^\s*\d+[.)]\s+", clean)[1:]
        for key, aliases in GHERKIN_SCENARIOS:
            matches = [part for part in scenarios if any(alias in part.splitlines()[0] for alias in aliases)]
            if len(matches) != 1:
                errors.append(f"{header}: falta escenario obligatorio único '{key}'.")
                continue
            body = matches[0]
            if not re.search(r"\b(?:dado|dada|dados|dadas|given)\b.+?\b(?:cuando|when)\b.+?\b(?:entonces|then)\b.+", body, re.S):
                errors.append(f"{header}/{key}: requiere Dado, Cuando y Entonces en orden y con contenido.")
            if re.search(r"\[[^\]]+\]", body):
                errors.append(f"{header}/{key}: reemplazar los campos de ejemplo entre corchetes.")

    return len(errors) == 0, errors


def prd_digest(root):
    return hashlib.sha256((root / "PRD.md").read_bytes()).hexdigest()


def approval_path(root, digest):
    return root / ".agyflow" / "approvals" / f"prd-{digest}.json"


def valid_approval(root):
    digest = prd_digest(root)
    path = approval_path(root, digest)
    if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
        return False
    try:
        data = load_evidence(path.read_text(encoding="utf-8"))
        date = datetime.fromisoformat(data.get("recorded_at", ""))
        return (data.get("document") == "PRD.md" and data.get("sha256") == digest
                and data.get("status") == "approved" and date.tzinfo is not None
                and all(specified(data.get(k)) for k in ("person", "scope", "evidence")))
    except (OSError, UnicodeError, ValueError, TypeError):
        return False


def record_prd_approval(root, person, scope, evidence):
    root = root.resolve()
    if not all(specified(v) for v in (person, scope, evidence)):
        raise ValueError("La aprobación requiere persona, alcance y evidencia explícitos.")
    ok, errors = check_prd_gherkin(root / "PRD.md")
    if not ok:
        raise ValueError("PRD incompleto: " + "; ".join(errors))
    digest = prd_digest(root)
    path = approval_path(root, digest)
    for parent in [path, *path.parents]:
        if parent == root:
            break
        if parent.is_symlink():
            raise ValueError("La ruta de aprobación no admite enlaces simbólicos.")
    path.parent.mkdir(parents=True, exist_ok=True)
    record = dict(schema_version=1, document="PRD.md", sha256=digest, status="approved",
                  person=person, scope=scope, evidence=evidence,
                  recorded_at=datetime.now(timezone.utc).isoformat())
    # Exclusive create: an approval for the same content cannot silently replace history.
    with path.open("x", encoding="utf-8") as handle:
        json.dump(record, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    return path


def detect_phase(root: Path) -> tuple[str, str, str]:
    root = root.resolve()
    try:
        if not (root / "PRD.md").exists():
            return "1_PO", "Falta PRD.md.", "po-agent"
        ok, errors = check_prd_gherkin(root / "PRD.md")
        if not ok:
            return "1_PO_REFINING", "; ".join(errors), "po-agent"
        if not valid_approval(root):
            return "1_PO_GATE", "Falta registro de aprobación para el contenido exacto del PRD.", "HUMANO"
        arch = root / "architecture.md"
        if not arch.is_file() or not arch.read_text(encoding="utf-8").strip():
            return "2_ARCHITECTURE_GATE", "El humano debe aportar architecture.md; el borrador no lo sustituye.", "HUMANO"
        entry = root / "handoff.json"
        if not entry.exists():
            return "2_SCRUM", "Preparar planificación y entrega explícita; no se ha comprobado Plane.", "scrum-master-agent"
        raw = entry.read_text(encoding="utf-8")
        data = load_evidence(raw)
        role = data.get("target_role")
        if not isinstance(role, str) or role not in AGENTS:
            return "BLOCKED", "Destinatario desconocido en handoff.json.", "HUMANO"
        candidate = {}
        if role in {"qa-agent", "devops-agent"} and data.get("phase", "delivery") == "delivery":
            candidate = load_evidence((root / "candidate.json").read_text(encoding="utf-8"))
        ok, errors = check_preconditions(role, raw, revision=candidate.get("revision"),
                                        qa_run=candidate.get("qa_run"), ticket=candidate.get("ticket"))
        if ok and role == "scrum-master-agent" and data["inputs"]["prd_approval"].get("revision") != prd_digest(root):
            errors.append("La entrega de planificación no referencia el hash del PRD aprobado.")
            ok = False
        if not ok:
            return "BLOCKED", "; ".join(errors), role
        if data.get("phase") == "preparation":
            return "3_PREPARATION", "Entradas declaradas consistentes para preparar pruebas/build; sin despliegue.", role
        phases = {"po-agent": "1_PO", "scrum-master-agent": "2_SCRUM", "designer-agent": "3_DESIGN",
                  "backend-dev-agent": "3_BACKEND", "frontend-dev-agent": "4_IMPLEMENTATION",
                  "qa-agent": "4_QA", "devops-agent": "5_STAGING_REVIEW", "automation-agent": "STATE_RECONCILIATION"}
        return phases[role], "Entrega declarada consistente. Verificar fuentes, asignación y activación humana antes de actuar.", role
    except (OSError, UnicodeError, ValueError, TypeError) as exc:
        return "BLOCKED", f"No se pudo verificar la evidencia: {exc}", "HUMANO"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("status", help="Diagnóstico local; no confirma estado remoto")
    subparsers.add_parser("check-prd", help="Comprobar estructura de escenarios; no valida su significado")
    subparsers.add_parser("advance", help="Proponer siguiente acción; no registra aprobaciones ni invoca agentes")
    approve = subparsers.add_parser("approve-prd", help="Registrar una aprobación humana ya otorgada, vinculada al SHA-256 del PRD")
    for name in ("person", "scope", "evidence"):
        approve.add_argument("--" + name, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        if args.command == "approve-prd":
            path = record_prd_approval(root, args.person, args.scope, args.evidence)
            print(f"Registro de aprobación escrito en {path}. No activa la siguiente fase.")
            return 0
        if args.command == "check-prd":
            ok, errors = check_prd_gherkin(root / "PRD.md")
            print("Estructura de escenarios válida; requiere revisión de contenido." if ok else "\n".join(errors))
            return 0 if ok else 1
        phase, detail, actor = detect_phase(root)
        print(f"Fase: {phase}\nDetalle: {detail}\nSiguiente actor propuesto: {actor}")
        if args.command == "advance":
            print("No se registró ninguna aprobación ni se ejecutó una fase.")
            if phase.endswith("GATE"):
                print("Aportar la evidencia humana requerida. Para PRD: approve-prd --person ... --scope ... --evidence ...")
        return 1 if phase == "BLOCKED" else 0
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
