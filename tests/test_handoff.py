"""Unit tests for scripts/handoff.py helper."""

import importlib.util
from pathlib import Path
import unittest

SOURCE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("handoff", SOURCE / "scripts/handoff.py")
handoff = importlib.util.module_from_spec(spec)
spec.loader.exec_module(handoff)


class HandoffTests(unittest.TestCase):
    def test_build_prompt_valid_role(self):
        prompt = handoff.build_prompt(
            target_role="frontend-dev-agent",
            ticket="PROJ-101 (https://plane.so/tickets/101)",
            routes="apps/web/src/features/auth",
            from_role="backend-dev-agent",
            session="agy-1",
            context="Contratos listos en packages/contracts@rev-12a",
        )
        self.assertIn("frontend-dev-agent", prompt)
        self.assertIn("PROJ-101", prompt)
        self.assertIn("apps/web/src/features/auth", prompt)
        self.assertIn("backend-dev-agent", prompt)
        self.assertIn("templates/entrega.md", prompt)

    def test_build_prompt_unknown_role_raises(self):
        with self.assertRaises(ValueError):
            handoff.build_prompt(
                target_role="non-existent-agent",
                ticket="PROJ-1",
                routes="src/",
            )

    def test_check_preconditions_success(self):
        content = "Entrega de contratos listos: packages/contracts/src/auth.schema.ts"
        ok, errors = handoff.check_preconditions("frontend-dev-agent", content)
        self.assertTrue(ok)
        self.assertEqual(errors, [])

    def test_check_preconditions_missing(self):
        content = "Documento inicial sin dependencias resueltas ni esquemas preparados"
        ok, errors = handoff.check_preconditions("frontend-dev-agent", content)
        self.assertFalse(ok)
        self.assertTrue(len(errors) > 0)

    def test_check_preconditions_devops_requires_qa_aprobado(self):
        content_rejected = "bug_report.md con resultado: rechazado"
        ok, _ = handoff.check_preconditions("devops-agent", content_rejected)
        self.assertFalse(ok)

        content_approved = "bug_report.md con QA aprobado para revision rev-abc"
        ok, errors = handoff.check_preconditions("devops-agent", content_approved)
        self.assertTrue(ok)
        self.assertEqual(errors, [])

    def test_get_template_prefilled(self):
        tmpl = handoff.get_template(role="backend-dev-agent", session="agy-2")
        self.assertIn("backend-dev-agent (agy-2)", tmpl)
        self.assertIn("Entrega de tarea", tmpl)


if __name__ == "__main__":
    unittest.main()
