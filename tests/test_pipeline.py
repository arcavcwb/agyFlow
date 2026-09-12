"""Unit tests for scripts/pipeline.py."""

import importlib.util
from pathlib import Path
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1]
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

    def test_detect_phase_contracts(self):
        (self.root / "PRD.md").write_text("# PRD\nAprobado por Juan Pérez el 2026-09-12.\n### [US-01] Story\nDado x cuando y entonces z.\nHappy path, error, edge case limite, estado vacio.")
        (self.root / "sprint_actual.md").write_text("# Sprint\nEstado: inicializado en Plane\n")
        phase, _, next_actor = pipeline.detect_phase(self.root)
        self.assertEqual(phase, "3_CONTRACTS")
        self.assertEqual(next_actor, "backend-dev-agent")


if __name__ == "__main__":
    unittest.main()
