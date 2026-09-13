"""Unit tests for scripts/pipeline.py."""

import importlib.util
from pathlib import Path
import tempfile
import unittest
import json
import sys
import subprocess

SOURCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE / "scripts"))
from demo_workflow import PRD, evidence, run_demo
spec = importlib.util.spec_from_file_location("pipeline", SOURCE / "scripts/pipeline.py")
pipeline = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pipeline)


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(prefix="test-pipeline-")
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)

    def test_check_prd_gherkin_valid(self):
        prd = self.root / "PRD.md"
        prd.write_text("""# PRD
### [US-01] Autenticación de Usuario
- Como usuario
- Quiero iniciar sesión
- Para ver mi cuenta

#### Criterios:
1. Happy Path:
   Dado un usuario registrado, cuando ingresa clave correcta, entonces accede al dashboard.
2. Sad Path / Error:
   Dado un usuario registrado, cuando ingresa clave incorrecta, entonces muestra mensaje de error.
3. Edge Case:
   Dado un usuario con 3 intentos fallidos, cuando reintenta, entonces bloquea temporalmente por 15 minutos (tiempo límite).
4. Estado Vacío / Carga:
   Dado que el servidor procesa la solicitud, cuando envía el formulario, entonces muestra spinner de carga.
""")
        ok, errors = pipeline.check_prd_gherkin(prd)
        self.assertTrue(ok)
        self.assertEqual(errors, [])

    def test_check_prd_gherkin_missing_scenarios(self):
        prd = self.root / "PRD.md"
        prd.write_text("""# PRD
### [US-01] Búsqueda simple
- Como usuario
- Quiero buscar productos
- Para comprar

#### Criterios:
Dado un usuario, cuando busca algo, entonces ve productos.
""")
        ok, errors = pipeline.check_prd_gherkin(prd)
        self.assertFalse(ok)
        self.assertTrue(any("falta escenario obligatorio" in e for e in errors))

    def test_detect_phase_po(self):
        phase, _, next_actor = pipeline.detect_phase(self.root)
        self.assertEqual(phase, "1_PO")
        self.assertEqual(next_actor, "po-agent")

    def prepare(self):
        (self.root / "PRD.md").write_text(PRD)
        pipeline.record_prd_approval(self.root, "PERSONA FICTICIA", "US-01", "TEST")
        (self.root / "architecture.md").write_text("Arquitectura de fixture")

    def test_missing_approval_and_changed_prd_stay_at_gate(self):
        (self.root / "PRD.md").write_text(PRD)
        self.assertEqual(pipeline.detect_phase(self.root)[0], "1_PO_GATE")
        self.prepare()
        self.assertTrue(pipeline.valid_approval(self.root))
        (self.root / "PRD.md").write_text(PRD + "\nAlcance modificado")
        self.assertEqual(pipeline.detect_phase(self.root)[0], "1_PO_GATE")

    def test_old_approval_in_prose_cannot_override_current_rejection(self):
        self.prepare()
        (self.root / "bug_report.md").write_text("Historial: Resultado: aprobado\nActual: Resultado: rechazado")
        data = evidence("devops-agent")
        data["inputs"]["qa"]["status"] = "rejected"
        (self.root / "handoff.json").write_text(json.dumps(data))
        (self.root / "candidate.json").write_text(json.dumps(dict(schema_version=1, revision="demo-rev-1", qa_run="demo-qa-1", ticket="SIM-US-01")))
        self.assertEqual(pipeline.detect_phase(self.root)[0], "BLOCKED")
        data["inputs"]["qa"]["status"] = "approved"
        (self.root / "handoff.json").write_text(json.dumps(data))
        self.assertEqual(pipeline.detect_phase(self.root)[0], "5_STAGING_REVIEW")
        (self.root / "candidate.json").write_text(json.dumps(dict(schema_version=1, revision="demo-rev-2", qa_run="demo-qa-2", ticket="SIM-US-01")))
        self.assertEqual(pipeline.detect_phase(self.root)[0], "BLOCKED")

    def test_garbage_documents_do_not_skip_prd_gate(self):
        (self.root / "PRD.md").write_text("Borrador sin aprobar")
        (self.root / "sprint_actual.md").write_text("Sin sincronizar")
        (self.root / "bug_report.md").write_text("Resultado: aprobado")
        self.assertEqual(pipeline.detect_phase(self.root)[0], "1_PO_REFINING")

    def test_advance_does_not_claim_or_record_approval(self):
        (self.root / "PRD.md").write_text(PRD)
        r = subprocess.run([sys.executable, str(SOURCE / "scripts/pipeline.py"), "--root", str(self.root), "advance"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0)
        self.assertIn("No se registró ninguna aprobación", r.stdout)
        self.assertFalse((self.root / ".agyflow").exists())

    def test_approval_is_persisted_and_not_overwritten(self):
        self.prepare()
        self.assertTrue(pipeline.valid_approval(self.root))
        with self.assertRaises(FileExistsError):
            pipeline.record_prd_approval(self.root, "Otra persona", "Otro alcance", "TEST")

    def test_every_scenario_requires_its_own_clauses(self):
        (self.root / "PRD.md").write_text(PRD.replace("Dado que no hay horarios, cuando consulto una fecha, entonces veo un estado vacío y puedo cambiarla.", "Vacío y carga, pendiente de definir."))
        self.assertFalse(pipeline.check_prd_gherkin(self.root / "PRD.md")[0])

    def test_malformed_handoff_blocks_without_crashing(self):
        self.prepare()
        for text in ('{', '[]', '{"schema_version":1,"target_role":[]}'):
            (self.root / "handoff.json").write_text(text)
            self.assertEqual(pipeline.detect_phase(self.root)[0], "BLOCKED")

    def test_demo_exercises_rejection_staleness_and_scope_change(self):
        events = run_demo()
        states = [state for _, state, _ in events]
        self.assertIn("5_STAGING_REVIEW", states)
        self.assertGreaterEqual(states.count("BLOCKED"), 3)
        self.assertGreaterEqual(states.count("1_PO_GATE"), 2)


if __name__ == "__main__":
    unittest.main()
