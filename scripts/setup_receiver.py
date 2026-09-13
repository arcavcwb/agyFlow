#!/usr/bin/env python3
"""Copy a portable squad safely and prepare proposals for human review."""
import argparse
from pathlib import Path
import shutil
import sys
import tempfile

TEMPLATE_ROOT = Path(__file__).resolve().parents[1]
CHOICES = {
    'frontend': ('next', 'astro', 'hybrid'),
    'backend': ('nestjs', 'node'),
    'db': ('supabase', 'postgres', 'none'),
    'state_manager': ('scrum-manual', 'automation'),
}


def generate_architecture_md(frontend=None, backend=None, db=None):
    return f'''# Propuesta de arquitectura — pendiente de revisión humana

Este borrador no es architecture.md, no constituye aprobación ni define contratos.
El humano decide las versiones, rutas, despliegue, pruebas y permisos del proyecto.

## Preferencias solicitadas

- Frontend: {frontend or 'por definir'}
- Backend: {backend or 'por definir'}
- Persistencia: {db or 'por definir'}

## Decisiones pendientes

- Superficies, frameworks, versiones y rutas reales.
- Contratos necesarios, consumidores y reglas de negocio.
- Diseño de referencia, estados y criterios de accesibilidad.
- Autenticación, autorización y tratamiento de datos según riesgos.
- Pruebas, build, entorno, despliegue y recuperación.

La persona responsable debe aportar architecture.md con las decisiones revisadas.
'''


def distribution_files():
    """Explicit distribution boundaries: never copy a receiver's credentials or reports."""
    result = []
    for name in ('AGENTS.md', 'README.md', '.pre-commit-config.yaml',
                 '.agents/mcp_config.example.json', '.github/workflows/validate-squad.yml'):
        result.append(Path(name))
    for pattern in ('.agents/agents/*/agent.md', '.agents/skills/*/SKILL.md',
                    'config/skills.json', 'templates/*.md', 'templates/*.json',
                    'scripts/*.py', 'tests/test_*.py'):
        result.extend(p.relative_to(TEMPLATE_ROOT) for p in TEMPLATE_ROOT.glob(pattern))
    for name in ('protocolo.md', 'agy-codex.md', 'stack.md', 'skills.md', 'herramientas-locales.md'):
        if (TEMPLATE_ROOT / 'docs' / name).is_file():
            result.append(Path('docs') / name)
    if (TEMPLATE_ROOT / 'docs/demo-flujo.html').is_file():
        result.append(Path('docs/demo-flujo.html'))
    if (TEMPLATE_ROOT / 'docs/diagrams').is_dir():
        result.extend(p.relative_to(TEMPLATE_ROOT) for p in (TEMPLATE_ROOT / 'docs/diagrams').iterdir()
                      if p.suffix in {'.md', '.excalidraw', '.svg', '.png'})
    return sorted(set(result))


def safe_destination(root, relative):
    path = root / relative
    for part in [path, *path.parents]:
        if part == root:
            break
        if part.is_symlink():
            raise ValueError(f'Destino con enlace simbólico: {relative}')
    if path.exists() and not path.is_file():
        raise ValueError(f'Se esperaba un archivo: {relative}')
    for part in path.parents:
        if part == root:
            break
        if part.exists() and not part.is_dir():
            raise ValueError(f'Un archivo impide crear el directorio: {part}')
    return path


def scaffold_receiver(target_dir: Path, frontend=None, backend=None, db=None,
                      state_manager=None, force=False, copy_squad=True, dry_run=False) -> list[Path]:
    for name, value in [('frontend', frontend), ('backend', backend), ('db', db), ('state_manager', state_manager)]:
        if value is not None and value not in CHOICES[name]:
            raise ValueError(f'{name} inválido: {value}')
    root = target_dir.resolve()
    source = TEMPLATE_ROOT.resolve()
    if root == source or root.is_relative_to(source) or source.is_relative_to(root):
        raise ValueError('El destino debe estar separado del árbol de la plantilla.')
    if root.exists() and not root.is_dir():
        raise ValueError('El destino debe ser un directorio.')

    files = {}
    if copy_squad:
        for relative in distribution_files():
            src = source / relative
            if src.is_symlink() or not src.resolve().is_relative_to(source):
                raise ValueError(f'Origen no portable: {relative}')
            files[relative] = src.read_bytes()
    # Generated drafts never replace existing documents, even with --force.
    drafts = {
        Path('architecture.proposed.md'): generate_architecture_md(frontend, backend, db).encode(),
        Path('project_setup.proposed.md'): (
            '# Preferencias de adopción — no verificadas\n\n'
            f'Responsable operativo solicitado: {state_manager or "por asignar"}.\n'
            'La asignación y las herramientas requieren evidencia humana y comprobación.\n'
        ).encode(),
        Path('PRD.md'): (source / 'templates/PRD.md').read_bytes(),
        Path('sprint_actual.md'): (source / 'templates/sprint_actual.md').read_bytes(),
    }
    files.update(drafts)
    # Merge ignores, retaining receiver rules. No live MCP config is distributed.
    ignore = safe_destination(root, Path('.gitignore'))
    old_ignore = ignore.read_text(encoding='utf-8') if ignore.exists() else ''
    rules = ['.agents/mcp_config.json', '.env', '.env.*', '!.env.example', '__pycache__/', '.agyflow-backups/']
    missing = [rule for rule in rules if rule not in old_ignore.splitlines()]
    if missing:
        files[Path('.gitignore')] = (old_ignore.rstrip('\n') + ('\n' if old_ignore else '') + '\n'.join(missing) + '\n').encode()
    changes = []
    for relative, content in sorted(files.items()):
        dest = safe_destination(root, relative)
        if dest.exists():
            if dest.read_bytes() == content:
                continue
            if relative != Path('.gitignore') and (relative in drafts or not force):
                continue
        changes.append((dest, content))
    if dry_run:
        return [p for p, _ in changes]
    backup_root = root / '.agyflow-backups'
    if any(dest.exists() for dest, _ in changes):
        if backup_root.is_symlink() or (backup_root.exists() and not backup_root.is_dir()):
            raise ValueError('El destino de respaldos debe ser un directorio sin enlaces.')
    root.mkdir(parents=True, exist_ok=True)
    backup = None
    for dest, content in changes:
        if dest.exists():
            if backup is None:
                backup_root.mkdir(exist_ok=True)
                backup = Path(tempfile.mkdtemp(prefix='setup-', dir=backup_root))
            saved = backup / dest.relative_to(root)
            saved.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(dest, saved)
        dest.parent.mkdir(parents=True, exist_ok=True)
        # Atomic replacement avoids truncated individual files on interrupted writes.
        with tempfile.NamedTemporaryFile(dir=dest.parent, delete=False) as handle:
            staged = Path(handle.name)
            handle.write(content)
        try:
            staged.replace(dest)
        finally:
            staged.unlink(missing_ok=True)
    return [p for p, _ in changes]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', type=Path, required=True)
    for name, choices in CHOICES.items():
        parser.add_argument('--' + name.replace('_', '-'), choices=choices)
    parser.add_argument('--force', action='store_true', help='Actualizar archivos distribuidos, con respaldo; conserva borradores y archivos ajenos')
    parser.add_argument('--dry-run', action='store_true', help='Mostrar archivos a cambiar sin escribir')
    parser.add_argument('--no-squad-copy', dest='copy_squad', action='store_false')
    args = parser.parse_args()
    try:
        paths = scaffold_receiver(args.target, args.frontend, args.backend, args.db,
                                  args.state_manager, args.force, args.copy_squad, args.dry_run)
    except (OSError, ValueError, UnicodeError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 1
    print('Vista previa (sin escrituras):' if args.dry_run else 'Archivos creados/actualizados:')
    for path in paths:
        print(path)
    print(f'{len(paths)} archivos. Documentos existentes conservados salvo actualización explícita del paquete; revisar conflictos manualmente.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
