"""Detector de ecosistemas desktop nativos y contexto de proyecto para desktop-spec."""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


ECOSYSTEM_PROFILES: List[Dict[str, str]] = [
    {
        "ecosystem": "wpf",
        "runtime_label": "WPF (.NET)",
        "family": "dotnet",
        "ui_toolkit": "WPF (XAML)",
        "language": "C#",
        "embedded_db": "SQLite (WAL)",
        "unit_test_runner": "xUnit",
        "ui_test_runner": "FlaUI",
        "manifest": "app.csproj",
        "version_file": "app.csproj",
        "format": "xml",
        "field": "Version",
        "src_ext": ".cs",
        "src_dir": "src",
        "ui_dir": "src/Views",
        "modules_dir": "src/Modules",
        "test_pattern": "tests/{slug_pascal}Tests.cs",
    },
    {
        "ecosystem": "winui3",
        "runtime_label": "WinUI 3 (Windows App SDK)",
        "family": "dotnet",
        "ui_toolkit": "WinUI 3",
        "language": "C#",
        "embedded_db": "SQLite (WAL)",
        "unit_test_runner": "xUnit",
        "ui_test_runner": "FlaUI / WinAppDriver",
        "manifest": "app.csproj",
        "version_file": "app.csproj",
        "format": "xml",
        "field": "Version",
        "src_ext": ".cs",
        "src_dir": "src",
        "ui_dir": "src/Views",
        "modules_dir": "src/Modules",
        "test_pattern": "tests/{slug_pascal}Tests.cs",
    },
    {
        "ecosystem": "avalonia",
        "runtime_label": "Avalonia UI (.NET)",
        "family": "dotnet",
        "ui_toolkit": "Avalonia UI",
        "language": "C#",
        "embedded_db": "SQLite (WAL)",
        "unit_test_runner": "xUnit",
        "ui_test_runner": "Avalonia.Headless",
        "manifest": "app.csproj",
        "version_file": "app.csproj",
        "format": "xml",
        "field": "Version",
        "src_ext": ".cs",
        "src_dir": "src",
        "ui_dir": "src/Views",
        "modules_dir": "src/Modules",
        "test_pattern": "tests/{slug_pascal}Tests.cs",
    },
    {
        "ecosystem": "maui-desktop",
        "runtime_label": ".NET MAUI Desktop",
        "family": "dotnet",
        "ui_toolkit": ".NET MAUI",
        "language": "C#",
        "embedded_db": "SQLite (WAL)",
        "unit_test_runner": "xUnit",
        "ui_test_runner": "Appium / FlaUI",
        "manifest": "app.csproj",
        "version_file": "app.csproj",
        "format": "xml",
        "field": "Version",
        "src_ext": ".cs",
        "src_dir": "src",
        "ui_dir": "src/Views",
        "modules_dir": "src/Modules",
        "test_pattern": "tests/{slug_pascal}Tests.cs",
    },
    {
        "ecosystem": "pyside6",
        "runtime_label": "PySide6 (Qt for Python)",
        "family": "python",
        "ui_toolkit": "PySide6 (Qt6)",
        "language": "Python",
        "embedded_db": "SQLite (WAL)",
        "unit_test_runner": "pytest",
        "ui_test_runner": "pytest-qt",
        "manifest": "pyproject.toml",
        "version_file": "pyproject.toml",
        "format": "toml",
        "field": "version",
        "src_ext": ".py",
        "src_dir": "src",
        "ui_dir": "src/ui",
        "modules_dir": "src/modules",
        "test_pattern": "tests/test_{slug_snake}.py",
    },
    {
        "ecosystem": "pyqt6",
        "runtime_label": "PyQt6 (Qt for Python)",
        "family": "python",
        "ui_toolkit": "PyQt6",
        "language": "Python",
        "embedded_db": "SQLite (WAL)",
        "unit_test_runner": "pytest",
        "ui_test_runner": "pytest-qt",
        "manifest": "pyproject.toml",
        "version_file": "pyproject.toml",
        "format": "toml",
        "field": "version",
        "src_ext": ".py",
        "src_dir": "src",
        "ui_dir": "src/ui",
        "modules_dir": "src/modules",
        "test_pattern": "tests/test_{slug_snake}.py",
    },
    {
        "ecosystem": "flet",
        "runtime_label": "Flet Desktop (Python)",
        "family": "python",
        "ui_toolkit": "Flet",
        "language": "Python",
        "embedded_db": "SQLite (WAL)",
        "unit_test_runner": "pytest",
        "ui_test_runner": "pytest",
        "manifest": "pyproject.toml",
        "version_file": "pyproject.toml",
        "format": "toml",
        "field": "version",
        "src_ext": ".py",
        "src_dir": "src",
        "ui_dir": "src/ui",
        "modules_dir": "src/modules",
        "test_pattern": "tests/test_{slug_snake}.py",
    },
    {
        "ecosystem": "compose-desktop",
        "runtime_label": "Compose Multiplatform Desktop (JVM)",
        "family": "jvm",
        "ui_toolkit": "Compose Multiplatform",
        "language": "Kotlin",
        "embedded_db": "SQLite (WAL)",
        "unit_test_runner": "JUnit 5",
        "ui_test_runner": "Compose UI Test",
        "manifest": "build.gradle.kts",
        "version_file": "build.gradle.kts",
        "format": "gradle",
        "field": "version",
        "src_ext": ".kt",
        "src_dir": "src/main/kotlin",
        "ui_dir": "src/main/kotlin/ui",
        "modules_dir": "src/main/kotlin/modules",
        "test_pattern": "src/test/kotlin/{slug_pascal}Test.kt",
    },
    {
        "ecosystem": "javafx",
        "runtime_label": "JavaFX (JVM)",
        "family": "jvm",
        "ui_toolkit": "JavaFX",
        "language": "Java",
        "embedded_db": "SQLite (WAL)",
        "unit_test_runner": "JUnit 5",
        "ui_test_runner": "TestFX",
        "manifest": "build.gradle.kts",
        "version_file": "build.gradle.kts",
        "format": "gradle",
        "field": "version",
        "src_ext": ".java",
        "src_dir": "src/main/java",
        "ui_dir": "src/main/java/ui",
        "modules_dir": "src/main/java/modules",
        "test_pattern": "src/test/java/{slug_pascal}Test.java",
    },
    {
        "ecosystem": "rust-native",
        "runtime_label": "Rust Native (Slint / Iced / egui)",
        "family": "rust-cpp",
        "ui_toolkit": "Slint",
        "language": "Rust",
        "embedded_db": "SQLite (WAL)",
        "unit_test_runner": "cargo test",
        "ui_test_runner": "cargo test",
        "manifest": "Cargo.toml",
        "version_file": "Cargo.toml",
        "format": "toml",
        "field": "version",
        "src_ext": ".rs",
        "src_dir": "src",
        "ui_dir": "src/ui",
        "modules_dir": "src/modules",
        "test_pattern": "tests/{slug_snake}_test.rs",
    },
    {
        "ecosystem": "qt-cpp",
        "runtime_label": "Qt6 (C++ / CMake)",
        "family": "rust-cpp",
        "ui_toolkit": "Qt6 Widgets / Quick",
        "language": "C++",
        "embedded_db": "SQLite (WAL)",
        "unit_test_runner": "GoogleTest",
        "ui_test_runner": "Qt Test",
        "manifest": "CMakeLists.txt",
        "version_file": "CMakeLists.txt",
        "format": "cmake",
        "field": "version",
        "src_ext": ".cpp",
        "src_dir": "src",
        "ui_dir": "src/ui",
        "modules_dir": "src/modules",
        "test_pattern": "tests/{slug_snake}_test.cpp",
    },
    {
        "ecosystem": "tauri",
        "runtime_label": "Tauri (Rust + WebView)",
        "family": "hybrid-web",
        "ui_toolkit": "WebView (React / TypeScript)",
        "language": "Rust / TypeScript",
        "embedded_db": "SQLite (WAL)",
        "unit_test_runner": "cargo test / Vitest",
        "ui_test_runner": "tauri-driver (WebDriver)",
        "manifest": "src-tauri/Cargo.toml",
        "version_file": "src-tauri/Cargo.toml",
        "format": "toml",
        "field": "version",
        "src_ext": ".ts",
        "src_dir": "src",
        "ui_dir": "src/components",
        "modules_dir": "src-tauri/src",
        "test_pattern": "src-tauri/tests/{slug_snake}_test.rs",
    },
    {
        "ecosystem": "electron",
        "runtime_label": "Electron (Node.js + Chromium)",
        "family": "hybrid-web",
        "ui_toolkit": "Chromium (React / TypeScript)",
        "language": "TypeScript / Node.js",
        "embedded_db": "SQLite (better-sqlite3 WAL)",
        "unit_test_runner": "Vitest / Jest",
        "ui_test_runner": "Playwright (Electron)",
        "manifest": "package.json",
        "version_file": "package.json",
        "format": "json",
        "field": "version",
        "src_ext": ".ts",
        "src_dir": "src",
        "ui_dir": "src/renderer",
        "modules_dir": "src/main",
        "test_pattern": "tests/{slug}.spec.ts",
    },
    {
        "ecosystem": "wails",
        "runtime_label": "Wails (Go + WebView)",
        "family": "hybrid-web",
        "ui_toolkit": "WebView (React / TypeScript)",
        "language": "Go / TypeScript",
        "embedded_db": "SQLite (modernc.org/sqlite WAL)",
        "unit_test_runner": "go test",
        "ui_test_runner": "Playwright",
        "manifest": "wails.json",
        "version_file": "wails.json",
        "format": "json",
        "field": "version",
        "src_ext": ".go",
        "src_dir": ".",
        "ui_dir": "frontend/src",
        "modules_dir": "internal",
        "test_pattern": "internal/{slug_snake}_test.go",
    },
    {
        "ecosystem": "flutter-desktop",
        "runtime_label": "Flutter Desktop",
        "family": "flutter",
        "ui_toolkit": "Flutter (Material / Fluent / macOS)",
        "language": "Dart",
        "embedded_db": "SQLite (drift / sqflite_common_ffi)",
        "unit_test_runner": "flutter test",
        "ui_test_runner": "integration_test",
        "manifest": "pubspec.yaml",
        "version_file": "pubspec.yaml",
        "format": "yaml",
        "field": "version",
        "src_ext": ".dart",
        "src_dir": "lib",
        "ui_dir": "lib/ui",
        "modules_dir": "lib/modules",
        "test_pattern": "test/{slug_snake}_test.dart",
    },
    {
        "ecosystem": "swift-macos",
        "runtime_label": "SwiftUI / AppKit (macOS)",
        "family": "apple",
        "ui_toolkit": "SwiftUI / AppKit",
        "language": "Swift",
        "embedded_db": "SQLite (GRDB.swift) / SwiftData",
        "unit_test_runner": "XCTest / Swift Testing",
        "ui_test_runner": "XCUITest",
        "manifest": "Package.swift",
        "version_file": "Package.swift",
        "format": "regex",
        "field": "version",
        "src_ext": ".swift",
        "src_dir": "Sources",
        "ui_dir": "Sources/Views",
        "modules_dir": "Sources/Modules",
        "test_pattern": "Tests/{slug_pascal}Tests.swift",
    },
]

_PROFILE_MAP: Dict[str, Dict[str, str]] = {
    profile["ecosystem"]: profile for profile in ECOSYSTEM_PROFILES
}

IGNORED_SCAFFOLD_ENTRIES = {
    ".git",
    ".spec",
    "docs",
    "graphify-out",
    ".gitignore",
    ".graphifyignore",
    ".githooks",
    ".gemini",
    ".cursor",
    ".claude",
    ".windsurf",
    "CLAUDE.md",
    ".windsurfrules",
}

_SCAN_SKIP_DIRS = {
    ".git",
    ".spec",
    "docs",
    "graphify-out",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "dist",
    "build",
    "target",
    "bin",
    "obj",
    "out",
    "cmake-build-debug",
    "cmake-build-release",
    ".gradle",
    ".mvn",
    ".idea",
    ".vscode",
    ".vs",
    ".gemini",
    ".cursor",
    ".claude",
    ".windsurf",
    ".githooks",
}

_SOURCE_AND_UI_EXTS = {
    ".cs",
    ".fs",
    ".vb",
    ".xaml",
    ".axaml",
    ".py",
    ".kt",
    ".java",
    ".rs",
    ".slint",
    ".cpp",
    ".cc",
    ".cxx",
    ".c",
    ".h",
    ".hpp",
    ".qml",
    ".ui",
}

_MODULE_DIR_NAMES = {
    "modules",
    "domain",
    "features",
    "use_cases",
    "use-cases",
    "usecases",
    "entities",
    "repositories",
    "services",
    "application",
    "infrastructure",
    "models",
    "viewmodels",
    "presenters",
    "handlers",
    "commands",
    "queries",
    "ports",
    "adapters",
}


def get_ecosystem_profile(ecosystem_key: str) -> Dict[str, str]:
    """Retorna una copia del perfil para un ecosistema desktop nativo valido."""
    profile = _PROFILE_MAP.get(ecosystem_key)
    if profile is not None:
        return dict(profile)
    valid = ", ".join(p["ecosystem"] for p in ECOSYSTEM_PROFILES)
    raise ValueError(
        f"Ecosistema desconocido '{ecosystem_key}'. Opciones validas: {valid}"
    )


def _read_text_safe(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def _find_csproj_files(project_root: Path) -> List[Path]:
    root_files = sorted(project_root.glob("*.csproj"))
    if root_files:
        candidates = root_files
    else:
        candidates = []
        for item in project_root.rglob("*.csproj"):
            if any(part in _SCAN_SKIP_DIRS for part in item.parts):
                continue
            candidates.append(item)
        candidates.sort()

    # Priorizar proyectos de aplicacion sobre proyectos de test (*Test*.csproj)
    candidates.sort(key=lambda p: ("test" in p.stem.lower(), len(p.parts), p.name.lower()))
    return candidates


def _has_axaml_files(project_root: Path) -> bool:
    for item in project_root.rglob("*.axaml"):
        if not any(part in _SCAN_SKIP_DIRS for part in item.parts):
            return True
    return False


def _detect_dotnet_details(
    project_root: Path, csproj_files: List[Path], ecosystem_key: Optional[str]
) -> Tuple[str, Dict[str, str]]:
    texts: List[str] = []
    for f in csproj_files:
        texts.append(_read_text_safe(f))
    for prop_name in ("Directory.Packages.props", "Directory.Build.props", "packages.config"):
        prop_file = project_root / prop_name
        if prop_file.is_file():
            texts.append(_read_text_safe(prop_file))
    combined = "\n".join(texts).lower()

    if ecosystem_key:
        resolved = ecosystem_key
    elif "avalonia" in combined or _has_axaml_files(project_root):
        resolved = "avalonia"
    elif (
        "microsoft.windowsappsdk" in combined
        or "<usewinui>true</usewinui>" in combined
        or "microsoft.ui.xaml" in combined
    ):
        resolved = "winui3"
    elif "<usemaui>true</usemaui>" in combined or "microsoft.maui" in combined:
        resolved = "maui-desktop"
    else:
        resolved = "wpf"

    overrides: Dict[str, str] = {}
    if csproj_files:
        rel_manifest = csproj_files[0].relative_to(project_root).as_posix()
        overrides["manifest"] = rel_manifest
        overrides["version_file"] = rel_manifest

    if "sqlcipher" in combined:
        overrides["embedded_db"] = "SQLCipher"
    elif "duckdb" in combined:
        overrides["embedded_db"] = "DuckDB"
    elif "litedb" in combined:
        overrides["embedded_db"] = "LiteDB"
    elif "realm" in combined:
        overrides["embedded_db"] = "Realm"
    elif "sqlite" in combined:
        overrides["embedded_db"] = "SQLite (WAL)"

    if re.search(r'include=["\']nunit["\']', combined):
        overrides["unit_test_runner"] = "NUnit"
    elif re.search(r'include=["\']xunit["\']', combined):
        overrides["unit_test_runner"] = "xUnit"
    elif re.search(r'include=["\']mstest', combined):
        overrides["unit_test_runner"] = "MSTest"
    elif "nunit" in combined:
        overrides["unit_test_runner"] = "NUnit"
    elif "xunit" in combined:
        overrides["unit_test_runner"] = "xUnit"
    elif "mstest" in combined:
        overrides["unit_test_runner"] = "MSTest"

    if "avalonia.headless" in combined:
        overrides["ui_test_runner"] = "Avalonia.Headless"
    elif "flaui" in combined:
        overrides["ui_test_runner"] = "FlaUI"
    elif "appium" in combined:
        overrides["ui_test_runner"] = "Appium"

    return resolved, overrides


def _detect_python_details(
    project_root: Path, ecosystem_key: Optional[str]
) -> Tuple[str, Dict[str, str]]:
    pyproject = project_root / "pyproject.toml"
    setup_cfg = project_root / "setup.cfg"

    texts: List[str] = []
    if pyproject.is_file():
        texts.append(_read_text_safe(pyproject))
    if setup_cfg.is_file():
        texts.append(_read_text_safe(setup_cfg))
    for req_file in sorted(project_root.glob("requirements*.txt")):
        texts.append(_read_text_safe(req_file))
    combined = "\n".join(texts).lower()

    if ecosystem_key:
        resolved = ecosystem_key
    elif re.search(r"(?<![a-z0-9_-])flet(?![a-z0-9_-])", combined):
        resolved = "flet"
    elif "pyqt6" in combined:
        resolved = "pyqt6"
    else:
        resolved = "pyside6"

    overrides: Dict[str, str] = {}
    if pyproject.is_file():
        overrides["manifest"] = "pyproject.toml"
        overrides["version_file"] = "pyproject.toml"
        overrides["format"] = "toml"
    elif setup_cfg.is_file():
        overrides["manifest"] = "setup.cfg"
        overrides["version_file"] = "setup.cfg"
        overrides["format"] = "cfg"

    if "sqlcipher" in combined:
        overrides["embedded_db"] = "SQLCipher"
    elif "duckdb" in combined:
        overrides["embedded_db"] = "DuckDB"
    elif "tinydb" in combined:
        overrides["embedded_db"] = "TinyDB"
    elif any(k in combined for k in ("sqlite", "sqlalchemy", "sqlmodel", "peewee", "aiosqlite")):
        overrides["embedded_db"] = "SQLite (WAL)"

    if "pytest-qt" in combined:
        overrides["ui_test_runner"] = "pytest-qt"
        overrides["unit_test_runner"] = "pytest"
    elif "pytest" in combined:
        overrides["unit_test_runner"] = "pytest"

    return resolved, overrides


def _detect_jvm_details(
    project_root: Path, ecosystem_key: Optional[str]
) -> Tuple[str, Dict[str, str]]:
    gradle_kts = project_root / "build.gradle.kts"
    gradle_groovy = project_root / "build.gradle"
    pom_xml = project_root / "pom.xml"
    libs_toml = project_root / "gradle" / "libs.versions.toml"

    texts: List[str] = []
    for path in (gradle_kts, gradle_groovy, pom_xml, libs_toml):
        if path.is_file():
            texts.append(_read_text_safe(path))
    combined = "\n".join(texts).lower()

    if ecosystem_key:
        resolved = ecosystem_key
    elif any(
        k in combined
        for k in (
            "org.jetbrains.compose",
            "compose.desktop",
            "compose-multiplatform",
            "org.jetbrains.kotlin.plugin.compose",
        )
    ):
        resolved = "compose-desktop"
    elif any(k in combined for k in ("org.openjfx", "javafx", "javafx-controls", "javafx-fxml")):
        resolved = "javafx"
    elif gradle_kts.is_file() or (project_root / "src" / "main" / "kotlin").is_dir():
        resolved = "compose-desktop"
    else:
        resolved = "javafx"

    overrides: Dict[str, str] = {}
    if gradle_kts.is_file():
        overrides["manifest"] = "build.gradle.kts"
        overrides["version_file"] = "build.gradle.kts"
        overrides["format"] = "gradle"
    elif gradle_groovy.is_file():
        overrides["manifest"] = "build.gradle"
        overrides["version_file"] = "build.gradle"
        overrides["format"] = "gradle"
    elif pom_xml.is_file():
        overrides["manifest"] = "pom.xml"
        overrides["version_file"] = "pom.xml"
        overrides["format"] = "xml"

    if (
        resolved == "javafx"
        and (project_root / "src" / "main" / "kotlin").is_dir()
        and not (project_root / "src" / "main" / "java").is_dir()
    ):
        overrides["language"] = "Kotlin"
        overrides["src_ext"] = ".kt"
        overrides["src_dir"] = "src/main/kotlin"

    if "sqlcipher" in combined:
        overrides["embedded_db"] = "SQLCipher"
    elif "duckdb" in combined:
        overrides["embedded_db"] = "DuckDB"
    elif "realm" in combined:
        overrides["embedded_db"] = "Realm"
    elif any(k in combined for k in ("sqlite", "sqldelight", "exposed", "xerial")):
        overrides["embedded_db"] = "SQLite (WAL)"

    if "kotest" in combined:
        overrides["unit_test_runner"] = "Kotest"
    elif "testng" in combined:
        overrides["unit_test_runner"] = "TestNG"
    elif "junit" in combined:
        overrides["unit_test_runner"] = "JUnit 5"

    if "testfx" in combined:
        overrides["ui_test_runner"] = "TestFX"
    elif "compose" in combined and ("ui-test" in combined or "ui.test" in combined):
        overrides["ui_test_runner"] = "Compose UI Test"

    return resolved, overrides


def _detect_rust_details(project_root: Path) -> Dict[str, str]:
    cargo = project_root / "Cargo.toml"
    combined = _read_text_safe(cargo).lower() if cargo.is_file() else ""
    overrides: Dict[str, str] = {}

    if "slint" in combined:
        overrides["ui_toolkit"] = "Slint"
        overrides["ui_test_runner"] = "slint-testing"
    elif "iced" in combined:
        overrides["ui_toolkit"] = "Iced"
    elif "egui" in combined or "eframe" in combined:
        overrides["ui_toolkit"] = "egui"
    elif "gtk4" in combined or "relm4" in combined:
        overrides["ui_toolkit"] = "GTK4 (Rust)"
    elif "gpui" in combined:
        overrides["ui_toolkit"] = "GPUI"

    if "sqlcipher" in combined:
        overrides["embedded_db"] = "SQLCipher"
    elif "duckdb" in combined:
        overrides["embedded_db"] = "DuckDB"
    elif "redb" in combined:
        overrides["embedded_db"] = "redb (Embedded KV)"
    elif "sled" in combined:
        overrides["embedded_db"] = "sled (Embedded KV)"
    elif any(k in combined for k in ("rusqlite", "sqlx", "diesel", "sqlite")):
        overrides["embedded_db"] = "SQLite (WAL)"

    return overrides


def _detect_qt_cpp_details(project_root: Path) -> Dict[str, str]:
    texts: List[str] = []
    for fname in ("CMakeLists.txt", "vcpkg.json", "conanfile.txt", "conanfile.py"):
        fpath = project_root / fname
        if fpath.is_file():
            texts.append(_read_text_safe(fpath))
    combined = "\n".join(texts).lower()
    overrides: Dict[str, str] = {}

    if (
        "qt6::quick" in combined
        or "qtquick" in combined
        or re.search(r"\bcomponents\b[^)]*\bquick\b", combined, re.DOTALL)
    ):
        overrides["ui_toolkit"] = "Qt6 Quick (QML)"
    elif (
        "qt6::widgets" in combined
        or "qtwidgets" in combined
        or re.search(r"\bcomponents\b[^)]*\bwidgets\b", combined, re.DOTALL)
    ):
        overrides["ui_toolkit"] = "Qt6 Widgets"
    elif "qt5::" in combined or re.search(r"\bfind_package\s*\(\s*qt5\b", combined):
        overrides["ui_toolkit"] = "Qt5"

    if "sqlcipher" in combined:
        overrides["embedded_db"] = "SQLCipher"
    elif "duckdb" in combined:
        overrides["embedded_db"] = "DuckDB"
    elif (
        "sqlite" in combined
        or "qt6::sql" in combined
        or "qt::sql" in combined
        or re.search(r"\bcomponents\b[^)]*\bsql\b", combined, re.DOTALL)
    ):
        overrides["embedded_db"] = "SQLite (WAL)"

    has_qt_test = (
        "qt6::test" in combined
        or "qt::test" in combined
        or "qtest" in combined
        or bool(re.search(r"\bcomponents\b[^)]*\btest\b", combined, re.DOTALL))
    )
    if "catch2" in combined:
        overrides["unit_test_runner"] = "Catch2"
    elif "gtest" in combined or "googletest" in combined:
        overrides["unit_test_runner"] = "GoogleTest"
    elif has_qt_test:
        overrides["unit_test_runner"] = "Qt Test"

    if has_qt_test:
        overrides["ui_test_runner"] = "Qt Test"

    return overrides


def _detect_directories(project_root: Path, profile: Dict[str, str]) -> Tuple[str, str, str]:
    src_candidates: Tuple[str, ...] = (
        ("src/main/kotlin", "src/main/java", "src", "app")
        if profile["family"] == "jvm"
        else ("src", "app", "source")
    )
    src_dir = profile["src_dir"]
    for cand in src_candidates:
        if (project_root / cand).is_dir():
            src_dir = cand
            break

    ui_candidates_by_family: Dict[str, Tuple[str, ...]] = {
        "dotnet": ("src/Views", "Views", "src/UI", "UI", "Pages"),
        "python": ("src/ui", "ui", "src/views", "views"),
        "jvm": (
            "src/main/kotlin/ui",
            "src/main/java/ui",
            "src/main/resources/fxml",
            "src/main/resources",
        ),
        "rust-cpp": ("src/ui", "ui", "qml", "src/views"),
    }
    ui_dir = profile["ui_dir"]
    for cand in ui_candidates_by_family.get(profile["family"], ()):
        if (project_root / cand).is_dir():
            ui_dir = cand
            break

    modules_candidates: Tuple[str, ...] = (
        ("src/Modules", "Modules", "src/Domain", "Domain", "src/Features")
        if profile["family"] == "dotnet"
        else (
            "src/main/kotlin/modules",
            "src/main/java/modules",
            "src/modules",
            "modules",
            "src/domain",
            "src/features",
        )
    )
    modules_dir = profile["modules_dir"]
    for cand in modules_candidates:
        if (project_root / cand).is_dir():
            modules_dir = cand
            break

    return src_dir, ui_dir, modules_dir


def _detect_manifest_family_and_profile(
    project_root: Path, ecosystem_key: Optional[str]
) -> Tuple[str, Dict[str, str]]:
    csproj_files = _find_csproj_files(project_root)
    has_pyproject = (project_root / "pyproject.toml").is_file()
    has_setup_cfg = (project_root / "setup.cfg").is_file()
    has_gradle_kts = (project_root / "build.gradle.kts").is_file()
    has_gradle = (project_root / "build.gradle").is_file()
    has_pom = (project_root / "pom.xml").is_file()
    has_cargo = (project_root / "Cargo.toml").is_file()
    has_cmake = (project_root / "CMakeLists.txt").is_file()

    if ecosystem_key is not None:
        base = get_ecosystem_profile(ecosystem_key)
        family = base["family"]
        if family == "dotnet":
            _, overrides = _detect_dotnet_details(project_root, csproj_files, ecosystem_key)
            return ecosystem_key, overrides
        if family == "python":
            _, overrides = _detect_python_details(project_root, ecosystem_key)
            return ecosystem_key, overrides
        if family == "jvm":
            _, overrides = _detect_jvm_details(project_root, ecosystem_key)
            return ecosystem_key, overrides
        if ecosystem_key == "rust-native":
            return ecosystem_key, _detect_rust_details(project_root)
        if family in ("hybrid-web", "flutter", "apple"):
            return ecosystem_key, {}
        return ecosystem_key, _detect_qt_cpp_details(project_root)

    if csproj_files:
        return _detect_dotnet_details(project_root, csproj_files, None)
    if has_pyproject or has_setup_cfg:
        return _detect_python_details(project_root, None)
    if has_gradle_kts or has_gradle or has_pom:
        return _detect_jvm_details(project_root, None)
    if (
        (project_root / "src-tauri" / "Cargo.toml").is_file()
        or (project_root / "src-tauri" / "tauri.conf.json").is_file()
        or (project_root / "tauri.conf.json").is_file()
    ):
        return "tauri", {}
    if (project_root / "wails.json").is_file():
        return "wails", {}
    if (project_root / "package.json").is_file():
        pkg_text = _read_text_safe(project_root / "package.json").lower()
        if "@tauri-apps" in pkg_text:
            return "tauri", {}
        if "electron" in pkg_text:
            return "electron", {}
    if (project_root / "go.mod").is_file():
        gomod_text = _read_text_safe(project_root / "go.mod").lower()
        if "wails" in gomod_text:
            return "wails", {}
    if (project_root / "pubspec.yaml").is_file():
        return "flutter-desktop", {}
    if (project_root / "Package.swift").is_file():
        return "swift-macos", {}
    if has_cargo:
        return "rust-native", _detect_rust_details(project_root)
    if has_cmake:
        return "qt-cpp", _detect_qt_cpp_details(project_root)

    return "avalonia", {}


def build_profile_context(
    project_root: Path, ecosystem_key: Optional[str] = None
) -> Dict[str, Any]:
    """Construye el perfil tecnico nativo inspeccionando manifiestos y dependencias reales."""
    project_root = Path(project_root)
    if ecosystem_key is not None:
        # Valida la clave solicitada desde el inicio
        get_ecosystem_profile(ecosystem_key)

    resolved_key, overrides = _detect_manifest_family_and_profile(
        project_root, ecosystem_key
    )
    profile = get_ecosystem_profile(resolved_key)
    profile.update(overrides)

    src_dir, ui_dir, modules_dir = _detect_directories(project_root, profile)
    profile["src_dir"] = src_dir
    profile["ui_dir"] = ui_dir
    profile["modules_dir"] = modules_dir

    manifest_path = project_root / profile["manifest"]
    version_path = project_root / "VERSION"
    if not manifest_path.is_file() and version_path.is_file():
        profile["version_file"] = "VERSION"
        profile["format"] = "plain"

    return profile


def _is_test_file(low_name: str, rel_posix_low: str) -> bool:
    if rel_posix_low.startswith(("tests/", "test/", "__tests__/", "spec/")):
        return True
    if any(seg in rel_posix_low for seg in ("/tests/", "/test/", "/__tests__/", "/src/test/")):
        return True
    return bool(
        re.search(
            r"(^test_.*\.py$|_test\.py$|_tests?\.rs$|_tests?\.(cpp|cc|cxx)$"
            r"|tests?\.(cs|kt|java)$|spec\.(cs|kt|java)$)",
            low_name,
        )
    )


def _is_fresh_scaffold(project_root: Path) -> bool:
    """Determina si el repo nativo es un scaffold inicial (sin modulos ni tests propios, <=2 archivos fuente/UI)."""
    source_ui_files = 0

    for item in project_root.rglob("*"):
        if any(part in _SCAN_SKIP_DIRS for part in item.parts) or not item.is_file():
            continue

        rel_path = item.relative_to(project_root)
        rel_parts = rel_path.parts
        rel_low = rel_path.as_posix().lower()
        low_name = item.name.lower()

        if len(rel_parts) == 1 and (
            low_name == "setup.py"
            or ".config." in low_name
            or low_name.endswith(".sln")
            or low_name in ("directory.build.props", "directory.packages.props", "gradle.properties")
        ):
            continue

        if _is_test_file(low_name, rel_low):
            return False

        if item.suffix.lower() not in _SOURCE_AND_UI_EXTS:
            continue

        if low_name == "__init__.py" and item.stat().st_size == 0:
            continue

        dir_parts_low = [p.lower() for p in rel_parts[:-1]]
        if any(seg in _MODULE_DIR_NAMES for seg in dir_parts_low):
            return False

        if (
            len(rel_parts) >= 3
            and rel_parts[0].lower() in ("src", "app")
            and rel_parts[1].lower()
            not in ("main", "test", "app", "core", "ui", "views", "screens", "windows")
            and not any((project_root / rel_parts[0] / rel_parts[1]).glob("*.csproj"))
        ):
            return False

        source_ui_files += 1
        if source_ui_files > 2:
            return False

    return True


def _has_known_manifest(project_root: Path) -> bool:
    if _find_csproj_files(project_root):
        return True
    return any(
        (project_root / fname).is_file()
        for fname in (
            "pyproject.toml",
            "setup.cfg",
            "build.gradle.kts",
            "build.gradle",
            "pom.xml",
            "Cargo.toml",
            "CMakeLists.txt",
            "src-tauri/Cargo.toml",
            "src-tauri/tauri.conf.json",
            "tauri.conf.json",
            "package.json",
            "wails.json",
            "go.mod",
            "pubspec.yaml",
            "Package.swift",
        )
    )


def detect_desktop_ecosystem(project_root: Path) -> Dict[str, Any]:
    """Detecta modo Greenfield vs Brownfield e identifica el stack desktop nativo activo."""
    project_root = Path(project_root).resolve()

    if not project_root.exists():
        return {
            "mode": "greenfield",
            "project_state": "empty",
            "is_fresh_scaffold": False,
            "detected": None,
            "manifest_path": None,
            "version_path": None,
            "message": "Directorio vacio o nuevo proyecto. Modo Greenfield activado.",
        }

    existing_files = [
        f for f in project_root.iterdir() if f.name not in IGNORED_SCAFFOLD_ENTRIES
    ]
    if not existing_files:
        return {
            "mode": "greenfield",
            "project_state": "empty",
            "is_fresh_scaffold": False,
            "detected": None,
            "manifest_path": None,
            "version_path": None,
            "message": "Directorio vacio o nuevo proyecto. Modo Greenfield activado.",
        }

    if not _has_known_manifest(project_root):
        return {
            "mode": "brownfield",
            "project_state": "brownfield",
            "is_fresh_scaffold": False,
            "detected": None,
            "manifest_path": None,
            "version_path": None,
            "message": "Proyecto existente detectado (ecosistema desktop personalizado).",
        }

    profile = build_profile_context(project_root)
    manifest_path = project_root / profile["manifest"]
    version_path = project_root / profile["version_file"]
    fresh_scaffold = _is_fresh_scaffold(project_root)
    project_state = "scaffold" if fresh_scaffold else "brownfield"

    return {
        "mode": "brownfield",
        "project_state": project_state,
        "is_fresh_scaffold": fresh_scaffold,
        "detected": profile,
        "manifest_path": manifest_path,
        "version_path": version_path,
        "message": (
            f"Ecosistema detectado: {profile['runtime_label']} "
            f"({profile['ecosystem']} / {profile['language']} / {profile['ui_toolkit']})"
        ),
    }
