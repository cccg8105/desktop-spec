from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
CLI_MAIN = ROOT_DIR / "cli" / "main.py"
CLI_DIR = ROOT_DIR / "cli"
if str(CLI_DIR) not in sys.path:
    sys.path.insert(0, str(CLI_DIR))

from desktop_spec.commands.check_cmd import run_check


class TestPackagingAndE2E(unittest.TestCase):
    """Pruebas de empaquetado, entrypoint CLI por subprocess y pilotos E2E."""

    def test_cli_main_version_subprocess(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(CLI_MAIN), "--version"],
            cwd=str(ROOT_DIR),
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        self.assertIn("desktop-spec", proc.stdout)
        self.assertIn("0.1.0", proc.stdout)

    def test_cli_main_check_fails_on_uninitialized_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            proc = subprocess.run(
                [sys.executable, str(CLI_MAIN), "check"],
                cwd=tmp,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 1)

    def test_examples_sample_dotnet_desktop_check(self) -> None:
        sample_dir = ROOT_DIR / "examples" / "sample-dotnet-desktop"
        if not sample_dir.is_dir() or not (sample_dir / "docs").is_dir():
            self.skipTest("examples/sample-dotnet-desktop no esta presente en disco.")
        self.assertTrue(run_check(sample_dir))

    def test_examples_sample_pyside6_desktop_check(self) -> None:
        sample_dir = ROOT_DIR / "examples" / "sample-pyside6-desktop"
        if not sample_dir.is_dir() or not (sample_dir / "docs").is_dir():
            self.skipTest("examples/sample-pyside6-desktop no esta presente en disco.")
        self.assertTrue(run_check(sample_dir))


if __name__ == "__main__":
    unittest.main()
