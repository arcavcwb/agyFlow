"""Regression tests for non-destructive receiver adoption."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('setup_receiver', SOURCE / 'scripts/setup_receiver.py')
setup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(setup)


class SetupReceiverTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='test-receiver-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'receiver'

    def install(self, **kwargs):
        return setup.scaffold_receiver(self.root, frontend='next', backend='node', db='none', **kwargs)

    def test_initial_install_is_a_draft_not_a_product(self):
        self.install()
        self.assertTrue((self.root / 'architecture.proposed.md').exists())
        self.assertFalse((self.root / 'architecture.md').exists())
        self.assertFalse((self.root / 'packages/contracts/src/index.ts').exists())
        self.assertIn('Estado: borrador', (self.root / 'PRD.md').read_text())
        self.assertTrue(list((self.root / 'tests').glob('test_*.py')))
        self.assertTrue((self.root / '.github/workflows/validate-squad.yml').exists())
        self.assertTrue((self.root / '.gitignore').exists())

    def test_force_preserves_foreign_files_architecture_and_product_documents(self):
        self.install()
        foreign = {'docs/decisiones.md': 'Humano', 'architecture.md': 'Arquitectura humana',
                   'PRD.md': 'PRD real', 'sprint_actual.md': 'Estado real',
                   'packages/contracts/src/index.ts': 'export type Actual = string;'}
        for name, content in foreign.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        self.install(force=True)
        for name, content in foreign.items():
            self.assertEqual((self.root / name).read_text(), content)

    def test_merge_existing_directories_and_backup_conflicts(self):
        (self.root / 'docs').mkdir(parents=True)
        existing = self.root / 'docs/protocolo.md'
        existing.write_text('Custom protocol')
        self.install()
        self.assertEqual(existing.read_text(), 'Custom protocol')
        self.assertTrue((self.root / 'docs/stack.md').exists())
        self.install(force=True)
        backups = list((self.root / '.agyflow-backups').glob('setup-*/docs/protocolo.md'))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), 'Custom protocol')

    def test_dry_run_is_non_mutating_and_rerun_is_idempotent(self):
        self.assertTrue(self.install(dry_run=True))
        self.assertFalse(self.root.exists())
        self.install()
        self.assertEqual(self.install(), [])

    def test_symlink_and_nested_target_rejected_before_writes(self):
        self.root.mkdir()
        external = Path(self.temp.name) / 'outside'
        external.mkdir()
        (self.root / 'docs').symlink_to(external, target_is_directory=True)
        with self.assertRaises(ValueError):
            self.install(force=True)
        self.assertEqual(list(external.iterdir()), [])
        self.assertFalse((self.root / 'AGENTS.md').exists())
        for target in (SOURCE, SOURCE / 'nested-receiver'):
            with self.assertRaises(ValueError):
                setup.scaffold_receiver(target)

    def test_does_not_distribute_live_mcp_config(self):
        self.assertNotIn(Path('.agents/mcp_config.json'), setup.distribution_files())
        self.assertNotIn(Path('.env'), setup.distribution_files())
        self.install()
        self.assertFalse((self.root / '.agents/mcp_config.json').exists())

    def test_existing_ignores_are_preserved(self):
        self.root.mkdir()
        (self.root / '.gitignore').write_text('my-cache/\n')
        self.install()
        content = (self.root / '.gitignore').read_text()
        self.assertIn('my-cache/', content)
        self.assertIn('.agents/mcp_config.json', content)


if __name__ == '__main__':
    unittest.main()
