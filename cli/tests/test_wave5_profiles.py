"""Pruebas unitarias para los 5 perfiles de la Wave 5 y retrocompatibilidad v1.0.0."""

import json
import tempfile
import unittest
from pathlib import Path

from desktop_spec.commands.check_cmd import DESKTOP_SOURCE_EXTENSIONS
from desktop_spec.commands.new_req_cmd import _resolve_desktop_artifact
from desktop_spec.common import _ECOSYSTEM_DEFAULT_EXT
from desktop_spec.detector.ecosystem_detector import (
    detect_desktop_ecosystem,
    get_ecosystem_profile,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


class Wave5ProfilesTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_detect_tauri_profile(self):
        (self.root / "src-tauri").mkdir()
        (self.root / "src-tauri" / "Cargo.toml").write_text(
            '[package]\nname = "app"\nversion = "0.2.0"\n', encoding="utf-8"
        )
        res = detect_desktop_ecosystem(self.root)
        self.assertEqual(res["mode"], "brownfield")
        self.assertEqual(res["detected"]["ecosystem"], "tauri")

    def test_detect_electron_profile(self):
        (self.root / "package.json").write_text(
            json.dumps({"name": "el-app", "version": "1.0.0", "devDependencies": {"electron": "^30.0.0"}}),
            encoding="utf-8",
        )
        res = detect_desktop_ecosystem(self.root)
        self.assertEqual(res["mode"], "brownfield")
        self.assertEqual(res["detected"]["ecosystem"], "electron")

    def test_detect_wails_profile(self):
        (self.root / "wails.json").write_text(
            json.dumps({"name": "wails-app", "version": "0.1.0"}), encoding="utf-8"
        )
        res = detect_desktop_ecosystem(self.root)
        self.assertEqual(res["mode"], "brownfield")
        self.assertEqual(res["detected"]["ecosystem"], "wails")

    def test_detect_flutter_desktop_profile(self):
        (self.root / "pubspec.yaml").write_text(
            "name: flutter_app\nversion: 1.0.0+1\n", encoding="utf-8"
        )
        res = detect_desktop_ecosystem(self.root)
        self.assertEqual(res["mode"], "brownfield")
        self.assertEqual(res["detected"]["ecosystem"], "flutter-desktop")

    def test_detect_swift_macos_profile(self):
        (self.root / "Package.swift").write_text(
            "// swift-tools-version: 5.9\nimport PackageDescription\n", encoding="utf-8"
        )
        res = detect_desktop_ecosystem(self.root)
        self.assertEqual(res["mode"], "brownfield")
        self.assertEqual(res["detected"]["ecosystem"], "swift-macos")

    def test_extensions_and_artifact_resolution(self):
        for eco in ("tauri", "electron", "wails", "flutter-desktop", "swift-macos"):
            profile = get_ecosystem_profile(eco)
            self.assertIn(eco, _ECOSYSTEM_DEFAULT_EXT)
            self.assertIn(profile["src_ext"], DESKTOP_SOURCE_EXTENSIONS)
            ui_path = _resolve_desktop_artifact(
                {"ui_dir": profile["ui_dir"], "modules_dir": profile["modules_dir"], "src_ext": profile["src_ext"]},
                eco,
                "ui-only",
                "core",
                "main-view",
                "main_view",
                "MainView",
            )
            self.assertTrue(ui_path.startswith(profile["ui_dir"]))

        for ext in (".ts", ".tsx", ".js", ".jsx", ".go", ".dart", ".swift"):
            self.assertIn(ext, DESKTOP_SOURCE_EXTENSIONS)

    def test_schemas_wave5_and_v1_backward_compat(self):
        tech_schema = json.loads(
            (REPO_ROOT / "schemas" / "technical" / "tech-stack.schema.json").read_text(encoding="utf-8")
        )
        ecos = tech_schema["properties"]["ecosystem"]["enum"]
        self.assertEqual(len(ecos), 16)
        for eco in ("tauri", "electron", "wails", "flutter-desktop", "swift-macos"):
            self.assertIn(eco, ecos)

        win_schema = json.loads(
            (REPO_ROOT / "schemas" / "technical" / "windowing-and-os-contracts.schema.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertNotIn("ipc_ffi_contracts", win_schema["required"])
        self.assertIn("ipc_ffi_contracts", win_schema["properties"])


if __name__ == "__main__":
    unittest.main()
