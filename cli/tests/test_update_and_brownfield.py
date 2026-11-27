import json
import sys
import tempfile
import types
import unittest
from pathlib import Path

CLI_DIR = Path(__file__).resolve().parent.parent
if str(CLI_DIR) not in sys.path:
    sys.path.insert(0, str(CLI_DIR))

# Permite ejecutar pruebas aisladas de W3-A si check_cmd.py de W3-B aun no existe en disco
try:
    import desktop_spec.commands.check_cmd  # noqa: F401
except ImportError:
    _stub = types.ModuleType("desktop_spec.commands.check_cmd")
    _stub.run_check = lambda project_root, check_staged=False, strict_tokens=False, check_security=False: True
    sys.modules["desktop_spec.commands.check_cmd"] = _stub

from desktop_spec.commands.bootstrap_cmd import run_bootstrap
from desktop_spec.commands.init_cmd import run_init
from desktop_spec.commands.resolve_cmd import run_resolve
from desktop_spec.commands.sync_index_cmd import run_sync_index
from desktop_spec.commands.update_cmd import run_update


class TestUpdateAndBrownfield(unittest.TestCase):
    def test_init_empty_and_update_refresh_stack(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "desktop-empty-app"
            repo.mkdir()

            run_init(repo, harness="all", versioning="semver", ci="github")

            # Estructura base y .gitkeep
            self.assertTrue((repo / "docs" / "functional" / "user-flows" / ".gitkeep").is_file())
            self.assertTrue((repo / "docs" / "functional" / "use-cases" / ".gitkeep").is_file())
            self.assertTrue((repo / ".spec" / "templates" / "_template_user_flow.md").is_file())
            self.assertTrue((repo / ".spec" / "templates" / "_template_use_case.md").is_file())
            self.assertTrue((repo / ".graphifyignore").is_file())
            self.assertTrue((repo / ".gitignore").is_file())
            self.assertTrue((repo / ".github" / "workflows" / "desktop-spec-check.yml").is_file())

            # Config sin placeholders sin resolver
            cfg_txt = (repo / ".spec" / "config.yaml").read_text(encoding="utf-8")
            self.assertNotIn("{{", cfg_txt)
            self.assertIn("desktop-empty-app", cfg_txt)

            # Harnesses y skills
            self.assertTrue((repo / ".gemini" / "rules" / "desktop-spec.md").is_file())
            self.assertEqual(
                len(list((repo / ".gemini" / "skills").glob("*/SKILL.md"))),
                4,
            )
            self.assertTrue((repo / "CLAUDE.md").is_file())
            self.assertEqual(
                len(list((repo / ".claude" / "skills").glob("*/SKILL.md"))),
                5,
            )
            self.assertTrue((repo / ".cursor" / "rules" / "desktop-spec.mdc").is_file())
            self.assertEqual(
                len(list((repo / ".cursor" / "skills").glob("*/SKILL.md"))),
                5,
            )
            self.assertTrue((repo / ".windsurfrules").is_file())
            self.assertEqual(
                len(list((repo / ".windsurf" / "skills").glob("*/SKILL.md"))),
                5,
            )

            # Simular scaffold PySide6 posterior al init y refrescar stack
            (repo / "pyproject.toml").write_text(
                '[project]\nname = "desktop-empty-app"\nversion = "1.4.2"\ndependencies = ["PySide6>=6.7"]\n',
                encoding="utf-8",
            )
            ok = run_update(repo, harness="antigravity", refresh_stack=True)
            self.assertTrue(ok)

            updated_cfg = (repo / ".spec" / "config.yaml").read_text(encoding="utf-8")
            self.assertIn('name: "pyside6"', updated_cfg)
            self.assertIn('format: "toml"', updated_cfg)
            self.assertIn('current_version: "1.4.2"', updated_cfg)

            tech_stack = (repo / "docs" / "technical" / "tech-stack.md").read_text(encoding="utf-8")
            self.assertIn("PySide6", tech_stack)
            self.assertIn("v1.4.2", tech_stack)

    def test_update_dry_run_does_not_modify_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "dry-run-app"
            repo.mkdir()
            run_init(repo, harness="antigravity", ci="none")

            bp = repo / ".spec" / "templates" / "_template_user_flow.md"
            bp.unlink()

            ok = run_update(repo, harness="cursor", dry_run=True, ci="github")
            self.assertTrue(ok)
            self.assertFalse(bp.exists())
            self.assertFalse((repo / ".cursor").exists())
            self.assertFalse((repo / ".github" / "workflows" / "desktop-spec-check.yml").exists())

    def test_update_preserves_custom_rules_hooks_and_ci(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "custom-preserve-app"
            (repo / ".git" / "hooks").mkdir(parents=True)
            (repo / ".github" / "workflows").mkdir(parents=True)

            (repo / "CLAUDE.md").write_text(
                "<!-- BACKEND-SPEC:START -->\n# Backend rules\n<!-- BACKEND-SPEC:END -->\n\nMy custom rule.\n",
                encoding="utf-8",
            )
            (repo / ".git" / "hooks" / "pre-commit").write_text(
                "#!/usr/bin/env bash\necho custom-hook\nexit 0\n",
                encoding="utf-8",
            )
            custom_ci = "name: Custom CI\non: [push]\njobs:\n  test:\n    runs-on: ubuntu-latest\n"
            (repo / ".github" / "workflows" / "desktop-spec-check.yml").write_text(
                custom_ci,
                encoding="utf-8",
            )

            run_init(repo, harness="claude", ci="github")
            ok = run_update(repo, harness="claude", ci="github")
            self.assertTrue(ok)

            claude_txt = (repo / "CLAUDE.md").read_text(encoding="utf-8")
            self.assertIn("BACKEND-SPEC:START", claude_txt)
            self.assertIn("DESKTOP-SPEC:START", claude_txt)
            self.assertIn("My custom rule.", claude_txt)

            hook_txt = (repo / ".git" / "hooks" / "pre-commit").read_text(encoding="utf-8")
            self.assertIn("echo custom-hook", hook_txt)
            self.assertIn("# DESKTOP-SPEC:START", hook_txt)
            self.assertIn("# DESKTOP-SPEC:END", hook_txt)
            self.assertLess(hook_txt.index("# DESKTOP-SPEC:END"), hook_txt.rindex("exit 0"))

            ci_txt = (repo / ".github" / "workflows" / "desktop-spec-check.yml").read_text(
                encoding="utf-8"
            )
            self.assertEqual(ci_txt, custom_ci)

    def test_bootstrap_brownfield_checkbox_preservation_and_reset(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "avalonia-brownfield"
            (repo / "src" / "Modules" / "Inventory").mkdir(parents=True)
            (repo / "src" / "Modules" / "Billing").mkdir(parents=True)
            (repo / "src" / "Views").mkdir(parents=True)
            (repo / "src" / "ViewModels").mkdir(parents=True)
            (repo / "src" / "Data" / "migrations").mkdir(parents=True)
            (repo / "tests").mkdir(parents=True)
            (repo / "installer").mkdir(parents=True)

            (repo / "App.csproj").write_text(
                '<Project Sdk="Microsoft.NET.Sdk">\n'
                "  <PropertyGroup>\n"
                "    <Version>0.8.0</Version>\n"
                "  </PropertyGroup>\n"
                '  <ItemGroup><PackageReference Include="Avalonia" Version="11.0.0" /></ItemGroup>\n'
                "</Project>\n",
                encoding="utf-8",
            )
            (repo / "src" / "Modules" / "Inventory" / "InventoryService.cs").write_text(
                "public class InventoryService {}\n", encoding="utf-8"
            )
            (repo / "src" / "Modules" / "Billing" / "BillingRepository.cs").write_text(
                "public class BillingRepository {}\n", encoding="utf-8"
            )
            (repo / "src" / "Views" / "MainWindow.axaml").write_text(
                "<Window />\n", encoding="utf-8"
            )
            (repo / "src" / "ViewModels" / "MainWindowViewModel.cs").write_text(
                "public class MainWindowViewModel {}\n", encoding="utf-8"
            )
            (repo / "src" / "Data" / "migrations" / "001_init.sql").write_text(
                "CREATE TABLE items (id INTEGER PRIMARY KEY);\n", encoding="utf-8"
            )
            (repo / "tests" / "InventoryTests.cs").write_text(
                "public class InventoryTests {}\n", encoding="utf-8"
            )
            (repo / "installer" / "setup.wxs").write_text("<Wix />\n", encoding="utf-8")
            (repo / "README.md").write_text("# Legacy Desktop App\n", encoding="utf-8")

            run_init(repo, harness="antigravity")
            report_path = run_bootstrap(repo)
            self.assertTrue(report_path.is_file())

            report_txt = report_path.read_text(encoding="utf-8")
            self.assertIn("`billing`", report_txt)
            self.assertIn("`inventory`", report_txt)
            self.assertIn("MainWindow.axaml", report_txt)
            self.assertIn("MainWindowViewModel.cs", report_txt)
            self.assertIn("001_init.sql", report_txt)
            self.assertIn("setup.wxs", report_txt)

            func_idx = (repo / "docs" / "functional" / "index.md").read_text(encoding="utf-8")
            self.assertIn("`billing`", func_idx)
            self.assertIn("`inventory`", func_idx)
            self.assertIn("Pendiente As-Is", func_idx)

            # Marcar casilla manualmente y verificar preservacion
            target_cb = "- [ ] Inventariar modulos MOD-* y fronteras publicas en docs/technical/modular-architecture.md"
            checked_cb = "- [x] Inventariar modulos MOD-* y fronteras publicas en docs/technical/modular-architecture.md"
            self.assertIn(target_cb, report_txt)
            report_path.write_text(report_txt.replace(target_cb, checked_cb), encoding="utf-8")

            run_bootstrap(repo)
            self.assertIn(checked_cb, report_path.read_text(encoding="utf-8"))

            run_bootstrap(repo, reset=True)
            self.assertIn(target_cb, report_path.read_text(encoding="utf-8"))

    def test_sync_index_and_export_tokens(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "sync-tokens-app"
            repo.mkdir()
            run_init(repo, harness="antigravity")

            # Agregar modulo pendiente en config.yaml
            cfg_path = repo / ".spec" / "config.yaml"
            cfg_txt = cfg_path.read_text(encoding="utf-8")
            cfg_path.write_text(
                cfg_txt.replace("modules:\n  - core", "modules:\n  - core\n  - inventory\n  - billing"),
                encoding="utf-8",
            )

            # Crear UF y UC para inventory
            uf_file = repo / "docs" / "functional" / "user-flows" / "UF-INVENTORY-001-list.md"
            uf_file.write_text(
                "---\n"
                "id: UF-INVENTORY-001\n"
                "title: Listar Inventario\n"
                "module: inventory\n"
                "actor: Operador\n"
                "window_target: InventoryWindow\n"
                "entry_trigger: Menu Inventario\n"
                "status: Activo\n"
                "fsm_required: true\n"
                "invokes_use_case: UC-INVENTORY-001\n"
                "---\n\n# UF-INVENTORY-001: Listar Inventario\n",
                encoding="utf-8",
            )
            uc_file = repo / "docs" / "functional" / "use-cases" / "UC-INVENTORY-001-create.md"
            uc_file.write_text(
                "---\n"
                "id: UC-INVENTORY-001\n"
                "title: Crear Item\n"
                "module: inventory\n"
                "actor: Operador\n"
                "status: Activo\n"
                "ocl_applied: true\n"
                "trigger: Comando CrearItem\n"
                "---\n\n# UC-INVENTORY-001: Crear Item\n",
                encoding="utf-8",
            )

            # Crear requerimiento en pending.md
            pending_file = repo / "docs" / "backlog" / "pending.md"
            pending_file.write_text(
                pending_file.read_text(encoding="utf-8")
                + "\n### [REQ-DESK-001] Alta de inventario\n"
                "- **Prioridad:** P1\n"
                "- **Tipo:** MINOR\n"
                "- **Alcance:** full-module\n"
                "- **Version Objetivo:** `v0.2.0`\n"
                "- **Flujos UX:** `UF-INVENTORY-001`\n"
                "- **Casos de Uso:** `UC-INVENTORY-001`\n"
                "- **Referencias Tecnicas:** `docs/technical/modular-architecture.md`\n"
                "- **Modulos Afectados:** `inventory`\n"
                "#### Criterios de Aceptacion:\n"
                "- [ ] Cumple contrato\n",
                encoding="utf-8",
            )

            reqs, ufs, ucs = run_sync_index(repo, export_tokens=True)
            self.assertEqual((reqs, ufs, ucs), (2, 1, 1))

            backlog_idx = (repo / "docs" / "backlog" / "index.md").read_text(encoding="utf-8")
            self.assertIn("REQ-DESK-001", backlog_idx)

            func_idx = (repo / "docs" / "functional" / "index.md").read_text(encoding="utf-8")
            self.assertIn("UF-INVENTORY-001", func_idx)
            self.assertIn("UC-INVENTORY-001", func_idx)
            self.assertIn("`billing`", func_idx)
            self.assertNotIn("| `inventory` | Pendiente As-Is", func_idx)

            design_idx = (repo / "docs" / "design" / "index.md").read_text(encoding="utf-8")
            self.assertIn("compact", design_idx)
            self.assertIn("high-contrast", design_idx)

            tokens_json = repo / ".spec" / "specs" / "design.tokens.json"
            self.assertTrue(tokens_json.is_file())
            payload = json.loads(tokens_json.read_text(encoding="utf-8"))
            self.assertIn("color", payload)
            self.assertGreater(len(payload["color"]), 0)

    def test_resolve_bump_multi_manifest_tauri(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "tauri-multi-manifest"
            (repo / "src-tauri").mkdir(parents=True)
            (repo / "src-tauri" / "Cargo.toml").write_text(
                '[package]\nname = "tauri-app"\nversion = "0.1.0"\n\n[dependencies]\ntauri = "2"\n',
                encoding="utf-8",
            )
            (repo / "src-tauri" / "tauri.conf.json").write_text(
                json.dumps({"productName": "tauri-app", "version": "0.1.0"}, indent=2),
                encoding="utf-8",
            )
            (repo / "package.json").write_text(
                json.dumps(
                    {
                        "name": "tauri-app",
                        "version": "0.1.0",
                        "dependencies": {"@tauri-apps/api": "^2.0.0"},
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )

            run_init(repo, harness="antigravity", versioning="semver")

            pending_file = repo / "docs" / "backlog" / "pending.md"
            pending_txt = pending_file.read_text(encoding="utf-8")
            pending_txt += (
                "\n### [REQ-DESK-001] Soporte multi-ventana\n"
                "- **Prioridad:** P1\n"
                "- **Tipo:** MINOR\n"
                "- **Alcance:** full-module\n"
                "- **Versión Objetivo:** `v0.2.0`\n"
                "- **Flujos UX:** `N/A`\n"
                "- **Casos de Uso:** `N/A`\n"
                "- **Referencias Técnicas:** `docs/technical/modular-architecture.md`\n"
                "- **Módulos Afectados:** `core`\n"
                "#### Criterios de Aceptación:\n"
                "- [ ] Cumple contrato\n"
            )
            pending_file.write_text(pending_txt, encoding="utf-8")

            ok = run_resolve(repo, "REQ-DESK-001", auto_bump=True)
            self.assertTrue(ok)

            cargo_txt = (repo / "src-tauri" / "Cargo.toml").read_text(encoding="utf-8")
            self.assertIn('version = "0.2.0"', cargo_txt)

            tauri_conf = json.loads((repo / "src-tauri" / "tauri.conf.json").read_text(encoding="utf-8"))
            self.assertEqual(tauri_conf["version"], "0.2.0")

            pkg_json = json.loads((repo / "package.json").read_text(encoding="utf-8"))
            self.assertEqual(pkg_json["version"], "0.2.0")

            cfg_txt = (repo / ".spec" / "config.yaml").read_text(encoding="utf-8")
            self.assertIn('current_version: "0.2.0"', cfg_txt)
            self.assertIn('current_milestone: "v0.3.0"', cfg_txt)

            updated_pending = pending_file.read_text(encoding="utf-8")
            self.assertIn("## Milestone v0.3.0", updated_pending)
            self.assertNotIn("## Milestone v0.2.0", updated_pending)

            backlog_idx = (repo / "docs" / "backlog" / "index.md").read_text(encoding="utf-8")
            self.assertIn("- **Version Actual:** `v0.2.0`", backlog_idx)
            self.assertIn("- **Milestone Activo:** `v0.3.0`", backlog_idx)
            self.assertIn("## Resumen del Milestone Activo (`v0.3.0`)", backlog_idx)

            # Verificar proteccion anti-downgrade contra manifiesto acompanante mas alto
            pkg_json["version"] = "0.5.0"
            (repo / "package.json").write_text(json.dumps(pkg_json, indent=2), encoding="utf-8")
            updated_pending += (
                "\n### [REQ-DESK-002] Fix menor\n"
                "- **Prioridad:** P2\n"
                "- **Tipo:** PATCH\n"
                "- **Alcance:** domain-only\n"
                "- **Versión Objetivo:** `v0.3.0`\n"
                "#### Criterios de Aceptación:\n"
                "- [ ] Corregido\n"
            )
            pending_file.write_text(updated_pending, encoding="utf-8")

            ok2 = run_resolve(repo, "REQ-DESK-002", auto_bump=True)
            self.assertTrue(ok2)
            self.assertIn('version = "0.2.0"', (repo / "src-tauri" / "Cargo.toml").read_text(encoding="utf-8"))

    def test_bootstrap_brownfield_tauri(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "tauri-brownfield"
            (repo / "src-tauri" / "src" / "inventory").mkdir(parents=True)
            (repo / "src-tauri" / "src" / "db").mkdir(parents=True)
            (repo / "frontend" / "src" / "stores").mkdir(parents=True)

            (repo / "src-tauri" / "Cargo.toml").write_text(
                '[package]\nname = "tauri-brownfield"\nversion = "0.4.0"\n\n[dependencies]\ntauri = "2"\n',
                encoding="utf-8",
            )
            (repo / "src-tauri" / "tauri.conf.json").write_text(
                json.dumps({"productName": "tauri-brownfield", "version": "0.4.0"}),
                encoding="utf-8",
            )
            (repo / "package.json").write_text(
                json.dumps({"name": "tauri-brownfield", "version": "0.4.0", "dependencies": {"@tauri-apps/api": "^2.0.0"}}),
                encoding="utf-8",
            )
            (repo / "src-tauri" / "src" / "inventory" / "commands.rs").write_text(
                "pub fn list_items() {}\n", encoding="utf-8"
            )
            (repo / "src-tauri" / "src" / "db" / "rusqlite_repo.rs").write_text(
                "pub fn open_db() {}\n", encoding="utf-8"
            )
            (repo / "frontend" / "src" / "App.tsx").write_text(
                "export function App() { return null; }\n", encoding="utf-8"
            )
            (repo / "frontend" / "src" / "stores" / "appStore.ts").write_text(
                "export const appStore = {};\n", encoding="utf-8"
            )
            (repo / "frontend" / "src" / "App.test.tsx").write_text(
                "test('renders', () => {});\n", encoding="utf-8"
            )

            run_init(repo, harness="antigravity")
            report_path = run_bootstrap(repo)
            report_txt = report_path.read_text(encoding="utf-8")

            self.assertIn("ecosystem: tauri", report_txt)
            self.assertIn("`inventory`", report_txt)
            self.assertIn("frontend/src/App.tsx", report_txt)
            self.assertIn("frontend/src/stores/appStore.ts", report_txt)
            self.assertIn("src-tauri/src/db/rusqlite_repo.rs", report_txt)
            self.assertIn("src-tauri/tauri.conf.json", report_txt)
            self.assertIn("1 unit, 0 UI", report_txt)

    def test_bootstrap_brownfield_flutter_desktop(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "flutter-brownfield"
            (repo / "windows").mkdir(parents=True)
            (repo / "lib" / "modules" / "billing").mkdir(parents=True)
            (repo / "lib" / "ui").mkdir(parents=True)
            (repo / "lib" / "data").mkdir(parents=True)
            (repo / "test").mkdir(parents=True)

            (repo / "pubspec.yaml").write_text(
                "name: flutter_brownfield\nversion: 1.2.0+1\ndependencies:\n  flutter:\n    sdk: flutter\n",
                encoding="utf-8",
            )
            (repo / "lib" / "modules" / "billing" / "billing_service.dart").write_text(
                "class BillingService {}\n", encoding="utf-8"
            )
            (repo / "lib" / "ui" / "home_page.dart").write_text(
                "class HomePage {}\n", encoding="utf-8"
            )
            (repo / "lib" / "ui" / "billing_cubit.dart").write_text(
                "class BillingCubit {}\n", encoding="utf-8"
            )
            (repo / "lib" / "data" / "drift_database.dart").write_text(
                "class AppDatabase {}\n", encoding="utf-8"
            )
            (repo / "test" / "billing_test.dart").write_text(
                "void main() {}\n", encoding="utf-8"
            )

            run_init(repo, harness="antigravity")
            report_path = run_bootstrap(repo)
            report_txt = report_path.read_text(encoding="utf-8")

            self.assertIn("ecosystem: flutter-desktop", report_txt)
            self.assertIn("`billing`", report_txt)
            self.assertIn("lib/ui/home_page.dart", report_txt)
            self.assertIn("lib/ui/billing_cubit.dart", report_txt)
            self.assertIn("lib/data/drift_database.dart", report_txt)
            self.assertIn("1 unit, 0 UI", report_txt)


if __name__ == "__main__":
    unittest.main()
