"""Unit tests for scripts/handoff.py helper."""

import importlib.util
from pathlib import Path
import unittest
import json
import sys

SOURCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE / "scripts"))
from demo_workflow import evidence
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
        content = json.dumps(evidence("frontend-dev-agent"))
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

        content_approved = json.dumps(evidence("devops-agent"))
        ok, errors = handoff.check_preconditions("devops-agent", content_approved, revision="demo-rev-1", qa_run="demo-qa-1", ticket="SIM-US-01")
        self.assertTrue(ok)
        self.assertEqual(errors, [])

    def test_get_template_prefilled(self):
        tmpl = handoff.get_template(role="backend-dev-agent", session="agy-2")
        self.assertIn("backend-dev-agent (agy-2)", tmpl)
        self.assertIn("Entrega de tarea", tmpl)


    def test_negations_and_plain_text_never_authorize(self):
        for role, text in [("devops-agent", "QA no aprobado. No desplegar."),
                           ("frontend-dev-agent", "Los contratos no están listos.")]:
            self.assertFalse(handoff.check_preconditions(role, text)[0])

    def test_stale_candidate_and_pending_checks_fail(self):
        data = evidence("devops-agent")
        params = dict(revision="demo-rev-2", qa_run="demo-qa-2", ticket="SIM-US-01")
        self.assertFalse(handoff.check_preconditions("devops-agent", json.dumps(data), **params)[0])
        params.update(revision="demo-rev-1", qa_run="demo-qa-1")
        data["inputs"]["qa"]["pending_checks"] = ["test de permisos"]
        self.assertFalse(handoff.check_preconditions("devops-agent", json.dumps(data), **params)[0])

    def test_not_applicable_requires_reason(self):
        data = evidence("frontend-dev-agent")
        data["inputs"]["contracts"] = {"status": "not_applicable"}
        self.assertFalse(handoff.check_preconditions("frontend-dev-agent", json.dumps(data))[0])
        data["inputs"]["contracts"]["reason"] = "Página informativa sin API"
        self.assertTrue(handoff.check_preconditions("frontend-dev-agent", json.dumps(data))[0])

    def test_preparation_does_not_require_approved_qa(self):
        data = evidence("devops-agent")
        data["phase"] = "preparation"
        data["inputs"].pop("qa")
        data["inputs"].pop("artifact")
        self.assertTrue(handoff.check_preconditions("devops-agent", json.dumps(data))[0])

    def test_invalid_json_shapes_and_duplicates_fail(self):
        for raw in ['[]', 'null', '{', '{"schema_version":1,"schema_version":1}',
                    '{"schema_version":true}', '{"schema_version":1,"inputs":[]}']:
            self.assertFalse(handoff.check_preconditions("devops-agent", raw)[0])


if __name__ == "__main__":
    unittest.main()
