#!/usr/bin/env python3
"""Scaffold and initialize an agyFlow receiver project with verified inputs and architecture."""

import argparse
from pathlib import Path
import shutil
import sys

TEMPLATE_ROOT = Path(__file__).resolve().parents[1]


def generate_architecture_md(frontend: str, backend: str, db: str) -> str:
    fe_desc = {
        "next": "Next.js (apps/web) para la aplicación interactiva.",
        "astro": "Astro (apps/site) para páginas y sitios estáticos / SSG.",
        "hybrid": "Next.js (apps/web) para app cliente y Astro (apps/site) para portal/marketing.",
    }.get(frontend, "Next.js / Astro según superficie.")

    be_desc = {
        "nestjs": "NestJS para servicios modulares estructurados.",
        "node": "Node.js / Express o Fastify para servicios y APIs.",
    }.get(backend, "Servicios Node.js / NestJS.")

    db_desc = {
        "supabase": "Supabase (PostgreSQL + RLS explícito y autenticación).",
        "postgres": "PostgreSQL directo con migraciones SQL.",
        "none": "Sin base de datos dedicada inicial / persistencia delegada.",
    }.get(db, "Persistencia según definición del proyecto.")

    return f"""# Architecture & Technical Decisions

> Gobernanza humana: este archivo define el stack y las rutas oficiales del proyecto receptor.
> Ningún agente modifica este archivo sin autorización humana explícita.

## Stack seleccionado

- **Frontend**: {fe_desc}
- **Backend**: {be_desc}
- **Persistencia**: {db_desc}
- **Contratos compartidos**: `packages/contracts` con esquemas Zod y tipos TypeScript inferidos.
- **Testing y QA**: Playwright para E2E / pruebas de navegador; suites de integración y unitarias locales.

## Rutas del proyecto

- `apps/`: aplicaciones cliente e interfaz.
- `packages/contracts/src/`: esquemas y tipos compartidos (escritura Backend, lectura Frontend).
- `tests/`: pruebas automatizadas y reportes de QA (`bug_report.md`).
- `docs/`: documentación de arquitectura, despliegues y guías operativas.

## Convenciones de contrato

1. Todo contrato de datos entre Frontend y Backend se define primero en `packages/contracts/src/` con Zod.
2. Ninguna ruta de frontend asume contratos no publicados o no verificados.
3. Las tablas de base de datos no se publican sin políticas de seguridad explícitas (RLS).
"""


def scaffold_receiver(target_dir: Path, frontend: str, backend: str, db: str,
                       state_manager: str, force: bool = False, copy_squad: bool = True) -> list[Path]:
    created = []
    target_dir.mkdir(parents=True, exist_ok=True)

    # 1. Copy squad template files if requested and target is not TEMPLATE_ROOT
    if copy_squad and target_dir.resolve() != TEMPLATE_ROOT.resolve():
        for item in ["AGENTS.md", "README.md"]:
            dest = target_dir / item
            if not dest.exists() or force:
                shutil.copy2(TEMPLATE_ROOT / item, dest)
                created.append(dest)
        for folder in [".agents", "config", "docs", "templates", "scripts"]:
            dest = target_dir / folder
            if not dest.exists() or force:
                if dest.exists() and force:
                    shutil.rmtree(dest)
                shutil.copytree(TEMPLATE_ROOT / folder, dest)
                created.append(dest)

    # 2. architecture.md
    arch_file = target_dir / "architecture.md"
    if not arch_file.exists() or force:
        arch_file.write_text(generate_architecture_md(frontend, backend, db), encoding="utf-8")
        created.append(arch_file)

    # 3. PRD.md (from template)
    prd_file = target_dir / "PRD.md"
    if not prd_file.exists() or force:
        template_prd = (TEMPLATE_ROOT / "templates/PRD.md").read_text(encoding="utf-8")
        prd_file.write_text(template_prd, encoding="utf-8")
        created.append(prd_file)

    # 4. sprint_actual.md (from template with state manager prefilled)
    sprint_file = target_dir / "sprint_actual.md"
    if not sprint_file.exists() or force:
        template_sprint = (TEMPLATE_ROOT / "templates/sprint_actual.md").read_text(encoding="utf-8")
        mgr_text = "Scrum manual" if state_manager == "scrum-manual" else "Automation"
        template_sprint = template_sprint.replace(
            "Responsable de estado operativo y espejo: por asignar (Scrum manual o Automation)",
            f"Responsable de estado operativo y espejo: {mgr_text}"
        )
        sprint_file.write_text(template_sprint, encoding="utf-8")
        created.append(sprint_file)

    # 5. packages/contracts/src/index.ts
    contracts_dir = target_dir / "packages/contracts/src"
    contracts_dir.mkdir(parents=True, exist_ok=True)
    contracts_entry = contracts_dir / "index.ts"
    if not contracts_entry.exists() or force:
        contracts_entry.write_text("// Shared contracts and Zod schemas for agyFlow squad\nexport type BaseEntity = { id: string; createdAt: string };\n", encoding="utf-8")
        created.append(contracts_entry)

    # 6. tests/ directory
    tests_dir = target_dir / "tests"
    tests_dir.mkdir(parents=True, exist_ok=True)

    return created


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", type=Path, default=Path.cwd(), help="Directorio destino del proyecto receptor")
    parser.add_argument("--frontend", choices=["next", "astro", "hybrid"], default="hybrid", help="Superficie frontend principal")
    parser.add_argument("--backend", choices=["nestjs", "node"], default="nestjs", help="Framework de backend")
    parser.add_argument("--db", choices=["supabase", "postgres", "none"], default="supabase", help="Sistema de base de datos")
    parser.add_argument("--state-manager", choices=["scrum-manual", "automation"], default="scrum-manual", help="Responsable del estado operativo del sprint")
    parser.add_argument("--force", action="store_true", help="Sobreescribir archivos si ya existen")
    parser.add_argument("--no-squad-copy", dest="copy_squad", action="store_false", help="No copiar los archivos del squad de agyFlow")

    args = parser.parse_args()

    created = scaffold_receiver(
        target_dir=args.target,
        frontend=args.frontend,
        backend=args.backend,
        db=args.db,
        state_manager=args.state_manager,
        force=args.force,
        copy_squad=args.copy_squad,
    )

    print(f"Scaffolding completado en {args.target.resolve()}. Archivos generados/actualizados: {len(created)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
