import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

CLI_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = CLI_DIR.parent
if str(CLI_DIR) not in sys.path:
    sys.path.insert(0, str(CLI_DIR))

from desktop_spec.commands.check_cmd import run_check
from desktop_spec.commands.init_cmd import run_init
from desktop_spec.commands.new_req_cmd import run_new_req
from desktop_spec.commands.resolve_cmd import run_resolve
from desktop_spec.commands.sync_index_cmd import run_sync_index
from desktop_spec.common import read_config_settings
from desktop_spec.detector.version_extractor import extract_version


def _write_valid_uc(project_root: Path, uc_id: str = "UC-CORE-001", slug: str = "open-project") -> Path:
    uc_path = project_root / "docs" / "functional" / "use-cases" / f"{uc_id}-{slug}.md"
    uc_path.parent.mkdir(parents=True, exist_ok=True)
    uc_path.write_text(
        f"""---
id: {uc_id}
title: Abrir proyecto local
module: core
actor: Usuario Desktop
status: Activo
trigger: Click en Abrir Proyecto
ocl_applied: true
preconditions:
  - El espacio de trabajo local esta inicializado
---

# {uc_id}: Abrir proyecto local

- **Modulo:** `core`
- **Actor Principal:** `Usuario Desktop`
- **Disparador (Trigger):** `Click en Abrir Proyecto`

## 1. Diagrama de Proceso

```mermaid
flowchart TD
    A[Inicio] --> B[Validar ruta]
    B --> C[Cargar proyecto]
```

### Inputs Requeridos:
| Campo | Tipo | Obligatorio | Validacion |
| :--- | :--- | :--- | :--- |
| `project_path` | `string` | Si | Ruta canonica existente |

### Output Esperado:
| Campo | Tipo | Descripcion |
| :--- | :--- | :--- |
| `workspace` | `WorkspaceDTO` | Estado cargado del proyecto |

## 4. Reglas de Negocio
- **[BR-01] Ruta valida:**
  - **Descripcion:** El archivo debe existir en disco.
  ```ocl
  context OpenProjectCommand inv ValidPath: self.project_path.size() > 0
  ```
""",
        encoding="utf-8",
    )
    return uc_path


def _write_valid_uf(
    project_root: Path,
    uf_id: str = "UF-CORE-001",
    slug: str = "open-project",
    invokes_uc: str = "UC-CORE-001",
) -> Path:
    uf_path = project_root / "docs" / "functional" / "user-flows" / f"{uf_id}-{slug}.md"
    uf_path.parent.mkdir(parents=True, exist_ok=True)
    uf_path.write_text(
        f"""---
id: {uf_id}
title: Flujo de apertura de proyecto
module: core
actor: Usuario Desktop
window_target: WIN-MAIN-001
entry_trigger: Menu Archivo -> Abrir
shortcut: Ctrl+O
invokes_use_case: {invokes_uc}
status: Activo
accessibility:
  focus_management: Foco en lista de proyectos recientes
  os_accessibility_roles: AutomationProperties.Name en controles principales
  keyboard_navigation: Tab y Enter navegan la lista
---

# {uf_id}: Flujo de apertura de proyecto

- **Modulo:** `core`
- **Actor Principal:** `Usuario Desktop`
- **Ventana / Vista Destino:** `WIN-MAIN-001`
- **Disparador de Entrada:** `Menu Archivo -> Abrir`
- **Caso de Uso Delegado:** `{invokes_uc}`

```mermaid
flowchart LR
    Start[Abrir] --> Load[Cargar]
```

## 4. Matriz de Estados de Interfaz

| Estado | Disparador | Feedback Visual |
| :--- | :--- | :--- |
| `Loading` | Seleccion de archivo | Spinner en barra de estado |
| `Ready` | Carga exitosa | Render de arbol de archivos |

## 6. Accesibilidad Nativa
- **Foco Inicial:** Foco en lista de proyectos recientes
- **Roles de Accesibilidad:** AutomationProperties.Name en controles principales
- **Navegacion por Teclado:** Tab y Enter navegan la lista
""",
        encoding="utf-8",
    )
    return uf_path


class TestCliWorkflow(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = Path(tempfile.mkdtemp(prefix="dspec_e2e_"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_greenfield_e2e_lifecycle_init_req_sync_check_resolve_bump(self) -> None:
        (self.tmp_dir / "App.csproj").write_text(
            "<Project><PropertyGroup><Version>0.1.0</Version></PropertyGroup></Project>\n",
            encoding="utf-8",
        )
        run_init(target_dir=self.tmp_dir, ecosystem="avalonia", harness="antigravity")

        uc_path = _write_valid_uc(self.tmp_dir, "UC-CORE-001", "abrir-proyecto")
        uf_path = _write_valid_uf(self.tmp_dir, "UF-CORE-001", "abrir-proyecto", "UC-CORE-001")

        req_id = run_new_req(
            project_root=self.tmp_dir,
            title="Abrir proyecto local",
            module="core",
            scope="full-module",
            uf_ref=uf_path.relative_to(self.tmp_dir).as_posix(),
            uc_ref=uc_path.relative_to(self.tmp_dir).as_posix(),
            target_version="v0.2.0",
        )
        self.assertEqual(req_id, "REQ-DESK-CORE-001")

        u_cnt, d_cnt, r_cnt = run_sync_index(self.tmp_dir, export_tokens=True)
        self.assertGreaterEqual(u_cnt, 2)
        self.assertGreaterEqual(r_cnt, 1)
        self.assertTrue((self.tmp_dir / ".spec" / "specs" / "design.tokens.json").exists())

        self.assertTrue(run_check(self.tmp_dir))

        self.assertTrue(run_resolve(self.tmp_dir, "REQ-DESK-CORE-001", auto_bump=True))
        pending_txt = (self.tmp_dir / "docs" / "backlog" / "pending.md").read_text(encoding="utf-8")
        changelog_txt = (self.tmp_dir / "docs" / "backlog" / "changelog.md").read_text(encoding="utf-8")
        self.assertNotIn("REQ-DESK-CORE-001", pending_txt)
        self.assertIn("REQ-DESK-CORE-001", changelog_txt)
        self.assertIn("- [x]", changelog_txt)
        self.assertEqual(extract_version(self.tmp_dir / "App.csproj", "xml"), "0.2.0")

        cfg = read_config_settings(self.tmp_dir)
        self.assertEqual(cfg["current_version"], "0.2.0")

    def test_scope_validation_and_orphan_invokes_use_case(self) -> None:
        run_init(target_dir=self.tmp_dir, ecosystem="avalonia", harness="antigravity")

        # 1. UF con invokes_use_case huerfano debe fallar check
        uf_orphan = _write_valid_uf(self.tmp_dir, "UF-CORE-001", "orphan", invokes_uc="UC-CORE-999")
        run_sync_index(self.tmp_dir)
        self.assertFalse(run_check(self.tmp_dir))

        # Arreglar UC y UF
        uc_path = _write_valid_uc(self.tmp_dir, "UC-CORE-001", "orphan")
        uf_orphan.write_text(
            uf_orphan.read_text(encoding="utf-8").replace("UC-CORE-999", "UC-CORE-001"),
            encoding="utf-8",
        )
        run_sync_index(self.tmp_dir)
        self.assertTrue(run_check(self.tmp_dir))

        # 2. full-module sin UC debe fallar check
        req_bad = run_new_req(
            project_root=self.tmp_dir,
            title="Modulo incompleto",
            module="core",
            scope="full-module",
            uf_ref=uf_orphan.relative_to(self.tmp_dir).as_posix(),
            uc_ref="N/A",
        )
        self.assertEqual(req_bad, "REQ-DESK-CORE-001")
        self.assertFalse(run_check(self.tmp_dir))

        # 3. Resolver el malo y probar PATCH fast-track sin UF/UC (debe pasar)
        run_resolve(self.tmp_dir, "REQ-DESK-CORE-001")
        req_patch = run_new_req(
            project_root=self.tmp_dir,
            title="Fix menor en barra de estado",
            module="core",
            impact="PATCH",
            fast_track=True,
        )
        self.assertEqual(req_patch, "REQ-DESK-CORE-002")
        self.assertTrue(run_check(self.tmp_dir))

    def test_strict_tokens_detects_burned_hex_and_ignores_themes_and_comments(self) -> None:
        run_init(target_dir=self.tmp_dir, ecosystem="avalonia", harness="antigravity")
        views_dir = self.tmp_dir / "src" / "Views"
        views_dir.mkdir(parents=True, exist_ok=True)

        # Archivo de tema y comentario deben ser ignorados
        (views_dir / "ThemeColors.axaml").write_text(
            '<SolidColorBrush x:Key="Primary" Color="#112233" />\n',
            encoding="utf-8",
        )
        main_view = views_dir / "MainView.axaml"
        main_view.write_text('<!-- #AABBCC -->\n<TextBlock Text="Hola" />\n', encoding="utf-8")
        self.assertTrue(run_check(self.tmp_dir, strict_tokens=True))

        # Color hex quemado en vista real debe fallar
        main_view.write_text(
            '<Border Background="#FF5733"><TextBlock Text="Hola" /></Border>\n',
            encoding="utf-8",
        )
        self.assertFalse(run_check(self.tmp_dir, strict_tokens=True))

    def test_staged_commit_blocks_ghost_commits_and_module_boundary_violations(self) -> None:
        run_init(target_dir=self.tmp_dir, ecosystem="avalonia", harness="antigravity")
        subprocess.run(["git", "init"], cwd=str(self.tmp_dir), check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=str(self.tmp_dir), check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=str(self.tmp_dir), check=True)

        src_file = self.tmp_dir / "src" / "Modules" / "catalog" / "CatalogService.cs"
        src_file.parent.mkdir(parents=True, exist_ok=True)
        src_file.write_text("public class CatalogService {}\n", encoding="utf-8")
        subprocess.run(["git", "add", "src/Modules/catalog/CatalogService.cs"], cwd=str(self.tmp_dir), check=True)

        # Sin REQ activo -> bloqueado
        self.assertFalse(run_check(self.tmp_dir, check_staged=True))

        # Con REQ en otro modulo (core) -> bloqueado por frontera
        run_new_req(
            project_root=self.tmp_dir,
            title="Fix en core",
            module="core",
            impact="PATCH",
            fast_track=True,
        )
        self.assertFalse(run_check(self.tmp_dir, check_staged=True))

        # Con REQ en modulo catalog declarando el archivo -> pasa
        run_new_req(
            project_root=self.tmp_dir,
            title="Catalog service",
            module="catalog",
            impact="PATCH",
            fast_track=True,
        )
        self.assertTrue(run_check(self.tmp_dir, check_staged=True))

    def test_from_audit_and_anti_downgrade(self) -> None:
        (self.tmp_dir / "App.csproj").write_text(
            "<Project><PropertyGroup><Version>1.5.0</Version></PropertyGroup></Project>\n",
            encoding="utf-8",
        )
        run_init(target_dir=self.tmp_dir, ecosystem="avalonia", harness="antigravity")
        audit_file = self.tmp_dir / "docs" / "backlog" / "audit-proposals.md"
        audit_file.write_text(
            """# Propuestas de Auditoria

### [AUDIT-DESK-CORE-001] Evitar bloqueo en hilo UI
- **Dominio:** `core`
- **Categoria:** Bloqueo Hilo UI
- **Severidad Sugerida:** P1
- **Impacto Estimado:** PATCH
- **Evidencia en Codigo:** `src/Modules/core/Loader.cs:L12`
- **Estado:** Propuesto
""",
            encoding="utf-8",
        )

        req_id = run_new_req(
            project_root=self.tmp_dir,
            from_audit="AUDIT-DESK-CORE-001",
            target_version="v1.2.0",
        )
        self.assertEqual(req_id, "REQ-DESK-CORE-001")
        self.assertIn("Promovido a REQ-DESK-CORE-001", audit_file.read_text(encoding="utf-8"))

        # Anti-downgrade: 1.2.0 < 1.5.0 sin force_version no degrada App.csproj
        self.assertTrue(run_resolve(self.tmp_dir, "REQ-DESK-CORE-001", auto_bump=True, force_version=False))
        self.assertEqual(extract_version(self.tmp_dir / "App.csproj", "xml"), "1.5.0")

        # Con force_version si actualiza a 1.2.0
        req_id2 = run_new_req(
            project_root=self.tmp_dir,
            title="Forzar version",
            module="core",
            impact="PATCH",
            target_version="v1.2.0",
        )
        self.assertTrue(run_resolve(self.tmp_dir, req_id2, auto_bump=True, force_version=True))
        self.assertEqual(extract_version(self.tmp_dir / "App.csproj", "xml"), "1.2.0")

    def test_staged_docs_and_undeclared_source_bypass_is_blocked(self) -> None:
        run_init(target_dir=self.tmp_dir, ecosystem="avalonia", harness="antigravity")
        subprocess.run(["git", "init"], cwd=str(self.tmp_dir), check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=str(self.tmp_dir), check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=str(self.tmp_dir), check=True)

        run_new_req(
            project_root=self.tmp_dir,
            title="Declarar archivo inicial",
            module="core",
            impact="PATCH",
            fast_track=True,
        )
        undeclared_file = self.tmp_dir / "src" / "Modules" / "core" / "GhostHelper.cs"
        undeclared_file.parent.mkdir(parents=True, exist_ok=True)
        undeclared_file.write_text("public class GhostHelper {}\n", encoding="utf-8")

        subprocess.run(
            ["git", "add", "docs/backlog/pending.md", "src/Modules/core/GhostHelper.cs"],
            cwd=str(self.tmp_dir),
            check=True,
        )
        self.assertFalse(run_check(self.tmp_dir, check_staged=True))

    def test_staged_root_source_blocked_while_root_setup_ignored(self) -> None:
        run_init(target_dir=self.tmp_dir, ecosystem="pyside6", harness="antigravity")
        subprocess.run(["git", "init"], cwd=str(self.tmp_dir), check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=str(self.tmp_dir), check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=str(self.tmp_dir), check=True)

        setup_py = self.tmp_dir / "setup.py"
        setup_py.write_text("from setuptools import setup\nsetup(name='demo')\n", encoding="utf-8")
        subprocess.run(["git", "add", "setup.py"], cwd=str(self.tmp_dir), check=True)
        self.assertTrue(run_check(self.tmp_dir, check_staged=True))

        main_py = self.tmp_dir / "main.py"
        main_py.write_text("print('hello desktop')\n", encoding="utf-8")
        subprocess.run(["git", "add", "main.py"], cwd=str(self.tmp_dir), check=True)
        self.assertFalse(run_check(self.tmp_dir, check_staged=True))

    def test_strict_tokens_wave5_profiles_and_ignores_configs(self) -> None:
        run_init(target_dir=self.tmp_dir, ecosystem="tauri", harness="antigravity")

        # Config files with hex colors must be ignored
        src_dir = self.tmp_dir / "src"
        src_dir.mkdir(parents=True, exist_ok=True)
        (src_dir / "tailwind.config.js").write_text("module.exports = { theme: { primary: '#123456' } };\n", encoding="utf-8")
        (src_dir / "vite.config.ts").write_text("export default { define: { COLOR: '#654321' } };\n", encoding="utf-8")
        (src_dir / "postcss.config.mjs").write_text("export default { color: '#ABCDEF' };\n", encoding="utf-8")
        self.assertTrue(run_check(self.tmp_dir, strict_tokens=True))

        # Burned hex in lib/ui/*.dart must fail
        dart_view = self.tmp_dir / "lib" / "ui" / "home_page.dart"
        dart_view.parent.mkdir(parents=True, exist_ok=True)
        dart_view.write_text("const bg = '#FF00AA';\n", encoding="utf-8")
        self.assertFalse(run_check(self.tmp_dir, strict_tokens=True))
        dart_view.unlink()

        # Burned hex in src/components/*.tsx must fail
        tsx_view = self.tmp_dir / "src" / "components" / "Button.tsx"
        tsx_view.parent.mkdir(parents=True, exist_ok=True)
        tsx_view.write_text("export const style = { color: '#AA11BB' };\n", encoding="utf-8")
        self.assertFalse(run_check(self.tmp_dir, strict_tokens=True))
        tsx_view.unlink()

        # Burned hex in Sources/Views/*.swift must fail
        swift_view = self.tmp_dir / "Sources" / "Views" / "ContentView.swift"
        swift_view.parent.mkdir(parents=True, exist_ok=True)
        swift_view.write_text("let accent = \"#11AA22\"\n", encoding="utf-8")
        self.assertFalse(run_check(self.tmp_dir, strict_tokens=True))

    def test_frontmatter_additional_fields_and_technical_h2_validation(self) -> None:
        run_init(target_dir=self.tmp_dir, ecosystem="avalonia", harness="antigravity")
        self.assertTrue(run_check(self.tmp_dir))

        tokens_path = self.tmp_dir / "docs" / "design" / "tokens-and-themes.md"
        orig_tokens = tokens_path.read_text(encoding="utf-8")

        # Invalid density_modes must fail
        tokens_path.write_text(orig_tokens.replace("- compact", "- ultra-dense"), encoding="utf-8")
        self.assertFalse(run_check(self.tmp_dir))

        # Invalid window_chrome must fail
        tokens_path.write_text(orig_tokens.replace("titlebar_style: native", "titlebar_style: floating-magic"), encoding="utf-8")
        self.assertFalse(run_check(self.tmp_dir))
        tokens_path.write_text(orig_tokens, encoding="utf-8")

        # Invalid target_platforms in packaging-and-release.md must fail
        pkg_path = self.tmp_dir / "docs" / "technical" / "packaging-and-release.md"
        orig_pkg = pkg_path.read_text(encoding="utf-8")
        pkg_path.write_text(
            orig_pkg.replace("branching_model: github-flow", "branching_model: github-flow\ntarget_platforms:\n  - android"),
            encoding="utf-8",
        )
        self.assertFalse(run_check(self.tmp_dir))

        # Missing ## heading in technical doc body must fail
        pkg_path.write_text("---\nartifact_type: packaging-and-release\nbranching_model: github-flow\n---\n\n# Solo H1\n", encoding="utf-8")
        self.assertFalse(run_check(self.tmp_dir))

    def test_cli_entrypoint_version(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(CLI_DIR / "main.py"), "--version"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True,
        )
        self.assertIn("desktop-spec", proc.stdout)


if __name__ == "__main__":
    unittest.main()
