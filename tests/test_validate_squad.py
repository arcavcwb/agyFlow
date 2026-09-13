"""Exercise packaging failures using disposable copies, without external tools."""

import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


SOURCE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("validate_squad", SOURCE / "scripts/validate_squad.py")
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class PackageValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="agyflow-validation-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "project"
        self.root.mkdir()
        for name in ("AGENTS.md", "README.md"):
            shutil.copy2(SOURCE / name, self.root / name)
        for name in (".agents", ".github", "config", "docs", "templates", "tools"):
            shutil.copytree(SOURCE / name, self.root / name)
        self.registry_path = self.root / "config/skills.json"
        self.registry = json.loads(self.registry_path.read_text())

    def save(self, registry):
        self.registry_path.write_text(json.dumps(registry))

    def check(self, project=False):
        return validator.validate(self.root, project)

    def test_template_is_complete_without_product(self):
        self.assertFalse((self.root / "architecture.md").exists())
        self.assertEqual(self.check(), [])

    def test_missing_skill_is_rejected(self):
        path = self.registry["bundled"]["agy-requirements"]["path"]
        (self.root / path).unlink()
        self.assertTrue(self.check())

    def test_skill_name_mismatch_is_rejected(self):
        path = self.root / self.registry["bundled"]["agy-requirements"]["path"]
        path.write_text(path.read_text().replace("name: agy-requirements", "name: wrong-name"))
        self.assertTrue(self.check())

    def test_agent_must_reference_assigned_skill(self):
        path = self.root / ".agents/agents/po-agent/agent.md"
        path.write_text(path.read_text().replace(".agents/skills/agy-requirements/SKILL.md", "unassigned.md"))
        self.assertTrue(self.check())

    def test_agent_missing_stack_reference_is_rejected(self):
        path = self.root / ".agents/agents/po-agent/agent.md"
        path.write_text(path.read_text().replace("docs/stack.md", "docs/unassigned.md"))
        self.assertTrue(self.check())

    def test_agent_missing_entrega_reference_is_rejected(self):
        path = self.root / ".agents/agents/frontend-dev-agent/agent.md"
        path.write_text(path.read_text().replace("templates/entrega.md", "templates/unassigned.md"))
        self.assertTrue(self.check())

    def test_context_strategy_is_required_and_referenced(self):
        (self.root / "docs/context-strategy.md").unlink()
        self.assertTrue(any("context-strategy.md" in e for e in self.check()))

    def test_readme_and_index_must_reference_context_strategy(self):
        for name in ("README.md", "AGENTS.md"):
            with self.subTest(name=name):
                path = self.root / name
                original = path.read_text()
                path.write_text(original.replace(
                    "docs/context-strategy.md", "docs/missing-context.md"
                ))
                self.assertTrue(any(
                    name in e and "estrategia de contexto" in e
                    for e in self.check()
                ))
                path.write_text(original)

    def test_every_agent_applies_context_strategy(self):
        path = self.root / ".agents/agents/qa-agent/agent.md"
        path.write_text(path.read_text().replace(
            "docs/context-strategy.md", "docs/other.md"
        ))
        self.assertTrue(any(
            "qa-agent/agent.md" in e and "estrategia de contexto" in e
            for e in self.check()
        ))

    def test_diagrams_are_declared_non_operational(self):
        path = self.root / "docs/diagrams/README.md"
        path.write_text(path.read_text().replace(
            "material humano", "material requerido"
        ))
        self.assertTrue(any("material humano" in e for e in self.check()))

    def test_agents_cannot_require_binary_diagrams(self):
        path = self.root / ".agents/agents/designer-agent/agent.md"
        path.write_text(
            path.read_text()
            + "\nLeé docs/diagrams/agyflow-super-mvp.excalidraw siempre.\n"
        )
        self.assertTrue(any(
            "diagrama binario" in e for e in self.check()
        ))

    def test_unknown_or_duplicate_optional_is_rejected(self):
        for optional in (["unknown"], ["webapp-testing", "webapp-testing"], [None]):
            with self.subTest(optional=optional):
                registry = copy.deepcopy(self.registry)
                registry["agents"]["qa-agent"]["optional"] = optional
                self.save(registry)
                self.assertTrue(self.check())

    def test_registry_types_produce_errors_without_crashing(self):
        cases = [[], None, {"schema_version": 1, "agents": [], "bundled": {}, "external": {}}]
        for section in ("agents", "bundled", "external"):
            registry = copy.deepcopy(self.registry)
            key = next(iter(registry[section]))
            registry[section][key] = None
            cases.append(registry)
        for registry in cases:
            with self.subTest(registry=registry):
                self.save(registry)
                self.assertTrue(self.check())

    def test_core_assignment_is_unique_and_known(self):
        for core in ("unknown", "agy-planning", []):
            with self.subTest(core=core):
                registry = copy.deepcopy(self.registry)
                registry["agents"]["po-agent"]["core"] = core
                self.save(registry)
                self.assertTrue(self.check())

    def test_nonportable_paths_are_rejected(self):
        for path in ("../outside/SKILL.md", "/tmp/SKILL.md", "C:\\skills\\SKILL.md"):
            with self.subTest(path=path):
                registry = copy.deepcopy(self.registry)
                registry["bundled"]["agy-requirements"]["path"] = path
                self.save(registry)
                self.assertTrue(self.check())

    def test_symlink_outside_distribution_is_rejected(self):
        path = self.root / self.registry["bundled"]["agy-requirements"]["path"]
        outside = Path(self.temp.name) / "outside.md"
        outside.write_text(path.read_text())
        path.unlink()
        path.symlink_to(outside)
        self.assertTrue(self.check())

    def test_pinned_source_requires_exact_revision(self):
        registry = copy.deepcopy(self.registry)
        entry = registry["external"]["impeccable"]
        entry.update(status="pinned", revision="main")
        self.save(registry)
        self.assertTrue(self.check())
        entry["revision"] = "a" * 40
        self.save(registry)
        self.assertEqual(self.check(), [])

    def test_invalid_external_source_is_rejected(self):
        for source in (None, "file:///etc/passwd", "https://", "https://["):
            with self.subTest(source=source):
                registry = copy.deepcopy(self.registry)
                registry["external"]["impeccable"]["source"] = source
                self.save(registry)
                self.assertTrue(self.check())

    def test_project_mode_requires_actual_inputs(self):
        self.assertTrue(self.check(project=True))
        for name in ("architecture.md", "PRD.md", "sprint_actual.md"):
            (self.root / name).write_text("Fixture de entrada: sin aprobación de producto.\n")
        contracts = self.root / "packages/contracts/src"
        contracts.mkdir(parents=True)
        fixture = contracts / "fixture.ts"
        fixture.write_text(" ")
        self.assertTrue(self.check(project=True))
        fixture.write_text("export type Fixture = { value: string };\n")
        self.assertEqual(self.check(project=True), [])

    def test_malformed_json_fails_cli_without_traceback(self):
        self.registry_path.write_text("{broken")
        result = subprocess.run(
            [sys.executable, str(SOURCE / "scripts/validate_squad.py"), "--root", str(self.root)],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 1)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
