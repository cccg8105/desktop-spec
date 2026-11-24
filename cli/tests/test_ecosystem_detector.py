import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

CLI_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = CLI_DIR.parent
if str(CLI_DIR) not in sys.path:
    sys.path.insert(0, str(CLI_DIR))

from desktop_spec.detector.ecosystem_detector import (
    ECOSYSTEM_PROFILES,
    build_profile_context,
    detect_desktop_ecosystem,
    get_ecosystem_profile,
)


REQUIRED_PROFILE_KEYS = {
    "ecosystem",
    "runtime_label",
    "family",
    "ui_toolkit",
    "language",
    "embedded_db",
    "unit_test_runner",
    "ui_test_runner",
    "manifest",
    "version_file",
    "format",
    "field",
    "src_ext",
    "src_dir",
    "ui_dir",
    "modules_dir",
    "test_pattern",
}


class TestEcosystemDetector(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_all_11_profiles_match_schema_and_have_required_keys(self):
        schema_path = REPO_ROOT / "schemas" / "technical" / "tech-stack.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        schema_ecosystems = schema["properties"]["ecosystem"]["enum"]

        profile_ecosystems = [p["ecosystem"] for p in ECOSYSTEM_PROFILES]
        self.assertEqual(len(ECOSYSTEM_PROFILES), 11)
        self.assertEqual(profile_ecosystems, schema_ecosystems)

        for profile in ECOSYSTEM_PROFILES:
            self.assertTrue(REQUIRED_PROFILE_KEYS.issubset(profile.keys()), profile["ecosystem"])
            for key in REQUIRED_PROFILE_KEYS:
                self.assertTrue(profile[key], f"{profile['ecosystem']}.{key} vacio")

    def test_get_ecosystem_profile_returns_copy_and_validates(self):
        prof = get_ecosystem_profile("avalonia")
        self.assertEqual(prof["family"], "dotnet")
        prof["ui_toolkit"] = "Modified"
        self.assertEqual(get_ecosystem_profile("avalonia")["ui_toolkit"], "Avalonia UI")

        with self.assertRaises(ValueError):
            get_ecosystem_profile("electron-webview")

    def test_greenfield_detection_empty_and_ignored_entries(self):
        res_empty = detect_desktop_ecosystem(self.tmp)
        self.assertEqual(res_empty["mode"], "greenfield")
        self.assertEqual(res_empty["project_state"], "empty")
        self.assertFalse(res_empty["is_fresh_scaffold"])
        self.assertIsNone(res_empty["detected"])
        self.assertIsNone(res_empty["manifest_path"])
        self.assertIsNone(res_empty["version_path"])

        (self.tmp / ".git").mkdir()
        (self.tmp / ".spec").mkdir()
        (self.tmp / "docs").mkdir()
        (self.tmp / ".gitignore").write_text("bin/\n", encoding="utf-8")
        res_ignored = detect_desktop_ecosystem(self.tmp)
        self.assertEqual(res_ignored["mode"], "greenfield")
        self.assertEqual(res_ignored["project_state"], "empty")

        res_missing = detect_desktop_ecosystem(self.tmp / "nonexistent")
        self.assertEqual(res_missing["mode"], "greenfield")
        self.assertEqual(res_missing["project_state"], "empty")

    def test_custom_unknown_brownfield(self):
        (self.tmp / "README.md").write_text("# Custom Native App\n", encoding="utf-8")
        res = detect_desktop_ecosystem(self.tmp)
        self.assertEqual(res["mode"], "brownfield")
        self.assertEqual(res["project_state"], "brownfield")
        self.assertFalse(res["is_fresh_scaffold"])
        self.assertIsNone(res["detected"])
        self.assertIsNone(res["manifest_path"])

    def test_dotnet_4_profiles_distinction(self):
        cases = [
            (
                "wpf",
                "WpfApp.csproj",
                """<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0-windows</TargetFramework>
    <UseWPF>true</UseWPF>
    <Version>1.0.0</Version>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Microsoft.Data.Sqlite" Version="8.0.0" />
    <PackageReference Include="xunit" Version="2.9.0" />
    <PackageReference Include="FlaUI.UIA3" Version="4.0.0" />
  </ItemGroup>
</Project>""",
                "SQLite (WAL)",
                "xUnit",
                "FlaUI",
            ),
            (
                "winui3",
                "WinUIApp.csproj",
                """<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0-windows10.0.19041.0</TargetFramework>
    <UseWinUI>true</UseWinUI>
    <Version>1.1.0</Version>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Microsoft.WindowsAppSDK" Version="1.6.0" />
  </ItemGroup>
</Project>""",
                "SQLite (WAL)",
                "xUnit",
                "FlaUI / WinAppDriver",
            ),
            (
                "avalonia",
                "AvaloniaApp.csproj",
                """<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <Version>2.0.0</Version>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Avalonia.Desktop" Version="11.2.0" />
    <PackageReference Include="Avalonia.Headless.XUnit" Version="11.2.0" />
    <PackageReference Include="DuckDB.NET.Data.Full" Version="1.1.0" />
    <PackageReference Include="NUnit" Version="4.2.0" />
  </ItemGroup>
</Project>""",
                "DuckDB",
                "NUnit",
                "Avalonia.Headless",
            ),
            (
                "maui-desktop",
                "MauiDesktop.csproj",
                """<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <UseMaui>true</UseMaui>
    <ApplicationDisplayVersion>1.0.0</ApplicationDisplayVersion>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Microsoft.Maui.Controls" Version="8.0.90" />
    <PackageReference Include="SQLitePCLRaw.bundle_e_sqlcipher" Version="2.1.8" />
  </ItemGroup>
</Project>""",
                "SQLCipher",
                "xUnit",
                "Appium / FlaUI",
            ),
        ]

        for expected_eco, csproj_name, content, exp_db, exp_unit, exp_ui in cases:
            proj = self.tmp / expected_eco
            proj.mkdir()
            (proj / csproj_name).write_text(content, encoding="utf-8")
            det = detect_desktop_ecosystem(proj)
            self.assertEqual(det["mode"], "brownfield", expected_eco)
            prof = det["detected"]
            self.assertEqual(prof["ecosystem"], expected_eco)
            self.assertEqual(prof["family"], "dotnet")
            self.assertEqual(prof["manifest"], csproj_name)
            self.assertEqual(prof["format"], "xml")
            self.assertEqual(prof["field"], "Version")
            self.assertEqual(prof["embedded_db"], exp_db)
            self.assertEqual(prof["unit_test_runner"], exp_unit)
            self.assertEqual(prof["ui_test_runner"], exp_ui)

    def test_dotnet_solution_layout_prefers_app_csproj_over_test_csproj(self):
        proj = self.tmp / "dotnet-sln"
        (proj / "src" / "StudioApp").mkdir(parents=True)
        (proj / "tests" / "StudioApp.Tests").mkdir(parents=True)
        (proj / "StudioApp.sln").write_text("", encoding="utf-8")
        (proj / "src" / "StudioApp" / "StudioApp.csproj").write_text(
            '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><Version>1.0.0</Version></PropertyGroup>'
            '<ItemGroup><PackageReference Include="Avalonia" Version="11.2.0" /></ItemGroup></Project>',
            encoding="utf-8",
        )
        (proj / "tests" / "StudioApp.Tests" / "StudioApp.Tests.csproj").write_text(
            '<Project Sdk="Microsoft.NET.Sdk"><ItemGroup><PackageReference Include="xunit" Version="2.9.0" /></ItemGroup></Project>',
            encoding="utf-8",
        )
        (proj / "src" / "StudioApp" / "Program.cs").write_text("class Program {}", encoding="utf-8")

        det = detect_desktop_ecosystem(proj)
        self.assertEqual(det["detected"]["ecosystem"], "avalonia")
        self.assertEqual(det["detected"]["manifest"], "src/StudioApp/StudioApp.csproj")
        self.assertEqual(det["detected"]["unit_test_runner"], "xUnit")
        self.assertEqual(det["manifest_path"], (proj / "src" / "StudioApp" / "StudioApp.csproj").resolve())

    def test_python_3_profiles_and_setup_cfg_fallback(self):
        cases = [
            (
                "pyside6",
                "pyproject.toml",
                '[project]\nname = "app"\nversion = "0.1.0"\ndependencies = ["PySide6>=6.7", "sqlmodel>=0.0.21"]\n'
                '[project.optional-dependencies]\ndev = ["pytest", "pytest-qt"]\n',
                "toml",
                "SQLite (WAL)",
                "pytest-qt",
            ),
            (
                "pyqt6",
                "pyproject.toml",
                '[project]\nname = "app"\nversion = "0.2.0"\ndependencies = ["PyQt6>=6.7", "sqlcipher3>=0.5"]\n',
                "toml",
                "SQLCipher",
                "pytest-qt",
            ),
            (
                "flet",
                "pyproject.toml",
                '[project]\nname = "app"\nversion = "0.3.0"\ndependencies = ["flet>=0.24", "duckdb>=1.1"]\n',
                "toml",
                "DuckDB",
                "pytest",
            ),
            (
                "pyqt6",
                "setup.cfg",
                "[metadata]\nname = legacy_qt\nversion = 1.0.4\n[options]\ninstall_requires =\n    PyQt6>=6.6\n    TinyDB>=4.8\n",
                "cfg",
                "TinyDB",
                "pytest-qt",
            ),
        ]

        for idx, (exp_eco, manifest_name, content, exp_fmt, exp_db, exp_ui_test) in enumerate(cases):
            proj = self.tmp / f"py-{idx}"
            proj.mkdir()
            (proj / manifest_name).write_text(content, encoding="utf-8")
            det = detect_desktop_ecosystem(proj)
            prof = det["detected"]
            self.assertEqual(prof["ecosystem"], exp_eco)
            self.assertEqual(prof["family"], "python")
            self.assertEqual(prof["manifest"], manifest_name)
            self.assertEqual(prof["format"], exp_fmt)
            self.assertEqual(prof["embedded_db"], exp_db)
            self.assertEqual(prof["ui_test_runner"], exp_ui_test)

    def test_jvm_profiles_gradle_and_maven(self):
        compose_proj = self.tmp / "jvm-compose"
        compose_proj.mkdir()
        (compose_proj / "build.gradle.kts").write_text(
            'plugins {\n    id("org.jetbrains.compose") version "1.7.0"\n}\n'
            'version = "1.2.0"\n'
            'dependencies {\n    implementation("app.cash.sqldelight:sqlite-driver:2.0.2")\n'
            '    testImplementation("io.kotest:kotest-runner-junit5:5.9.0")\n}\n',
            encoding="utf-8",
        )
        det_compose = detect_desktop_ecosystem(compose_proj)
        self.assertEqual(det_compose["detected"]["ecosystem"], "compose-desktop")
        self.assertEqual(det_compose["detected"]["family"], "jvm")
        self.assertEqual(det_compose["detected"]["format"], "gradle")
        self.assertEqual(det_compose["detected"]["unit_test_runner"], "Kotest")
        self.assertEqual(det_compose["detected"]["embedded_db"], "SQLite (WAL)")

        fx_gradle = self.tmp / "jvm-fx-gradle"
        fx_gradle.mkdir()
        (fx_gradle / "build.gradle").write_text(
            "plugins {\n    id 'org.openjfx.javafxplugin' version '0.1.0'\n}\n"
            "version '0.9.0'\n"
            "dependencies {\n    testImplementation 'org.testfx:testfx-junit5:4.0.18'\n}\n",
            encoding="utf-8",
        )
        det_fx = detect_desktop_ecosystem(fx_gradle)
        self.assertEqual(det_fx["detected"]["ecosystem"], "javafx")
        self.assertEqual(det_fx["detected"]["manifest"], "build.gradle")
        self.assertEqual(det_fx["detected"]["format"], "gradle")
        self.assertEqual(det_fx["detected"]["ui_test_runner"], "TestFX")

        fx_maven = self.tmp / "jvm-fx-maven"
        fx_maven.mkdir()
        (fx_maven / "pom.xml").write_text(
            "<project><version>2.1.0</version><dependencies>"
            "<dependency><groupId>org.openjfx</groupId><artifactId>javafx-controls</artifactId></dependency>"
            "<dependency><groupId>org.xerial</groupId><artifactId>sqlite-jdbc</artifactId></dependency>"
            "</dependencies></project>",
            encoding="utf-8",
        )
        det_mvn = detect_desktop_ecosystem(fx_maven)
        self.assertEqual(det_mvn["detected"]["ecosystem"], "javafx")
        self.assertEqual(det_mvn["detected"]["manifest"], "pom.xml")
        self.assertEqual(det_mvn["detected"]["format"], "xml")
        self.assertEqual(det_mvn["detected"]["embedded_db"], "SQLite (WAL)")

    def test_rust_native_and_qt_cpp_profiles(self):
        rust_proj = self.tmp / "rust-slint"
        rust_proj.mkdir()
        (rust_proj / "Cargo.toml").write_text(
            '[package]\nname = "cad_viewer"\nversion = "0.4.0"\n'
            '[dependencies]\nslint = "1.8"\nredb = "2.2"\n',
            encoding="utf-8",
        )
        det_rust = detect_desktop_ecosystem(rust_proj)
        self.assertEqual(det_rust["detected"]["ecosystem"], "rust-native")
        self.assertEqual(det_rust["detected"]["family"], "rust-cpp")
        self.assertEqual(det_rust["detected"]["ui_toolkit"], "Slint")
        self.assertEqual(det_rust["detected"]["ui_test_runner"], "slint-testing")
        self.assertEqual(det_rust["detected"]["embedded_db"], "redb (Embedded KV)")

        qt_proj = self.tmp / "qt-cmake"
        qt_proj.mkdir()
        (qt_proj / "CMakeLists.txt").write_text(
            "cmake_minimum_required(VERSION 3.24)\n"
            "project(AudioBench VERSION 1.0.0 LANGUAGES CXX)\n"
            "find_package(Qt6 REQUIRED COMPONENTS Quick Sql Test)\n"
            "find_package(GTest REQUIRED)\n",
            encoding="utf-8",
        )
        det_qt = detect_desktop_ecosystem(qt_proj)
        self.assertEqual(det_qt["detected"]["ecosystem"], "qt-cpp")
        self.assertEqual(det_qt["detected"]["family"], "rust-cpp")
        self.assertEqual(det_qt["detected"]["format"], "cmake")
        self.assertEqual(det_qt["detected"]["ui_toolkit"], "Qt6 Quick (QML)")
        self.assertEqual(det_qt["detected"]["unit_test_runner"], "GoogleTest")
        self.assertEqual(det_qt["detected"]["ui_test_runner"], "Qt Test")
        self.assertEqual(det_qt["detected"]["embedded_db"], "SQLite (WAL)")

    def test_fresh_scaffold_vs_brownfield_native_projects(self):
        py_scaf = self.tmp / "py-scaffold"
        (py_scaf / "src" / "ui").mkdir(parents=True)
        (py_scaf / "pyproject.toml").write_text(
            '[project]\nname = "notes"\nversion = "0.1.0"\ndependencies = ["PySide6"]\n',
            encoding="utf-8",
        )
        (py_scaf / "src" / "__init__.py").write_text("", encoding="utf-8")
        (py_scaf / "src" / "main.py").write_text("def main(): pass\n", encoding="utf-8")
        (py_scaf / "src" / "ui" / "main_window.py").write_text("class MainWindow: pass\n", encoding="utf-8")

        det_scaf = detect_desktop_ecosystem(py_scaf)
        self.assertEqual(det_scaf["mode"], "brownfield")
        self.assertEqual(det_scaf["project_state"], "scaffold")
        self.assertTrue(det_scaf["is_fresh_scaffold"])

        # Agregar un modulo de dominio pasa a brownfield real
        (py_scaf / "src" / "modules" / "notes").mkdir(parents=True)
        (py_scaf / "src" / "modules" / "notes" / "service.py").write_text("pass\n", encoding="utf-8")
        det_mod = detect_desktop_ecosystem(py_scaf)
        self.assertEqual(det_mod["project_state"], "brownfield")
        self.assertFalse(det_mod["is_fresh_scaffold"])

        # Rust scaffold con suite propia de test pasa a brownfield
        rs_scaf = self.tmp / "rs-scaffold"
        (rs_scaf / "src").mkdir(parents=True)
        (rs_scaf / "ui").mkdir()
        (rs_scaf / "Cargo.toml").write_text('[package]\nname="app"\nversion="0.1.0"\n', encoding="utf-8")
        (rs_scaf / "src" / "main.rs").write_text("fn main() {}\n", encoding="utf-8")
        (rs_scaf / "ui" / "app.slint").write_text("export component App {}\n", encoding="utf-8")
        self.assertTrue(detect_desktop_ecosystem(rs_scaf)["is_fresh_scaffold"])

        (rs_scaf / "tests").mkdir()
        (rs_scaf / "tests" / "core_test.rs").write_text("#[test] fn ok() {}\n", encoding="utf-8")
        self.assertFalse(detect_desktop_ecosystem(rs_scaf)["is_fresh_scaffold"])

        # Mas de 2 archivos fuente/UI iniciales -> brownfield
        cs_scaf = self.tmp / "cs-scaffold"
        cs_scaf.mkdir()
        (cs_scaf / "App.csproj").write_text(
            '<Project><ItemGroup><PackageReference Include="Avalonia" /></ItemGroup></Project>',
            encoding="utf-8",
        )
        (cs_scaf / "Program.cs").write_text("class Program {}", encoding="utf-8")
        (cs_scaf / "MainWindow.axaml").write_text("<Window />", encoding="utf-8")
        self.assertTrue(detect_desktop_ecosystem(cs_scaf)["is_fresh_scaffold"])

        (cs_scaf / "SecondWindow.axaml").write_text("<Window />", encoding="utf-8")
        self.assertFalse(detect_desktop_ecosystem(cs_scaf)["is_fresh_scaffold"])

    def test_build_profile_context_explicit_and_version_fallback(self):
        empty_prof = build_profile_context(self.tmp, "qt-cpp")
        self.assertEqual(empty_prof["ecosystem"], "qt-cpp")
        self.assertEqual(empty_prof["manifest"], "CMakeLists.txt")
        self.assertEqual(empty_prof["format"], "cmake")

        ver_dir = self.tmp / "version-only"
        ver_dir.mkdir()
        (ver_dir / "VERSION").write_text("0.2.0\n", encoding="utf-8")
        prof_fallback = build_profile_context(ver_dir, "wpf")
        self.assertEqual(prof_fallback["version_file"], "VERSION")
        self.assertEqual(prof_fallback["format"], "plain")


if __name__ == "__main__":
    unittest.main()
