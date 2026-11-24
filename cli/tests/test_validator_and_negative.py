import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

CLI_DIR = Path(__file__).resolve().parent.parent
if str(CLI_DIR) not in sys.path:
    sys.path.insert(0, str(CLI_DIR))

from desktop_spec import __version__
from desktop_spec.common import (
    HARNESS_NAMES,
    SCHEME_LABELS,
    build_doc_context,
    read_config_settings,
    render_placeholders,
    slugify,
)
from desktop_spec.validator.schema_validator import (
    count_rolling_history_rows,
    export_w3c_design_tokens,
    extract_design_tokens_summary,
    extract_requirement_data,
    extract_use_case_data,
    extract_user_flow_data,
    load_json_schema,
    locate_framework_asset,
    parse_yaml_frontmatter,
    validate_against_schema,
    validate_w3c_tokens_dict,
)


class TestCommonAndConfig(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_constants_slugify_and_render_placeholders(self):
        self.assertEqual(HARNESS_NAMES, ("antigravity", "cursor", "claude", "windsurf"))
        self.assertEqual(
            SCHEME_LABELS,
            {
                "semver": "SemVer 2.0.0",
                "calver": "CalVer (YYYY.MM.MICRO)",
                "sequential": "Sequential Versioning",
            },
        )
        self.assertEqual(slugify("Creación de Catálogo Local!"), "creacion-de-catalogo-local")
        self.assertEqual(slugify("   ---   "), "feature")
        self.assertLessEqual(len(slugify("a" * 60)), 40)

        rendered = render_placeholders(
            "App {{PROJECT_NAME}} ({{ECOSYSTEM_NAME}})",
            {"PROJECT_NAME": "VaultDesk", "ECOSYSTEM_NAME": "avalonia"},
        )
        self.assertEqual(rendered, "App VaultDesk (avalonia)")

    def test_build_doc_context_generates_22_frozen_placeholders(self):
        profile = {
            "ecosystem": "pyside6",
            "family": "python",
            "ui_toolkit": "Qt for Python (PySide6)",
            "language": "Python",
            "embedded_db": "SQLite (WAL)",
            "unit_test_runner": "pytest",
            "ui_test_runner": "pytest-qt",
            "manifest": "pyproject.toml",
            "version_file": "pyproject.toml",
            "src_dir": "src",
            "ui_dir": "src/ui",
            "modules_dir": "src/modules",
            "test_pattern": "tests/{module}/test_{slug}.py",
            "runtime_label": "PySide6 (Qt6)",
        }
        expected_keys = {
            "PROJECT_NAME",
            "ECOSYSTEM_NAME",
            "ECOSYSTEM_FAMILY",
            "UI_TOOLKIT",
            "LANGUAGE_NAME",
            "EMBEDDED_DB",
            "UNIT_TEST_RUNNER",
            "UI_TEST_RUNNER",
            "MANIFEST_FILE",
            "SRC_DIR",
            "UI_DIR",
            "MODULES_DIR",
            "TEST_PATTERN",
            "VERSIONING_SCHEME",
            "VERSIONING_SCHEME_LABEL",
            "CURRENT_VERSION",
            "MILESTONE_VERSION",
            "TODAY",
            "RUNTIME_LABEL",
            "HARNESS_INTERVIEW_TRIGGER",
            "HARNESS_QUESTION_STRATEGY",
            "FRAMEWORK_VERSION",
        }
        self.assertEqual(len(expected_keys), 22)

        ctx_agy = build_doc_context(
            "NoteVault", profile, "v0.3.0", "v0.4.0", "semver", "2026-11-23", harness="antigravity"
        )
        self.assertEqual(set(ctx_agy.keys()), expected_keys)
        self.assertEqual(ctx_agy["CURRENT_VERSION"], "0.3.0")
        self.assertEqual(ctx_agy["HARNESS_INTERVIEW_TRIGGER"], "/grill-me")
        self.assertEqual(ctx_agy["FRAMEWORK_VERSION"], __version__)

        ctx_claude = build_doc_context(
            "NoteVault", profile, "0.3.0", "v0.4.0", "calver", "2026-11-23", harness="claude"
        )
        self.assertEqual(ctx_claude["HARNESS_INTERVIEW_TRIGGER"], "/desk-grill")
        self.assertIn("AskUserQuestion", ctx_claude["HARNESS_QUESTION_STRATEGY"])
        self.assertEqual(ctx_claude["VERSIONING_SCHEME_LABEL"], "CalVer (YYYY.MM.MICRO)")

        ctx_all = build_doc_context(
            "NoteVault", profile, "0.3.0", "v0.4.0", "sequential", "2026-11-23", harness="all"
        )
        self.assertEqual(ctx_all["HARNESS_INTERVIEW_TRIGGER"], "/grill-me / /desk-grill")

    def test_read_config_settings_parses_desktop_config_yaml(self):
        spec_dir = self.tmp / ".spec"
        spec_dir.mkdir(parents=True)
        (spec_dir / "config.yaml").write_text(
            """framework: desktop-spec
version: "0.1.0"
project_name: "StudioCAD"

ecosystem:
  name: "avalonia"
  family: "dotnet"
  ui_toolkit: "Avalonia UI"
  language: "C#"
  embedded_db: "SQLite (WAL)"
  unit_test_runner: "xUnit"
  ui_test_runner: "Avalonia.Headless"
  manifest_file: "StudioCAD.csproj"
  src_dir: "src"
  ui_dir: "src/Shell/Views"
  modules_dir: "src/Modules"
  test_pattern: "tests/{module}/{slug}Tests.cs"

versioning_scheme: "semver"
current_version: "1.2.0"
current_milestone: "v1.3.0"

version_file:
  path: "src/StudioCAD.csproj"
  format: "xml"
  field: "Version"

modules:
  - core
  - catalog
  - export

harnesses:
  - antigravity
  - claude

paths:
  user_flows_docs: "docs/functional/user-flows"
  use_cases_docs: "docs/functional/use-cases"
  design_docs: "docs/design"
  technical_docs: "docs/technical"
  backlog: "docs/backlog"
  templates: ".spec/templates"
""",
            encoding="utf-8",
        )
        cfg = read_config_settings(self.tmp)
        self.assertEqual(cfg["ecosystem"], "avalonia")
        self.assertEqual(cfg["ecosystem_family"], "dotnet")
        self.assertEqual(cfg["ui_toolkit"], "Avalonia UI")
        self.assertEqual(cfg["language"], "C#")
        self.assertEqual(cfg["embedded_db"], "SQLite (WAL)")
        self.assertEqual(cfg["unit_test_runner"], "xUnit")
        self.assertEqual(cfg["ui_test_runner"], "Avalonia.Headless")
        self.assertEqual(cfg["manifest_file"], "StudioCAD.csproj")
        self.assertEqual(cfg["manifest_path"], "src/StudioCAD.csproj")
        self.assertEqual(cfg["manifest_format"], "xml")
        self.assertEqual(cfg["current_version"], "1.2.0")
        self.assertEqual(cfg["current_milestone"], "v1.3.0")
        self.assertEqual(cfg["modules"], ["core", "catalog", "export"])
        self.assertEqual(cfg["harnesses"], ["antigravity", "claude"])
        self.assertEqual(cfg["paths"]["technical_docs"], "docs/technical")
        self.assertEqual(cfg["src_ext"], ".cs")


class TestValidatorAndExtractors(unittest.TestCase):
    def test_locate_and_load_all_9_real_schemas(self):
        schemas_dir = locate_framework_asset("schemas")
        self.assertIsNotNone(schemas_dir)
        schema_paths = [
            "requirement.schema.json",
            "use-case.schema.json",
            "user-flow.schema.json",
            "design/tokens-and-themes.schema.json",
            "technical/tech-stack.schema.json",
            "technical/modular-architecture.schema.json",
            "technical/windowing-and-os-contracts.schema.json",
            "technical/local-persistence.schema.json",
            "technical/packaging-and-release.schema.json",
        ]
        for rel in schema_paths:
            loaded = load_json_schema(rel)
            self.assertIsNotNone(loaded, f"Fallo al cargar esquema {rel}")
            self.assertEqual(loaded.get("$schema"), "http://json-schema.org/draft-07/schema#")

    def test_parse_yaml_frontmatter_nested_dicts_lists_and_comments(self):
        sample = """---
id: UF-CORE-001
title: "Exportar proyecto local"
fsm_required: true
tags: [desktop, native]
window_geometry:
  min_width_px: 800
  min_height_px: 600
  resizable: false
accessibility:
  focus_management: "Foco en input principal"
  os_accessibility_roles: "AutomationProperties.Name en controles"
  keyboard_navigation: "Tab y Escape soportados"
theme_colors:
  - "#0F52BA" # Color primario
  - null
---
# Cuerpo del documento
"""
        fm, body, has_fm = parse_yaml_frontmatter(sample)
        self.assertTrue(has_fm)
        self.assertEqual(fm["id"], "UF-CORE-001")
        self.assertIs(fm["fsm_required"], True)
        self.assertEqual(fm["tags"], ["desktop", "native"])
        self.assertEqual(
            fm["window_geometry"],
            {"min_width_px": 800, "min_height_px": 600, "resizable": False},
        )
        self.assertEqual(fm["accessibility"]["focus_management"], "Foco en input principal")
        self.assertEqual(fm["theme_colors"], ["#0F52BA", None])
        self.assertIn("# Cuerpo del documento", body)

    def test_validate_type_list_with_null_on_tokens_and_persistence_schemas(self):
        tokens_schema = load_json_schema("design/tokens-and-themes.schema.json")
        self.assertIsNotNone(tokens_schema)

        valid_tokens = {
            "artifact_type": "design-tokens",
            "theme_modes": ["light", "dark", "system", "high-contrast"],
            "density_modes": ["compact", "standard", "comfortable"],
            "semantic_colors": [
                {
                    "token": "bg-base",
                    "light_hex": "#F5F6F8",
                    "dark_hex": "#111317",
                    "high_contrast_hex": None,
                    "role": "Fondo base de la ventana",
                },
                {
                    "token": "primary",
                    "light_hex": "#0F52BA",
                    "dark_hex": "#4C8DFF",
                    "high_contrast_hex": "#FFFF00",
                    "role": "Accion primaria",
                },
            ],
            "typography": {
                "display_font": "Segoe UI Variable Display",
                "ui_font": "Segoe UI Variable Text",
                "mono_font": "JetBrains Mono",
            },
        }
        self.assertEqual(validate_against_schema(valid_tokens, tokens_schema), [])

        bad_hc = json.loads(json.dumps(valid_tokens))
        bad_hc["semantic_colors"][0]["high_contrast_hex"] = "not-a-hex"
        errs = validate_against_schema(bad_hc, tokens_schema)
        self.assertTrue(any("high_contrast_hex" in e for e in errs))

        bad_light_null = json.loads(json.dumps(valid_tokens))
        bad_light_null["semantic_colors"][0]["light_hex"] = None
        errs_light = validate_against_schema(bad_light_null, tokens_schema)
        self.assertTrue(errs_light)

        # local-persistence.schema.json columns[].default usa type ["string", "null"]
        lp_schema = load_json_schema("technical/local-persistence.schema.json")
        self.assertIsNotNone(lp_schema)
        valid_lp = {
            "artifact_type": "local-persistence",
            "storage_engine": "sqlite-wal",
            "os_data_paths": {
                "data_dir_policy": "%APPDATA%/StudioCAD/data",
                "cache_dir_policy": "%LOCALAPPDATA%/StudioCAD/cache",
                "logs_dir_policy": "%LOCALAPPDATA%/StudioCAD/logs",
            },
            "er_diagram_mermaid": "erDiagram\n  PROJECTS ||--o{ ITEMS : contains",
            "tables": [
                {
                    "name": "projects",
                    "description": "Catalogo de proyectos locales",
                    "columns": [
                        {
                            "name": "id",
                            "type": "TEXT",
                            "nullable": False,
                            "default": None,
                            "key": "PK",
                        },
                        {
                            "name": "status",
                            "type": "TEXT",
                            "nullable": False,
                            "default": "'ACTIVE'",
                            "key": "NONE",
                        },
                    ],
                }
            ],
            "project_file_formats": [
                {
                    "extension": ".scadproj",
                    "format": "sqlite-container",
                    "version_field": "schema_version",
                    "atomic_write": True,
                }
            ],
            "migration_strategy": {
                "tool": "embedded-sql-migrator",
                "run_trigger": "on-startup",
                "pre_migration_backup": True,
                "schema_version_check": "PRAGMA user_version",
                "recovery_policy": "Restaurar snapshot previo antes de abrir UI",
            },
        }
        self.assertEqual(validate_against_schema(valid_lp, lp_schema), [])

        bad_lp = json.loads(json.dumps(valid_lp))
        bad_lp["tables"][0]["columns"][0]["default"] = 12345
        errs_lp = validate_against_schema(bad_lp, lp_schema)
        self.assertTrue(any("default" in e for e in errs_lp))

        # Validacion directa de null vs no-null sin disparar pattern/minLength
        nullable_str_schema = {"type": ["string", "null"], "pattern": "^#[0-9A-Fa-f]{6}$", "minLength": 7}
        self.assertEqual(validate_against_schema(None, nullable_str_schema), [])
        self.assertTrue(validate_against_schema("bad", nullable_str_schema))
        self.assertTrue(validate_against_schema(None, {"type": "string", "minLength": 2}))

    def test_validate_technical_schemas_positive_and_negative(self):
        tech_schema = load_json_schema("technical/tech-stack.schema.json")
        mod_schema = load_json_schema("technical/modular-architecture.schema.json")
        win_schema = load_json_schema("technical/windowing-and-os-contracts.schema.json")
        pkg_schema = load_json_schema("technical/packaging-and-release.schema.json")

        valid_tech = {
            "artifact_type": "tech-stack",
            "ecosystem": "avalonia",
            "core": {
                "language_runtime": ".NET 8 / C# 12",
                "ui_toolkit": "Avalonia UI 11",
                "architecture_pattern": "Modular Monolith + MVVM",
                "embedded_db": "SQLite (WAL)",
                "keyring_provider": "OS Credential Manager",
                "unit_test_framework": "xUnit",
                "ui_test_framework": "Avalonia.Headless",
            },
            "performance_budgets": {
                "cold_startup_ms": 1200,
                "idle_ram_mb": 140,
                "ui_frame_budget_ms": 16,
                "installer_max_mb": 85,
            },
            "security_policies": {
                "local_secrets": "Resguardo en OS Keyring nativo",
                "path_traversal": "Canonizacion estricta de rutas locales",
                "deserialization": "System.Text.Json tipado sin BinaryFormatter",
                "binary_hardening": "Firma Authenticode y auditoria NuGet",
            },
        }
        self.assertEqual(validate_against_schema(valid_tech, tech_schema), [])
        self.assertTrue(validate_against_schema({**valid_tech, "ecosystem": "electron-web"}, tech_schema))

        valid_mod = {
            "artifact_type": "modular-architecture",
            "architecture_style": "modular-monolith-clean",
            "class_diagram_mermaid": "classDiagram\n  class CoreFacade",
            "sequence_diagram_mermaid": "sequenceDiagram\n  UI->>Core: Run",
            "modules": [
                {
                    "id": "MOD-CORE-001",
                    "name": "Core",
                    "responsibility": "Gestion de espacio de trabajo local",
                    "public_facade": "ICoreModuleFacade",
                    "owned_persistence_scope": "projects, settings",
                    "allowed_dependencies": [],
                }
            ],
            "dependency_rules": {
                "acyclic_modules": True,
                "forbid_cross_module_internals": True,
                "forbid_ui_direct_persistence": True,
                "architecture_test_tool": "NetArchTest",
            },
            "internal_event_bus": {
                "mechanism": "InMemoryMediator",
                "delivery_guarantee": "at-least-once-inproc",
                "async_dispatch": True,
            },
            "concurrency_model": {
                "ui_thread_policy": "Dispatcher exclusivo de UI",
                "background_worker_mechanism": "Task.Run + CancellationToken",
                "cancellation_support": True,
            },
        }
        self.assertEqual(validate_against_schema(valid_mod, mod_schema), [])
        bad_mod = json.loads(json.dumps(valid_mod))
        bad_mod["modules"][0]["id"] = "INVALID"
        self.assertTrue(validate_against_schema(bad_mod, mod_schema))

        valid_win = {
            "artifact_type": "windowing-and-os-contracts",
            "window_topology": "single-window",
            "single_instance_policy": {
                "enabled": True,
                "secondary_launch_behavior": "Focus existing window",
            },
            "windows": [
                {
                    "id": "WIN-MAIN-001",
                    "name": "MainWindow",
                    "user_flow_id": "UF-CORE-001",
                    "min_width_px": 1024,
                    "min_height_px": 720,
                    "unsaved_changes_guard": True,
                    "close_behavior": "Prompt if dirty",
                }
            ],
            "global_shortcuts": [
                {
                    "action": "SaveProject",
                    "shortcut_win_linux": "Ctrl+S",
                    "shortcut_macos": "Cmd+S",
                    "scope": "GlobalWindow",
                }
            ],
            "os_integrations": {
                "file_dialogs": "Native Open/Save",
                "drag_and_drop": "File drop",
                "file_associations": ".dspecproj",
                "deep_links": "N/A",
                "cli_arguments": "--open <path>",
                "system_tray": "N/A",
                "os_permissions": "User documents",
            },
        }
        self.assertEqual(validate_against_schema(valid_win, win_schema), [])
        bad_win = json.loads(json.dumps(valid_win))
        bad_win["windows"][0]["min_width_px"] = "1024px"
        self.assertTrue(validate_against_schema(bad_win, win_schema))

        valid_pkg = {
            "artifact_type": "packaging-and-release",
            "target_platforms": ["windows", "macos", "linux"],
            "branching_model": "github-flow",
            "pipeline_diagram_mermaid": "flowchart LR\n  Build --> Sign",
            "packaging_formats": {
                "windows": "MSIX / WiX",
                "macos": "DMG notarizado",
                "linux": "AppImage",
            },
            "signing_and_notarization": {
                "windows_authenticode": "signtool SHA256",
                "secrets_source": "github_secret",
            },
            "auto_update": {
                "strategy": "Velopack",
                "channels": ["stable", "beta"],
                "checksum_verification": "SHA-256",
            },
            "build_env_vars": [
                {
                    "name": "WIN_CERT_PFX",
                    "description": "Certificado Authenticode",
                    "is_secret": True,
                    "ci_source": "github_secret",
                    "environments": ["ci", "stable"],
                }
            ],
        }
        self.assertEqual(validate_against_schema(valid_pkg, pkg_schema), [])
        self.assertTrue(validate_against_schema({**valid_pkg, "target_platforms": ["ios"]}, pkg_schema))

    def test_extract_use_case_positive_and_negative(self):
        schema = load_json_schema("use-case.schema.json")
        self.assertIsNotNone(schema)

        templates_dir = locate_framework_asset("templates")
        uc_tpl_path = templates_dir / ".spec" / "templates" / "_template_use_case.md"
        if uc_tpl_path.exists():
            raw_uc = (
                uc_tpl_path.read_text(encoding="utf-8")
                .replace("UC-[MODULO]-[NUM]", "UC-CATALOG-001")
                .replace("[Nombre del Caso de Uso de Dominio]", "Actualizar saldo de inventario")
                .replace('"[core | catalog | ledger | sync]"', '"catalog"')
                .replace('"[Operador Local | Worker en Segundo Plano | Modulo Invocador]"', '"Operador Local"')
                .replace(
                    '"[Comando de aplicacion o evento interno que inicia el caso de uso]"',
                    '"UpdateInventoryBalanceCommand"',
                )
            )
            uc_data, has_fm = extract_use_case_data(raw_uc)
            self.assertTrue(has_fm)
            self.assertEqual(validate_against_schema(uc_data, schema), [])
            self.assertEqual(uc_data["id"], "UC-CATALOG-001")
            self.assertEqual(uc_data["module"], "catalog")
            self.assertGreaterEqual(len(uc_data["inputs"]), 2)
            self.assertGreaterEqual(len(uc_data["outputs"]), 2)
            self.assertGreaterEqual(len(uc_data["business_rules"]), 2)
            self.assertIn("ocl_contract", uc_data["business_rules"][0])
            self.assertIn("local_database", uc_data["side_effects"])

        bad_uc_md = """---
id: UC-bad-1
title: Corto
module: c
actor: A
status: Desconocido
trigger: go
---
# UC-bad-1: Corto
"""
        bad_data, _ = extract_use_case_data(bad_uc_md)
        errs = validate_against_schema(bad_data, schema)
        self.assertGreaterEqual(len(errs), 4)

    def test_extract_user_flow_positive_and_negative(self):
        schema = load_json_schema("user-flow.schema.json")
        self.assertIsNotNone(schema)

        templates_dir = locate_framework_asset("templates")
        uf_tpl_path = templates_dir / ".spec" / "templates" / "_template_user_flow.md"
        if uf_tpl_path.exists():
            raw_uf = (
                uf_tpl_path.read_text(encoding="utf-8")
                .replace("UF-[MODULO]-[NUM]", "UF-CATALOG-001")
                .replace("UC-[MODULO]-[NUM]", "UC-CATALOG-001")
                .replace("[Nombre del Flujo de Interaccion Nativo]", "Editar articulo en catalogo")
                .replace('"[core | catalog | shell | settings]"', '"catalog"')
                .replace('"[Operador Local | Usuario]"', '"Operador Local"')
                .replace('"[MainWindow | EditorDialog]"', '"EditorDialog"')
                .replace('"[Menu Archivo -> Accion o atajo Ctrl+N / Cmd+N]"', '"Ctrl+E / Cmd+E"')
            )
            uf_data, has_fm = extract_user_flow_data(raw_uf)
            self.assertTrue(has_fm)
            self.assertEqual(validate_against_schema(uf_data, schema), [])
            self.assertEqual(uf_data["id"], "UF-CATALOG-001")
            self.assertEqual(uf_data["invokes_use_case"], "UC-CATALOG-001")
            self.assertEqual(
                uf_data["window_geometry"],
                {"min_width_px": 640, "min_height_px": 480, "resizable": True},
            )
            self.assertGreaterEqual(len(uf_data["user_inputs"]), 2)
            self.assertGreaterEqual(len(uf_data["visual_outputs"]), 2)
            self.assertGreaterEqual(len(uf_data["ui_states"]), 3)
            self.assertIn("AutomationProperties", uf_data["accessibility"]["os_accessibility_roles"])

        # Flujo puramente presentacional con invokes_use_case: N/A y accessibility en frontmatter
        uf_presentational = """---
id: UF-SHELL-002
title: Cambiar tema claro y oscuro
module: shell
actor: Usuario
window_target: MainWindow
entry_trigger: Menu Ver -> Tema
status: Activo
invokes_use_case: N/A
shortcut: "Ctrl+T / Cmd+T"
fsm_required: false
window_geometry:
  min_width_px: 1024
  min_height_px: 720
  resizable: true
accessibility:
  focus_management: "Conservar foco en el control activo tras alternar tema"
  os_accessibility_roles: "MenuItem con ToggleState nativo"
  keyboard_navigation: "Acceso directo Ctrl+T / Cmd+T y navegacion con flechas"
---
# UF-SHELL-002: Cambiar tema claro y oscuro

```mermaid
flowchart LR
    Idle --> ToggleTheme --> Idle
```

## 4. Matriz de Estados de Interfaz y Casos Borde

| Estado UI | Condicion de Disparo | Que ve el usuario | Accion / Recuperacion |
| :--- | :--- | :--- | :--- |
| **Aplicado** | Usuario selecciona tema | Recursos nativos actualizados al instante | Persistir preferencia local |
"""
        pres_data, _ = extract_user_flow_data(uf_presentational)
        self.assertEqual(validate_against_schema(pres_data, schema), [])
        self.assertEqual(pres_data["invokes_use_case"], "N/A")

        # Negativo: invokes_use_case invalido, sin a11y ni window_geometry valida
        bad_uf_md = """---
id: UF-BAD
title: Bad
module: a
actor: b
window_target: W
entry_trigger: E
invokes_use_case: INVALID-REF
window_geometry:
  min_width_px: "ancho"
  min_height_px: 400
  resizable: true
---
# UF-BAD: Bad
"""
        bad_uf, _ = extract_user_flow_data(bad_uf_md)
        errs = validate_against_schema(bad_uf, schema)
        self.assertTrue(any("invokes_use_case" in e for e in errs))
        self.assertTrue(any("min_width_px" in e for e in errs))
        self.assertTrue(any("accessibility" in e for e in errs))

    def test_extract_requirement_data_positive_and_negative(self):
        schema = load_json_schema("requirement.schema.json")
        self.assertIsNotNone(schema)

        req_full_module = """
### [REQ-DESK-CATALOG-001] Exportar catalogo a SQLite compacto
- **Prioridad:** P1
- **Tipo:** Feature (MINOR)
- **Alcance (Scope):** full-module
- **Versión Objetivo:** `v0.3.0`
- **Flujos UX (`UF-*`):** `docs/functional/user-flows/UF-CATALOG-001.md`
- **Casos de Uso (`UC-*`):** `docs/functional/use-cases/UC-CATALOG-001.md`
- **Referencias Técnicas:** `docs/technical/modular-architecture.md`, `docs/technical/local-persistence.md`

#### Fronteras y Artefactos:
- **Módulos Afectados:** `catalog`, `shell-ui`
- **Artefactos a Modificar / Crear:**
  - `src/Modules/Catalog/ExportUseCase.cs` [NEW]
  - `src/Shell/Views/ExportDialog.axaml` [MODIFY]
- **Restricciones:**
  - Prohibido acceder a SQLite desde ViewModels.

#### Criterios de Aceptación:
- [ ] Exportacion atomica con snapshot previo.
- [x] Prueba headless de dialogo completada.
"""
        parsed_full = extract_requirement_data(req_full_module)
        self.assertEqual(validate_against_schema(parsed_full, schema), [])
        self.assertEqual(parsed_full["track"], "FULL")
        self.assertEqual(parsed_full["scope"], "full-module")
        self.assertEqual(
            parsed_full["references"]["user_flows"],
            ["docs/functional/user-flows/UF-CATALOG-001.md"],
        )
        self.assertEqual(
            parsed_full["boundaries"]["affected_modules"], ["catalog", "shell-ui"]
        )
        self.assertEqual(len(parsed_full["acceptance_criteria"]), 2)

        # domain-only / PATCH con N/A en Flujos UX y Casos de Uso
        req_patch = """
### [REQ-DESK-CORE-002] Corregir cierre de WAL en worker local
- **Prioridad:** P2
- **Tipo:** Hotfix / Fix (PATCH - Fast-Track)
- **Alcance (Scope):** domain-only
- **Versión Objetivo:** `v0.3.1`
- **Flujos UX (`UF-*`):** N/A (domain-only)
- **Casos de Uso (`UC-*`):** N/A (PATCH / Fast-Track)
- **Referencias Técnicas:** `docs/technical/local-persistence.md`

#### Fronteras y Artefactos:
- **Módulos Afectados:** `core`
- **Artefactos a Modificar / Crear:**
  - `src/Modules/Core/SqliteWalCheckpoint.cs` [MODIFY]
- **Restricciones:**
  - Sin cambios en esquemas ni UI.

#### Criterios de Aceptación:
- [ ] Test de regresion en verde.
"""
        parsed_patch = extract_requirement_data(req_patch)
        self.assertEqual(validate_against_schema(parsed_patch, schema), [])
        self.assertEqual(parsed_patch["track"], "FAST_TRACK")
        self.assertEqual(parsed_patch["references"]["user_flows"], [])
        self.assertEqual(parsed_patch["references"]["use_cases"], [])

        # Negativo: prefijo REQ-UI no permitido en desktop-spec + scope invalido + action invalida
        bad_req = """
### [REQ-UI-CORE-001] Requerimiento web mal etiquetado
- **Prioridad:** P9
- **Tipo:** Feature (MINOR)
- **Alcance (Scope):** web-ssr
- **Versión Objetivo:** ``
- **Flujos UX (`UF-*`):** N/A
- **Casos de Uso (`UC-*`):** N/A
- **Referencias Técnicas:** N/A

#### Fronteras y Artefactos:
- **Módulos Afectados:** N/A
- **Artefactos a Modificar / Crear:**
  - `src/App.tsx` [NEW]
- **Restricciones:**
  - Ninguna

#### Criterios de Aceptación:
- [ ] Pendiente
"""
        parsed_bad = extract_requirement_data(bad_req)
        errs = validate_against_schema(parsed_bad, schema)
        self.assertTrue(any("id" in e for e in errs))
        self.assertTrue(any("priority" in e for e in errs))
        self.assertTrue(any("scope" in e for e in errs))

    def test_design_tokens_4_and_5_cols_and_w3c_dtcg_export_validation(self):
        schema = load_json_schema("design/tokens-and-themes.schema.json")
        self.assertIsNotNone(schema)

        templates_dir = locate_framework_asset("templates")
        tok_path = templates_dir / ".spec" / "docs" / "design" / "tokens-and-themes.md"
        if tok_path.exists():
            raw_tok = tok_path.read_text(encoding="utf-8")
            summary = extract_design_tokens_summary(raw_tok)
            self.assertTrue(summary["has_fm"])
            self.assertEqual(validate_against_schema(summary, schema), [])
            self.assertGreaterEqual(len(summary["semantic_colors"]), 5)
            self.assertIn("high_contrast_hex", summary["semantic_colors"][0])

            dtcg = export_w3c_design_tokens(raw_tok)
            self.assertEqual(validate_w3c_tokens_dict(dtcg), [])
            first_color = next(iter(dtcg["color"].values()))
            self.assertIn("light", first_color["$extensions"]["mode"])
            self.assertIn("dark", first_color["$extensions"]["mode"])
            self.assertIn("high_contrast", first_color["$extensions"]["mode"])
            self.assertIn("display", dtcg["typography"]["fontFamily"])
            self.assertIn("ui", dtcg["typography"]["fontFamily"])
            self.assertIn("mono", dtcg["typography"]["fontFamily"])

        # Tabla de 4 columnas (sin high_contrast_hex) + 5 columnas con N/A
        md_4cols = """---
artifact_type: design-tokens
theme_modes: [light, dark]
density_modes: [compact, standard]
---
## 1. Colores Semanticos

| Token | Modo Claro | Modo Oscuro | Rol de Uso |
| :--- | :--- | :--- | :--- |
| `bg-base` | `#F5F6F8` | `#111317` | Fondo base |

## 2. Tipografia, Espaciado, Radios y Densidad
- **Display:** "Inter", sans-serif
- **UI:** "Inter", sans-serif
- **Monospace:** "JetBrains Mono", monospace
"""
        sum_4 = extract_design_tokens_summary(md_4cols)
        self.assertEqual(validate_against_schema(sum_4, schema), [])
        self.assertNotIn("high_contrast_hex", sum_4["semantic_colors"][0])
        dtcg_4 = export_w3c_design_tokens(md_4cols)
        self.assertEqual(validate_w3c_tokens_dict(dtcg_4), [])
        self.assertNotIn(
            "high_contrast", dtcg_4["color"]["bg-base"]["$extensions"]["mode"]
        )

        # Tabla de 5 columnas con high_contrast N/A -> None -> pasa schema y omite high_contrast en DTCG
        md_5cols_na = """---
artifact_type: design-tokens
theme_modes: [light, dark, system]
density_modes: [standard]
---
## 1. Colores Semanticos

| Token | Modo Claro | Modo Oscuro | Alto Contraste | Rol de Uso |
| :--- | :--- | :--- | :--- | :--- |
| `surface` | `#FFFFFF` | `#1A1D23` | `N/A` | Superficie principal |

## 2. Tipografia, Espaciado, Radios y Densidad
- **Display:** "Inter", sans-serif
- **UI:** "Inter", sans-serif
- **Monospace:** "JetBrains Mono", monospace
"""
        sum_5_na = extract_design_tokens_summary(md_5cols_na)
        self.assertIsNone(sum_5_na["semantic_colors"][0]["high_contrast_hex"])
        self.assertEqual(validate_against_schema(sum_5_na, schema), [])
        dtcg_5_na = export_w3c_design_tokens(md_5cols_na)
        self.assertEqual(validate_w3c_tokens_dict(dtcg_5_na), [])
        self.assertNotIn(
            "high_contrast", dtcg_5_na["color"]["surface"]["$extensions"]["mode"]
        )

        # Negativos W3C DTCG
        self.assertTrue(validate_w3c_tokens_dict({}))
        self.assertTrue(
            validate_w3c_tokens_dict(
                {"color": {"primary": {"$type": "color", "$value": "red"}}}
            )
        )
        self.assertTrue(
            validate_w3c_tokens_dict(
                {
                    "color": {
                        "primary": {
                            "$type": "color",
                            "$value": "#0F52BA",
                            "$extensions": {"mode": {"high_contrast": "invalid"}},
                        }
                    }
                }
            )
        )
        self.assertTrue(
            validate_w3c_tokens_dict(
                {
                    "color": {
                        "primary": {
                            "$type": "color",
                            "$value": "#0F52BA",
                            "nested": {"$value": "#000000"},
                        }
                    }
                }
            )
        )

    def test_rolling_history_rows_count(self):
        sample = """
## Historial de Revisiones (Ultimos Cambios)

| Version | Fecha | Requerimiento | Resumen del Cambio |
| :--- | :--- | :--- | :--- |
| `v0.1.0` | 2026-11-01 | `REQ-DESK-CORE-001` | Uno |
| `v0.2.0` | 2026-11-02 | `REQ-DESK-CORE-002` | Dos |
| `v0.3.0` | 2026-11-03 | `REQ-DESK-CORE-003` | Tres |
| `v0.4.0` | 2026-11-04 | `REQ-DESK-CORE-004` | Cuatro |

> *Nota: Esta tabla mantiene una ventana deslizante.*
"""
        self.assertEqual(count_rolling_history_rows(sample), 4)
        self.assertEqual(count_rolling_history_rows("# Sin historial"), 0)


if __name__ == "__main__":
    unittest.main()
