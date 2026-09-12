#!/usr/bin/env python3
"""Interactive pipeline runner and Gherkin validator for agyFlow squad."""

import argparse
from pathlib import Path
import re
import sys

AGENTS_BY_PHASE = {
    "PO": "po-agent",
    "SCRUM": "scrum-master-agent",
    "CONTRACTS": "backend-dev-agent",
    "DESIGN": "designer-agent",
    "FRONTEND": "frontend-dev-agent",
    "QA": "qa-agent",
    "DEVOPS": "devops-agent",
}

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

        # Check Given / When / Then
        has_given = any(k in block_lower for k in ["dado", "dada", "dados", "dadas", "given"])
        has_when = any(k in block_lower for k in ["cuando", "when"])
        has_then = any(k in block_lower for k in ["entonces", "then"])

        if not (has_given and has_when and has_then):
            errors.append(f"{header}: faltan cláusulas Given/When/Then (Dado/Cuando/Entonces).")

        # Check 4 mandatory scenarios
        for key, aliases in GHERKIN_SCENARIOS:
            if not any(alias in block_lower for alias in aliases):
                errors.append(f"{header}: falta escenario obligatorio '{key}' ({', '.join(aliases[:2])}).")

    return len(errors) == 0, errors


def detect_phase(root: Path) -> tuple[str, str, str]:
    """Detect current phase, details, and next recommended agent."""
    prd_path = root / "PRD.md"
    sprint_path = root / "sprint_actual.md"
    contracts_path = root / "packages/contracts/src"
    bug_path = root / "bug_report.md"

    # 1. PRD Phase
    if not prd_path.exists():
        return "1_PO", "Falta PRD.md.", "po-agent"

    prd_content = prd_path.read_text(encoding="utf-8")
    if "Aprobación humana (persona, fecha, alcance y evidencia): pendiente" in prd_content:
        ok_gh, gherkin_errs = check_prd_gherkin(prd_path)
        if not ok_gh:
            return "1_PO_REFINING", f"El PRD requiere completar los 4 escenarios Gherkin ({len(gherkin_errs)} pendientes).", "po-agent"
        return "1_PO_GATE", "PRD completo con 4 Gherkins listos. Requiere aprobación humana.", "HUMANO (Firma de aprobación)"

    # 2. Planning Phase
    if not sprint_path.exists():
        return "2_SCRUM", "PRD aprobado pero falta sprint_actual.md.", "scrum-master-agent"

    sprint_content = sprint_path.read_text(encoding="utf-8")
    if "Estado: sin inicializar" in sprint_content:
        return "2_SCRUM", "Sprint no inicializado en Plane.", "scrum-master-agent"

    # 3. Parallel Contracts & Design
    has_contracts = contracts_path.exists() and any(contracts_path.glob("**/*.ts"))
    if not has_contracts:
        return "3_CONTRACTS", "Faltan contratos compartidos en packages/contracts/src.", "backend-dev-agent"

    # 4. QA or Bugs
    if bug_path.exists():
        bug_content = bug_path.read_text(encoding="utf-8")
        if "Resultado: aprobado" in bug_content:
            return "5_DEVOPS_STAGING", "QA aprobado para la revisión candidata. Listo para Staging.", "devops-agent"
        elif "Resultado: rechazado" in bug_content:
            return "4_CORRECTION", "QA rechazado. Se requiere corregir el código según bug_report.md.", "frontend-dev-agent / backend-dev-agent"

    return "4_IMPLEMENTATION_QA", "Fase de implementación o auditoría QA.", "qa-agent"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Raíz del proyecto")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("status", help="Mostrar fase actual y diagnósticos")
    subparsers.add_parser("check-prd", help="Validar la regla de los 4 escenarios Gherkin en PRD.md")
    subparsers.add_parser("advance", help="Avanzar interactivamente a la siguiente fase")

    args = parser.parse_args()
    if not args.command:
        args.command = "status"
    root = args.root.resolve()

    if args.command == "status":
        phase, detail, next_actor = detect_phase(root)
        print("=== ESTADO DEL PIPELINE agyFlow ===")
        print(f"Directorio: {root}")
        print(f"Fase detectada: {phase}")
        print(f"Detalle: {detail}")
        print(f"Siguiente actor: {next_actor}")

        prd_file = root / "PRD.md"
        if prd_file.exists():
            ok_gh, gh_errs = check_prd_gherkin(prd_file)
            print("\n=== AUDITORÍA GHERKIN EN PRD.md ===")
            if ok_gh:
                print("✅ Todas las historias cumplen la Regla de los 4 Escenarios Gherkin.")
            else:
                print(f"⚠️ Se encontraron {len(gh_errs)} observaciones:")
                for err in gh_errs[:5]:
                    print(f"   - {err}")
                if len(gh_errs) > 5:
                    print(f"   ... y {len(gh_errs) - 5} más.")

    elif args.command == "check-prd":
        prd_file = root / "PRD.md"
        ok_gh, gh_errs = check_prd_gherkin(prd_file)
        if ok_gh:
            print("OK: PRD.md cumple 100% con la Regla de los 4 Escenarios Gherkin obligatorios.")
            return 0
        else:
            print(f"FALLO: El PRD no cumple con la regla de Gherkin ({len(gh_errs)} problemas):", file=sys.stderr)
            for e in gh_errs:
                print(f"  - {e}", file=sys.stderr)
            return 1

    elif args.command == "advance":
        phase, detail, next_actor = detect_phase(root)
        print(f"\n[Fase Actual]: {phase}")
        print(f"[Diagnóstico]: {detail}")
        print(f"[Siguiente Acción]: Invocar a [{next_actor}]")

        if "GATE" in phase or "HUMANO" in next_actor:
            confirm = input("\n¿Aprobás esta fase para avanzar? [S/N]: ").strip().lower()
            if confirm in ["s", "si", "y", "yes"]:
                print("✅ Aprobación humana registrada. Procede a ejecutar la siguiente fase.")
            else:
                print("⏸️ Detenido. La fase permanece pendiente de aprobación humana.")
        else:
            print(f"\nComando sugerido: agy --agent {next_actor}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
