"""Unit tests for scripts/setup_receiver.py."""

import importlib.util
from pathlib import Path
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1]
spec_setup = importlib.util.spec_from_file_location("setup_receiver", SOURCE / "scripts/setup_receiver.py")
setup_receiver = importlib.util.module_from_spec(spec_setup)
spec_setup.loader.exec_module(setup_receiver)

spec_val = importlib.util.spec_from_file_location("validate_squad", SOURCE / "scripts/validate_squad.py")
validate_squad = importlib.util.module_from_spec(spec_val)
spec_val.loader.exec_module(validate_squad)


class SetupReceiverTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(prefix="test-receiver-")
        self.addCleanup(self.temp_dir.cleanup)
        self.target = Path(self.temp_dir.name)

    def test_scaffold_creates_required_files(self):
        created = setup_receiver.scaffold_receiver(
            target_dir=self.target,
            frontend="next",
            backend="nestjs",
            db="supabase",
            state_manager="scrum-manual",
        )
        self.assertTrue((self.target / "architecture.md").exists())
        self.assertTrue((self.target / "PRD.md").exists())
        self.assertTrue((self.target / "sprint_actual.md").exists())
        self.assertTrue((self.target / "packages/contracts/src/index.ts").exists())

        arch_content = (self.target / "architecture.md").read_text()
        self.assertIn("Next.js", arch_content)
        self.assertIn("NestJS", arch_content)
        self.assertIn("Supabase", arch_content)

    def test_scaffolded_project_passes_project_validation(self):
        setup_receiver.scaffold_receiver(
            target_dir=self.target,
            frontend="hybrid",
            backend="nestjs",
            db="postgres",
            state_manager="automation",
        )
        # Run project mode validator on the scaffolded project
        errors = validate_squad.validate(self.target, project=True)
        self.assertEqual(errors, [])

    def test_force_protection(self):
        (self.target / "architecture.md").parent.mkdir(parents=True, exist_ok=True)
        (self.target / "architecture.md").write_text("Custom human architecture")

        # Without force, should not overwrite
        setup_receiver.scaffold_receiver(
            target_dir=self.target,
            frontend="astro",
            backend="node",
            db="none",
            state_manager="scrum-manual",
            force=False,
        )
        self.assertEqual((self.target / "architecture.md").read_text(), "Custom human architecture")

        # With force, should overwrite
        setup_receiver.scaffold_receiver(
            target_dir=self.target,
            frontend="astro",
            backend="node",
            db="none",
            state_manager="scrum-manual",
            force=True,
        )
        self.assertIn("Astro", (self.target / "architecture.md").read_text())


if __name__ == "__main__":
    unittest.main()
