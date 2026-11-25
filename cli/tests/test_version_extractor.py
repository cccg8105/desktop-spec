import shutil
import sys
import tempfile
import unittest
from pathlib import Path

CLI_DIR = Path(__file__).resolve().parent.parent
if str(CLI_DIR) not in sys.path:
    sys.path.insert(0, str(CLI_DIR))

from desktop_spec.detector.version_extractor import (
    compare_versions,
    compute_next_milestone,
    extract_version,
    parse_version_tuple,
    sync_multi_manifest_versions,
    update_version,
)


class TestVersionExtractor(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_xml_csproj_and_maui_and_pom(self):
        csproj = self.test_dir / "MyApp.csproj"
        csproj.write_text(
            '<Project Sdk="Microsoft.NET.Sdk">\n'
            "  <PropertyGroup>\n"
            "    <OutputType>WinExe</OutputType>\n"
            "    <Version>1.2.3</Version>\n"
            "  </PropertyGroup>\n"
            "</Project>\n",
            encoding="utf-8",
        )
        self.assertEqual(extract_version(csproj, "xml"), "1.2.3")
        self.assertTrue(update_version(csproj, "xml", "v1.3.0"))
        self.assertEqual(extract_version(csproj, "xml"), "1.3.0")

        maui = self.test_dir / "MauiApp.csproj"
        maui.write_text(
            '<Project Sdk="Microsoft.NET.Sdk">\n'
            "  <PropertyGroup>\n"
            "    <UseMaui>true</UseMaui>\n"
            "    <ApplicationDisplayVersion>2.0.1</ApplicationDisplayVersion>\n"
            "  </PropertyGroup>\n"
            "</Project>\n",
            encoding="utf-8",
        )
        self.assertEqual(extract_version(maui, "xml"), "2.0.1")
        self.assertTrue(update_version(maui, "xml", "2.1.0"))
        self.assertEqual(extract_version(maui, "xml"), "2.1.0")

        pom = self.test_dir / "pom.xml"
        pom.write_text(
            "<project>\n"
            "  <parent><version>3.2.0</version></parent>\n"
            "  <version>1.4.2</version>\n"
            "  <dependencies><dependency><version>9.9.9</version></dependency></dependencies>\n"
            "</project>\n",
            encoding="utf-8",
        )
        self.assertEqual(extract_version(pom, "xml"), "1.4.2")
        self.assertTrue(update_version(pom, "xml", "1.5.0"))
        updated_pom = pom.read_text(encoding="utf-8")
        self.assertIn("<parent><version>3.2.0</version></parent>", updated_pom)
        self.assertIn("<version>1.5.0</version>", updated_pom)
        self.assertIn("<dependency><version>9.9.9</version></dependency>", updated_pom)

    def test_toml_pyproject_and_cargo(self):
        pyproject = self.test_dir / "pyproject.toml"
        pyproject.write_text(
            "[tool.ruff]\n"
            'target-version = "py39"\n\n'
            "[project]\n"
            'name = "desktop-notes"\n'
            'version = "0.5.1"\n',
            encoding="utf-8",
        )
        self.assertEqual(extract_version(pyproject, "toml"), "0.5.1")
        self.assertTrue(update_version(pyproject, "toml", "0.6.0"))
        self.assertEqual(extract_version(pyproject, "toml"), "0.6.0")

        cargo = self.test_dir / "Cargo.toml"
        cargo.write_text(
            "[package]\n"
            'name = "cad-app"\n'
            'version = "0.2.0"\n'
            'edition = "2021"\n\n'
            "[dependencies]\n"
            'slint = "1.8"\n',
            encoding="utf-8",
        )
        self.assertEqual(extract_version(cargo, "toml"), "0.2.0")
        self.assertTrue(update_version(cargo, "toml", "0.3.0"))
        self.assertEqual(extract_version(cargo, "toml"), "0.3.0")

    def test_gradle_kotlin_and_groovy(self):
        kts = self.test_dir / "build.gradle.kts"
        kts.write_text(
            'group = "com.acme"\n'
            'version = "1.0.0"\n',
            encoding="utf-8",
        )
        self.assertEqual(extract_version(kts, "gradle"), "1.0.0")
        self.assertTrue(update_version(kts, "gradle", "1.1.0"))
        self.assertEqual(extract_version(kts, "gradle"), "1.1.0")

        groovy = self.test_dir / "build.gradle"
        groovy.write_text(
            "group 'com.acme'\n"
            "version '2.3.4'\n",
            encoding="utf-8",
        )
        self.assertEqual(extract_version(groovy, "gradle"), "2.3.4")
        self.assertTrue(update_version(groovy, "gradle", "2.4.0"))
        self.assertIn("version '2.4.0'", groovy.read_text(encoding="utf-8"))

    def test_cfg_setup(self):
        cfg = self.test_dir / "setup.cfg"
        cfg.write_text(
            "[metadata]\n"
            "name = desktop_tool\n"
            "version = 0.8.1\n",
            encoding="utf-8",
        )
        self.assertEqual(extract_version(cfg, "cfg"), "0.8.1")
        self.assertTrue(update_version(cfg, "cfg", "0.9.0"))
        self.assertEqual(extract_version(cfg, "cfg"), "0.9.0")
        self.assertIn("version = 0.9.0", cfg.read_text(encoding="utf-8"))

    def test_cmake_single_line_and_multiline_preserves_languages_and_args(self):
        cmake_single = self.test_dir / "CMakeLists.txt"
        cmake_single.write_text(
            "cmake_minimum_required(VERSION 3.24)\n"
            "project(MyDesktopApp VERSION 1.2.3 LANGUAGES CXX)\n"
            "find_package(Qt6 REQUIRED COMPONENTS Widgets)\n",
            encoding="utf-8",
        )
        self.assertEqual(extract_version(cmake_single, "cmake"), "1.2.3")
        self.assertTrue(update_version(cmake_single, "cmake", "v1.3.0"))
        self.assertEqual(extract_version(cmake_single, "cmake"), "1.3.0")
        self.assertIn(
            "project(MyDesktopApp VERSION 1.3.0 LANGUAGES CXX)",
            cmake_single.read_text(encoding="utf-8"),
        )

        cmake_multi = self.test_dir / "CMakeLists_multi.txt"
        cmake_multi.write_text(
            "# project(CommentedOut VERSION 9.9.9 LANGUAGES C)\n"
            "cmake_minimum_required(VERSION 3.25)\n"
            "project(\n"
            "    StudioSuite\n"
            "    LANGUAGES C CXX\n"
            "    VERSION 0.4.0\n"
            '    DESCRIPTION "Native Qt6 Studio"\n'
            ")\n",
            encoding="utf-8",
        )
        self.assertEqual(extract_version(cmake_multi, "cmake"), "0.4.0")
        self.assertTrue(update_version(cmake_multi, "cmake", "0.5.0"))
        updated_multi = cmake_multi.read_text(encoding="utf-8")
        self.assertIn("# project(CommentedOut VERSION 9.9.9 LANGUAGES C)", updated_multi)
        self.assertIn("LANGUAGES C CXX", updated_multi)
        self.assertIn("VERSION 0.5.0", updated_multi)
        self.assertIn('DESCRIPTION "Native Qt6 Studio"', updated_multi)

        cmake_no_ver = self.test_dir / "CMakeLists_nover.txt"
        cmake_no_ver.write_text(
            "cmake_minimum_required(VERSION 3.24)\n"
            "project(NoVersionApp LANGUAGES CXX)\n",
            encoding="utf-8",
        )
        self.assertIsNone(extract_version(cmake_no_ver, "cmake"))
        self.assertFalse(update_version(cmake_no_ver, "cmake", "1.0.0"))

    def test_plain_json_and_missing_files(self):
        ver_file = self.test_dir / "VERSION"
        self.assertTrue(update_version(ver_file, "plain", "v2.1.0"))
        self.assertEqual(extract_version(ver_file, "plain"), "2.1.0")

        pkg = self.test_dir / "package.json"
        pkg.write_text('{\n  "name": "app",\n  "version": "1.0.0"\n}\n', encoding="utf-8")
        self.assertEqual(extract_version(pkg, "json"), "1.0.0")
        self.assertTrue(update_version(pkg, "json", "1.1.0"))
        self.assertEqual(extract_version(pkg, "json"), "1.1.0")

        missing = self.test_dir / "missing.toml"
        self.assertIsNone(extract_version(missing, "toml"))
        self.assertFalse(update_version(missing, "toml", "1.0.0"))

    def test_parse_compare_and_compute_next_milestone(self):
        self.assertEqual(parse_version_tuple("v1.2.3-beta.1"), (1, 2, 3))
        self.assertEqual(parse_version_tuple("2026.11.2"), (2026, 11, 2))
        self.assertEqual(parse_version_tuple("invalid"), (0,))

        self.assertEqual(compare_versions("1.1.0", "1.0.0"), 1)
        self.assertEqual(compare_versions("v1.0.0", "1.0"), 0)
        self.assertEqual(compare_versions("0.2.0", "1.0.0"), -1)

        self.assertEqual(compute_next_milestone("1.0.0", "semver"), "v1.1.0")
        self.assertEqual(compute_next_milestone("4", "sequential"), "v5")
        self.assertEqual(compute_next_milestone("1.4", "sequential"), "v1.5")

        calver_old = compute_next_milestone("2020.01.3", "calver")
        self.assertTrue(calver_old.endswith(".1"))
        self.assertTrue(calver_old.startswith("v"))

    def test_yaml_and_sync_multi_manifest_versions(self):
        pubspec = self.test_dir / "pubspec.yaml"
        pubspec.write_text(
            "name: desktop_app\ndescription: Flutter desktop\nversion: 1.2.3+4\n",
            encoding="utf-8",
        )
        self.assertEqual(extract_version(pubspec, "yaml"), "1.2.3+4")
        self.assertTrue(update_version(pubspec, "yaml", "2.0.0"))
        self.assertEqual(extract_version(pubspec, "yaml"), "2.0.0")

        pkg = self.test_dir / "package.json"
        pkg.write_text('{\n  "name": "tauri-ui",\n  "version": "1.0.0"\n}\n', encoding="utf-8")
        cargo = self.test_dir / "Cargo.toml"
        cargo.write_text('[package]\nname = "tauri-app"\nversion = "1.0.0"\n', encoding="utf-8")
        tauri_conf = self.test_dir / "tauri.conf.json"
        tauri_conf.write_text('{\n  "version": "1.0.0"\n}\n', encoding="utf-8")

        results = sync_multi_manifest_versions([pkg, cargo, tauri_conf], "2.5.0")
        self.assertTrue(all(results.values()))
        self.assertEqual(extract_version(pkg, "json"), "2.5.0")
        self.assertEqual(extract_version(cargo, "toml"), "2.5.0")
        self.assertEqual(extract_version(tauri_conf, "json"), "2.5.0")


if __name__ == "__main__":
    unittest.main()
