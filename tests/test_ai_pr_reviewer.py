"""Tests for the optional AI PR Reviewer validation in validate_squad.py."""

import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
from types import ModuleType, SimpleNamespace
import unittest
from unittest import mock


SOURCE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "validate_squad", SOURCE / "scripts/validate_squad.py"
)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)

reviewer_spec = importlib.util.spec_from_file_location(
    "review_agent", SOURCE / "tools/ai-pr-reviewer/review_agent.py"
)
reviewer = importlib.util.module_from_spec(reviewer_spec)
reviewer_spec.loader.exec_module(reviewer)


class AIPRReviewerValidationTests(unittest.TestCase):
    """Validate the optional AI PR Reviewer module."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(
            prefix="agyflow-ai-pr-reviewer-"
        )
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "project"
        self.root.mkdir()
        for name in ("AGENTS.md", "README.md"):
            shutil.copy2(SOURCE / name, self.root / name)
        for name in (".agents", ".github", "config", "docs",
                     "templates", "tools"):
            src = SOURCE / name
            if src.exists():
                shutil.copytree(src, self.root / name)

    def check(self):
        return validator.validate(self.root, False)

    # --- Positive cases ---

    def test_complete_reviewer_passes(self):
        """A complete reviewer installation should produce no errors."""
        self.assertEqual(self.check(), [])

    def test_absent_reviewer_is_ignored(self):
        """Without tools/ai-pr-reviewer/ the validator skips silently."""
        shutil.rmtree(self.root / "tools" / "ai-pr-reviewer")
        (self.root / ".github/workflows/ai-pr-review.yml").unlink()
        (self.root / "docs/ai-pr-reviewer.md").unlink()
        self.assertEqual(self.check(), [])

    def test_partial_reviewer_is_rejected(self):
        shutil.rmtree(self.root / "tools" / "ai-pr-reviewer")
        self.assertTrue(any("review_agent.py" in e for e in self.check()))

    # --- Missing files ---

    def test_missing_policy_rejected(self):
        (self.root / "tools/ai-pr-reviewer/policy.md").unlink()
        self.assertTrue(any("policy.md" in e for e in self.check()))

    def test_missing_prompt_rejected(self):
        (self.root / "tools/ai-pr-reviewer/prompt.md").unlink()
        self.assertTrue(any("prompt.md" in e for e in self.check()))

    def test_missing_review_agent_rejected(self):
        (self.root / "tools/ai-pr-reviewer/review_agent.py").unlink()
        self.assertTrue(any("review_agent.py" in e for e in self.check()))

    def test_missing_requirements_rejected(self):
        (self.root / "tools/ai-pr-reviewer/requirements.txt").unlink()
        self.assertTrue(any("requirements.txt" in e for e in self.check()))

    def test_missing_docs_rejected(self):
        (self.root / "docs/ai-pr-reviewer.md").unlink()
        self.assertTrue(any("ai-pr-reviewer.md" in e for e in self.check()))

    def test_empty_docs_rejected(self):
        (self.root / "docs/ai-pr-reviewer.md").write_text("")
        self.assertTrue(any("ai-pr-reviewer.md" in e for e in self.check()))

    # --- Hardcoded keys ---

    def test_hardcoded_key_in_agent_rejected(self):
        path = self.root / "tools/ai-pr-reviewer/review_agent.py"
        path.write_text(
            path.read_text()
            + '\nKEY = "AIzaSyDfakekey1234567890abcdefghijklmno"\n'
        )
        self.assertTrue(
            any("API key hardcodeada" in e for e in self.check())
        )

    def test_hardcoded_key_in_workflow_rejected(self):
        path = self.root / ".github/workflows/ai-pr-review.yml"
        path.write_text(
            path.read_text()
            + '\n  GEMINI_API_KEY: "AIzaSyDfakekey1234567890abcdefghijklmno"\n'
        )
        self.assertTrue(
            any("API key hardcodeada" in e for e in self.check())
        )

    # --- Insecure workflow ---

    def test_workflow_without_secrets_ref_rejected(self):
        path = self.root / ".github/workflows/ai-pr-review.yml"
        path.write_text(
            path.read_text().replace(
                "secrets.GEMINI_API_KEY", "env.GEMINI_API_KEY"
            )
        )
        self.assertTrue(
            any("secrets.GEMINI_API_KEY" in e for e in self.check())
        )

    def test_workflow_without_read_permissions_rejected(self):
        path = self.root / ".github/workflows/ai-pr-review.yml"
        path.write_text(
            path.read_text().replace("contents: read", "contents: write")
        )
        self.assertTrue(
            any("contents: read" in e for e in self.check())
        )

    def test_workflow_must_fail_when_reviewer_errors(self):
        path = self.root / ".github/workflows/ai-pr-review.yml"
        path.write_text(path.read_text().replace(
            "steps.review.outputs.exit_code != '0'",
            "steps.review.outputs.exit_code == '2'",
        ))
        self.assertTrue(any("no completa" in e for e in self.check()))

    def test_retired_model_rejected(self):
        path = self.root / "tools/ai-pr-reviewer/review_agent.py"
        path.write_text(path.read_text().replace(
            "gemini-3.6-flash", "gemini-2.0-flash"
        ))
        self.assertTrue(any("modelo retirado" in e for e in self.check()))

    def test_structured_schema_is_required(self):
        path = self.root / "tools/ai-pr-reviewer/review_agent.py"
        path.write_text(path.read_text().replace(
            '"response_json_schema": REVIEW_SCHEMA,', ""
        ))
        self.assertTrue(any("esquema de respuesta" in e for e in self.check()))

    def test_reviewer_must_exclude_editable_diagrams(self):
        path = self.root / "tools/ai-pr-reviewer/review_agent.py"
        path.write_text(path.read_text().replace(r'r".*\.excalidraw|"', ''))
        self.assertTrue(any("diagramas editables" in e for e in self.check()))

    def test_workflow_must_block_partial_review(self):
        path = self.root / ".github/workflows/ai-pr-review.yml"
        path.write_text(path.read_text().replace(
            "steps.review.outputs.exit_code == '3'",
            "steps.review.outputs.exit_code == '0'",
        ))
        self.assertTrue(any("revisión parcial" in e for e in self.check()))

    # --- Incomplete policy ---

    def test_policy_missing_sections_rejected(self):
        path = self.root / "tools/ai-pr-reviewer/policy.md"
        path.write_text("# Política\n\nContenido incompleto.\n")
        errors = self.check()
        self.assertTrue(any("falta sección" in e for e in errors))

    def test_policy_partial_sections_rejected(self):
        """Policy with some sections but not all three required ones."""
        path = self.root / "tools/ai-pr-reviewer/policy.md"
        path.write_text(
            "# Política\n\n## Acceso permitido\nSí.\n\n"
            "## Acceso prohibido\nNo.\n"
        )
        errors = self.check()
        self.assertTrue(
            any("Gestión de la API key" in e for e in errors)
        )


class ReviewAgentTests(unittest.TestCase):
    def finding(self, severity="medium"):
        return {
            "severity": severity,
            "category": "security",
            "file": "src/auth.py",
            "lines": "L10-L12",
            "description": "Validación ausente",
            "impact": "Acceso indebido",
        }

    def test_redacts_credentials_before_transmission(self):
        diff = (
            "+GEMINI_API_KEY=AIzaSyDabcdefghijklmnopqrstuvwxyz123456\n"
            "+Authorization: Bearer abcdefghijklmnopqrstuvwxyz123456\n"
            "+-----BEGIN PRIVATE KEY-----\n+secret\n"
            "+-----END PRIVATE KEY-----\n"
        )
        redacted, count = reviewer.redact_sensitive_values(diff)
        self.assertGreaterEqual(count, 3)
        self.assertNotIn("AIzaSyDabcdefghijklmnopqrstuvwxyz123456", redacted)
        self.assertNotIn("abcdefghijklmnopqrstuvwxyz123456", redacted)
        self.assertNotIn("+secret", redacted)
        self.assertIn("REDACTED_POTENTIAL_SECRET", redacted)

    def test_context_budget_and_diagram_filter(self):
        self.assertEqual(reviewer.MAX_DIFF_CHARS_DEFAULT, 50_000)
        raw = (
            "diff --git a/docs/diagrams/map.excalidraw "
            "b/docs/diagrams/map.excalidraw\n+diagram data\n"
            "diff --git a/src/app.py b/src/app.py\n+print('kept')\n"
        )
        filtered = reviewer.filter_diff(raw)
        self.assertNotIn("diagram data", filtered)
        self.assertIn("print('kept')", filtered)

    def test_normalize_recomputes_verdict_from_findings(self):
        value = {
            "findings": [self.finding("critical")],
            "summary": {"verdict": "clean", "critical": 0},
        }
        result = reviewer.normalize_result(value)
        self.assertEqual(result["summary"]["critical"], 1)
        self.assertEqual(result["summary"]["verdict"], "blocked")

    def test_normalize_rejects_invalid_shape(self):
        invalid = self.finding()
        invalid["severity"] = "urgent"
        with self.assertRaises(ValueError):
            reviewer.normalize_result({"findings": [invalid]})

    def test_report_escapes_html_and_mentions(self):
        finding = self.finding()
        finding["description"] = "<script>alert(1)</script> @admins"
        report = reviewer.format_markdown_report(
            reviewer.normalize_result({"findings": [finding]})
        )
        self.assertNotIn("<script>", report)
        self.assertNotIn("@admins", report)

    def test_main_separates_system_instruction_and_blocks_critical(self):
        captured = {}

        class Models:
            def generate_content(self, **kwargs):
                captured.update(kwargs)
                return SimpleNamespace(text=json.dumps({
                    "findings": [self_finding],
                }))

        fake_genai = SimpleNamespace(
            Client=lambda api_key: SimpleNamespace(models=Models())
        )
        fake_google = ModuleType("google")
        fake_google.genai = fake_genai
        self_finding = self.finding("critical")

        with tempfile.TemporaryDirectory(prefix="review-agent-") as temp:
            diff_path = Path(temp) / "change.diff"
            output_path = Path(temp) / "report.md"
            diff_path.write_text(
                "diff --git a/app.py b/app.py\n+print('change')\n"
            )
            argv = [
                "review_agent.py", "--diff", str(diff_path),
                "--output", str(output_path),
            ]
            with mock.patch.dict(
                sys.modules, {"google": fake_google, "google.genai": fake_genai}
            ), mock.patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}), \
                    mock.patch.object(sys, "argv", argv):
                exit_code = reviewer.main()

        self.assertEqual(exit_code, 2)
        self.assertEqual(captured["model"], "gemini-3.6-flash")
        self.assertIn("system_instruction", captured["config"])
        self.assertIn("response_json_schema", captured["config"])
        self.assertNotIn("Sos un reviewer", captured["contents"])
        self.assertIn("pull_request_diff", captured["contents"])

    def test_main_marks_truncated_clean_review_as_partial(self):
        class Models:
            def generate_content(self, **kwargs):
                return SimpleNamespace(text=json.dumps({"findings": []}))

        fake_genai = SimpleNamespace(
            Client=lambda api_key: SimpleNamespace(models=Models())
        )
        fake_google = ModuleType("google")
        fake_google.genai = fake_genai

        with tempfile.TemporaryDirectory(prefix="review-agent-partial-") as temp:
            diff_path = Path(temp) / "change.diff"
            output_path = Path(temp) / "report.md"
            diff_path.write_text(
                "diff --git a/app.py b/app.py\n+" + "x" * 200 + "\n"
            )
            argv = [
                "review_agent.py", "--diff", str(diff_path),
                "--output", str(output_path), "--max-diff-chars", "50",
            ]
            with mock.patch.dict(
                sys.modules, {"google": fake_google, "google.genai": fake_genai}
            ), mock.patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}), \
                    mock.patch.object(sys, "argv", argv):
                exit_code = reviewer.main()
            report = output_path.read_text()

        self.assertEqual(exit_code, 3)
        self.assertIn("diff fue truncado", report)


if __name__ == "__main__":
    unittest.main()
