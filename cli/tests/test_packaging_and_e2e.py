from __future__ import annotations

import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from urllib.parse import unquote

ROOT_DIR = Path(__file__).resolve().parents[2]
CLI_MAIN = ROOT_DIR / "cli" / "main.py"
CLI_DIR = ROOT_DIR / "cli"
if str(CLI_DIR) not in sys.path:
    sys.path.insert(0, str(CLI_DIR))

from desktop_spec import __version__
from desktop_spec.commands.check_cmd import run_check
from desktop_spec.detector.ecosystem_detector import ECOSYSTEM_PROFILES

SCHEMA_PATH_RE = re.compile(r"schemas/[A-Za-z0-9_./-]+\.schema\.json")
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")

OBSOLETE_GUIDE_PATTERNS = (
    "--type ",
    "--title ",
    "PROP-001",
    "docs/functional/flows/",
    "docs/design/design-tokens.md",
    "docs/technical/architecture.md",
    ".windsurf/rules/desktop-spec.md",
)


def _strip_markdown_code(text: str) -> str:
    """Elimina bloques de codigo cercados y spans inline para extraer enlaces Markdown reales."""
    cleaned_lines: list[str] = []
    in_fence = False
    fence_char = ""
    fence_len = 0
    for line in text.splitlines():
        stripped = line.lstrip()
        fence_match = re.match(r"^(`{3,}|~{3,})", stripped)
        if fence_match:
            marker = fence_match.group(1)
            if not in_fence:
                in_fence = True
                fence_char = marker[0]
                fence_len = len(marker)
                continue
            if marker[0] == fence_char and len(marker) >= fence_len:
                in_fence = False
                fence_char = ""
                fence_len = 0
                continue
        if not in_fence:
            cleaned_lines.append(re.sub(r"`[^`]*`", "", line))
    return "\n".join(cleaned_lines)


class TestPackagingAndE2E(unittest.TestCase):
    """Pruebas de empaquetado, entrypoint CLI por subprocess, pilotos E2E y anti-doc-drift."""

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
        self.assertIn(__version__, proc.stdout)

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

    def _assert_pilot_sample_passes_strict_check(self, sample_name: str) -> None:
        sample_dir = ROOT_DIR / "examples" / sample_name
        self.assertTrue(
            sample_dir.is_dir() and (sample_dir / "docs").is_dir(),
            msg=f"examples/{sample_name}/docs no esta presente en disco.",
        )
        self.assertTrue(
            run_check(sample_dir, strict_tokens=True),
            msg=f"run_check(..., strict_tokens=True) fallo para examples/{sample_name}.",
        )

    def test_examples_sample_dotnet_desktop_check(self) -> None:
        self._assert_pilot_sample_passes_strict_check("sample-dotnet-desktop")

    def test_examples_sample_pyside6_desktop_check(self) -> None:
        self._assert_pilot_sample_passes_strict_check("sample-pyside6-desktop")

    def test_examples_sample_tauri_desktop_check(self) -> None:
        self._assert_pilot_sample_passes_strict_check("sample-tauri-desktop")

    def test_examples_sample_flutter_desktop_check(self) -> None:
        self._assert_pilot_sample_passes_strict_check("sample-flutter-desktop")

    def test_guides_04_lists_all_real_schemas_and_ecosystems(self) -> None:
        guide_04 = ROOT_DIR / "guides" / "04-cli-harnesses-and-contracts.md"
        self.assertTrue(guide_04.is_file(), msg="Falta guides/04-cli-harnesses-and-contracts.md.")
        content = guide_04.read_text(encoding="utf-8")

        mentioned_schemas = set(SCHEMA_PATH_RE.findall(content))
        self.assertTrue(
            mentioned_schemas,
            msg="guides/04-cli-harnesses-and-contracts.md no menciona ninguna ruta schemas/...schema.json.",
        )

        nonexistent_schemas = sorted(
            rel for rel in mentioned_schemas if not (ROOT_DIR / rel).is_file()
        )
        self.assertEqual(
            nonexistent_schemas,
            [],
            msg=f"Esquemas inexistentes referenciados en guides/04: {nonexistent_schemas}",
        )

        real_schemas = {
            path.relative_to(ROOT_DIR).as_posix()
            for path in (ROOT_DIR / "schemas").rglob("*.schema.json")
        }
        self.assertEqual(
            len(real_schemas),
            9,
            msg=f"Se esperaban 9 esquemas reales en schemas/, encontrados: {sorted(real_schemas)}",
        )
        missing_schemas = sorted(real_schemas - mentioned_schemas)
        self.assertEqual(
            missing_schemas,
            [],
            msg=f"Esquemas reales omitidos en guides/04: {missing_schemas}",
        )

        expected_ecosystems = [profile["ecosystem"] for profile in ECOSYSTEM_PROFILES]
        self.assertEqual(
            len(expected_ecosystems),
            16,
            msg=f"Se esperaban 16 perfiles en ECOSYSTEM_PROFILES, encontrados: {len(expected_ecosystems)}",
        )
        missing_ecosystems = [
            eco
            for eco in expected_ecosystems
            if not re.search(rf"(?<![A-Za-z0-9_-]){re.escape(eco)}(?![A-Za-z0-9_-])", content)
        ]
        self.assertEqual(
            missing_ecosystems,
            [],
            msg=f"Ecosistemas de ECOSYSTEM_PROFILES omitidos en guides/04: {missing_ecosystems}",
        )

    def test_guides_have_no_obsolete_cli_flags_or_broken_paths(self) -> None:
        guide_files = sorted((ROOT_DIR / "guides").glob("*.md"))
        self.assertTrue(guide_files, msg="No se encontraron archivos Markdown en guides/.")

        violations: list[tuple[str, str]] = []
        for guide_path in guide_files:
            content = guide_path.read_text(encoding="utf-8")
            for pattern in OBSOLETE_GUIDE_PATTERNS:
                if pattern in content:
                    violations.append((guide_path.name, pattern))

        self.assertEqual(
            violations,
            [],
            msg=f"Se detectaron flags o rutas obsoletas en guides/: {violations}",
        )

    def test_readme_and_guides_relative_links_exist(self) -> None:
        doc_files = [ROOT_DIR / "README.md", *sorted((ROOT_DIR / "guides").glob("*.md"))]
        broken_links: list[tuple[str, str]] = []

        for md_file in doc_files:
            self.assertTrue(md_file.is_file(), msg=f"Archivo esperado no encontrado: {md_file}")
            cleaned = _strip_markdown_code(md_file.read_text(encoding="utf-8"))
            for raw_target in MARKDOWN_LINK_RE.findall(cleaned):
                target = raw_target.strip()
                if target.startswith("<") and target.endswith(">"):
                    target = target[1:-1].strip()
                else:
                    parts = target.split()
                    target = parts[0] if parts else ""

                if not target or target.startswith(("http://", "https://", "mailto:", "#")):
                    continue

                rel_target = unquote(target.split("#", 1)[0].split("?", 1)[0])
                if not rel_target:
                    continue

                resolved = (md_file.parent / rel_target).resolve()
                if not resolved.exists():
                    broken_links.append((md_file.relative_to(ROOT_DIR).as_posix(), target))

        self.assertEqual(
            broken_links,
            [],
            msg=f"Enlaces relativos rotos en README.md / guides/: {broken_links}",
        )


if __name__ == "__main__":
    unittest.main()
