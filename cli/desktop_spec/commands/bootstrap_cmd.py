import datetime
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

from desktop_spec.commands.sync_index_cmd import _replace_sync_section, run_sync_index
from desktop_spec.common import build_doc_context, read_config_settings, render_placeholders
from desktop_spec.detector.ecosystem_detector import build_profile_context, detect_desktop_ecosystem
from desktop_spec.detector.version_extractor import extract_version
from desktop_spec.validator.schema_validator import locate_framework_asset

SKIP_DIRS = {
    ".git",
    ".spec",
    "docs",
    "bin",
    "obj",
    "target",
    "build",
    "dist",
    "out",
    ".gradle",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "node_modules",
    "cmake-build-debug",
    "cmake-build-release",
    "coverage",
    "test-results",
    "graphify-out",
    ".gemini",
    ".cursor",
    ".claude",
    ".windsurf",
    ".vs",
    ".idea",
}

VIEW_EXTS = {".xaml", ".axaml", ".fxml", ".qml", ".ui", ".slint"}
WEB_VIEW_EXTS = {".tsx", ".jsx", ".svelte", ".vue"}
DB_EXTS = {".db", ".sqlite", ".sqlite3"}
PACKAGING_EXTS = {".wxs", ".iss", ".desktop", ".entitlements"}
STATEHOLDER_KEYWORDS = (
    "viewmodel",
    "presenter",
    "controller",
    "bloc",
    "cubit",
    "notifier",
    "store",
    "provider",
)
GENERIC_DESKTOP_FOLDERS = {
    "src",
    "app",
    "main",
    "java",
    "kotlin",
    "modules",
    "views",
    "windows",
    "dialogs",
    "pages",
    "screens",
    "controls",
    "components",
    "viewmodels",
    "presenters",
    "controllers",
    "models",
    "domain",
    "data",
    "persistence",
    "repositories",
    "migrations",
    "services",
    "infrastructure",
    "common",
    "shared",
    "utils",
    "helpers",
    "resources",
    "assets",
    "styles",
    "themes",
    "core",
    "ui",
    "tests",
    "test",
}


def _scan_desktop_inventory(project_root: Path) -> Dict[str, List[str]]:
    views_and_windows: List[str] = []
    viewmodels_presenters: List[str] = []
    local_persistence: List[str] = []
    unit_tests: List[str] = []
    ui_tests: List[str] = []
    packaging_ci: List[str] = []
    candidate_modules: Set[str] = set()

    for path in sorted(project_root.rglob("*")):
        if any(part in SKIP_DIRS for part in path.parts) or not path.is_file():
            continue

        rel = path.relative_to(project_root).as_posix()
        low_rel = rel.lower()
        low_name = path.name.lower()
        ext = path.suffix.lower()

        is_ui_test = bool(
            re.search(r"(uitest|headless|flaui|testfx|appium|pytest_qt)", low_name)
            or low_rel.startswith(("ui_tests/", "ui-tests/", "e2e/", "integration_test/"))
            or "/ui_tests/" in low_rel
        )
        is_unit_test = bool(
            re.search(
                r"(^test_.*\.py$|_test\.py$|_tests?\.rs$|_tests?\.(cpp|cc|cxx)$"
                r"|tests?\.(cs|kt|java|swift)$|spec\.(cs|kt|java)$"
                r"|_test\.dart$|_test\.go$|\.test\.(ts|tsx)$|\.spec\.ts$)",
                low_name,
            )
            or low_rel.startswith(("tests/", "test/", "src/test/"))
            or "/tests/" in low_rel
            or "/test/" in low_rel
        )

        if is_ui_test:
            ui_tests.append(rel)
            continue
        if is_unit_test:
            unit_tests.append(rel)
            continue

        if (
            ext in PACKAGING_EXTS
            or low_name in (
                "info.plist",
                "package.appxmanifest",
                "tauri.conf.json",
                "wails.json",
                "package.swift",
                "exportoptions.plist",
            )
            or low_name.startswith(("electron-builder.", "forge.config."))
            or low_rel.startswith(".github/workflows/")
        ):
            packaging_ci.append(rel)

        if ext in DB_EXTS or "/migrations/" in low_rel or low_rel.startswith("migrations/") or any(
            k in low_name
            for k in (
                "repository",
                "dbcontext",
                "sqlite",
                "migration",
                "dao",
                "keyring",
                "drift",
                "sqflite",
                "better-sqlite",
                "better_sqlite",
                "sqlx",
                "rusqlite",
                "grdb",
                "swiftdata",
            )
        ):
            local_persistence.append(rel)

        is_stateholder = any(k in low_name for k in STATEHOLDER_KEYWORDS)
        if is_stateholder and ext in (
            ".cs",
            ".py",
            ".kt",
            ".java",
            ".rs",
            ".cpp",
            ".h",
            ".hpp",
            ".ts",
            ".tsx",
            ".go",
            ".dart",
            ".swift",
        ):
            viewmodels_presenters.append(rel)

        in_ui_dir = (
            low_rel.startswith(("lib/ui/", "sources/views/", "frontend/src/", "src/renderer/", "src/components/"))
            or any(seg in low_rel for seg in ("/lib/ui/", "/sources/views/", "/frontend/src/", "/src/renderer/", "/src/components/"))
        )
        if (
            ext in VIEW_EXTS
            or (ext in WEB_VIEW_EXTS and not is_stateholder)
            or low_name.endswith(("_page.dart", "_screen.dart"))
            or (
                in_ui_dir
                and not is_stateholder
                and ext in (".dart", ".swift", ".ts", ".tsx", ".js", ".jsx", ".svelte", ".vue", ".html")
            )
            or (
                ext == ".swift"
                and not is_stateholder
                and (
                    any(k in low_name for k in ("window", "dialog", "view", "screen", "page"))
                    or low_rel.startswith("sources/views/")
                    or "/sources/views/" in low_rel
                )
            )
            or (
                any(k in low_name for k in ("window", "dialog", "view"))
                and not is_stateholder
                and ext in (".cs", ".py", ".kt", ".java", ".rs", ".cpp", ".h", ".hpp", ".dart")
            )
        ):
            views_and_windows.append(rel)

        parts = Path(rel).parts
        if "modules" in [p.lower() for p in parts[:-1]]:
            mod_idx = [p.lower() for p in parts[:-1]].index("modules")
            if mod_idx + 1 < len(parts) - 1:
                clean_mod = re.sub(r"[^a-z0-9_-]", "", parts[mod_idx + 1].lower())
                if clean_mod and clean_mod not in GENERIC_DESKTOP_FOLDERS and len(clean_mod) >= 2:
                    candidate_modules.add(clean_mod)
        elif len(parts) >= 4 and parts[0].lower() == "src-tauri" and parts[1].lower() == "src":
            clean_mod = re.sub(r"[^a-z0-9_-]", "", parts[2].lower())
            if clean_mod and clean_mod not in GENERIC_DESKTOP_FOLDERS and len(clean_mod) >= 2:
                candidate_modules.add(clean_mod)
        elif len(parts) >= 3 and parts[0].lower() == "internal":
            clean_mod = re.sub(r"[^a-z0-9_-]", "", parts[1].lower())
            if clean_mod and clean_mod not in GENERIC_DESKTOP_FOLDERS and len(clean_mod) >= 2:
                candidate_modules.add(clean_mod)
        elif len(parts) >= 4 and parts[0].lower() == "src" and parts[1].lower() == "main":
            clean_mod = re.sub(r"[^a-z0-9_-]", "", parts[2].lower())
            if clean_mod and clean_mod not in GENERIC_DESKTOP_FOLDERS and len(clean_mod) >= 2:
                candidate_modules.add(clean_mod)
        elif ext == ".csproj" and len(parts) >= 2 and parts[0].lower() in ("src", "modules"):
            clean_mod = re.sub(r"[^a-z0-9_-]", "", path.stem.lower())
            if clean_mod and clean_mod not in GENERIC_DESKTOP_FOLDERS and "test" not in clean_mod:
                candidate_modules.add(clean_mod)
        elif len(parts) >= 3 and parts[0].lower() in ("src", "app"):
            clean_seg = re.sub(r"[^a-z0-9_-]", "", parts[1].lower())
            if clean_seg and clean_seg not in GENERIC_DESKTOP_FOLDERS and len(clean_seg) >= 3:
                candidate_modules.add(clean_seg)

    return {
        "modules": sorted(candidate_modules)[:15] or ["core"],
        "views_and_windows": views_and_windows[:40],
        "viewmodels_presenters": viewmodels_presenters[:40],
        "local_persistence": local_persistence[:30],
        "unit_tests": unit_tests,
        "ui_tests": ui_tests,
        "packaging_ci": packaging_ci[:20],
    }


def _scan_legacy_docs(project_root: Path) -> List[Dict[str, str]]:
    legacy_docs: List[Dict[str, str]] = []
    latest_src_mtime = 0.0

    for path in project_root.rglob("*"):
        if any(part in SKIP_DIRS for part in path.parts) or not path.is_file():
            continue
        if path.suffix.lower() in (
            VIEW_EXTS
            | WEB_VIEW_EXTS
            | {".cs", ".py", ".kt", ".java", ".rs", ".cpp", ".ts", ".tsx", ".js", ".jsx", ".go", ".dart", ".swift"}
        ):
            try:
                latest_src_mtime = max(latest_src_mtime, path.stat().st_mtime)
            except Exception:
                pass

    for path in project_root.rglob("*"):
        if any(part in SKIP_DIRS for part in path.parts) or not path.is_file():
            continue
        rel = path.relative_to(project_root).as_posix()
        low_name = path.name.lower()
        if rel.startswith("docs/"):
            continue
        if low_name in ("readme.md", "architecture.md", "design.md", "contributing.md"):
            try:
                drift = (
                    "Posible desfase (anterior a cambios recientes de codigo)"
                    if latest_src_mtime > 0 and (latest_src_mtime - path.stat().st_mtime) > 86400 * 7
                    else "Reciente / Coincidente"
                )
            except Exception:
                drift = "No determinado"
            legacy_docs.append({"path": rel, "drift": drift})

    return legacy_docs[:15]


def _read_graphify_summary(project_root: Path) -> List[str]:
    graph_json = project_root / "graphify-out" / "graph.json"
    if not graph_json.exists():
        return []
    try:
        payload = json.loads(graph_json.read_text(encoding="utf-8"))
        nodes = payload.get("nodes", [])
        links = payload.get("links") or payload.get("edges") or []
        degree: Dict[str, int] = {}
        labels: Dict[str, str] = {}
        for n in nodes:
            nid = str(n.get("id", ""))
            labels[nid] = str(n.get("label") or n.get("name") or nid)
            degree[nid] = 0
        for edge in links:
            src = str(edge.get("source", ""))
            tgt = str(edge.get("target", ""))
            degree[src] = degree.get(src, 0) + 1
            degree[tgt] = degree.get(tgt, 0) + 1
        top = sorted(degree.items(), key=lambda kv: kv[1], reverse=True)[:8]
        return [f"`{labels.get(nid, nid)}` ({deg} conexiones)" for nid, deg in top if deg > 0]
    except Exception:
        return []


def _extract_previous_checkbox_state(report_path: Path) -> Tuple[Dict[str, bool], str]:
    state: Dict[str, bool] = {}
    mode = "progressive"
    if not report_path.exists():
        return state, mode
    try:
        text = report_path.read_text(encoding="utf-8")
        m_mode = re.search(r"onboarding_mode:\s*([a-zA-Z0-9_-]+)", text)
        if m_mode:
            mode = m_mode.group(1).strip()
        for line in text.splitlines():
            m_cb = re.search(r"-\s*\[([ xX])\]\s*(.+)", line)
            if m_cb:
                state[m_cb.group(2).strip()] = m_cb.group(1).lower() == "x"
    except Exception:
        pass
    return state, mode


def _update_tech_stack_sync(
    docs_dir: Path, profile: Dict[str, str], current_version: str
) -> None:
    """Actualiza el bloque SYNC:TECH_STACK en docs/technical/tech-stack.md."""
    tech_stack_file = docs_dir / "technical" / "tech-stack.md"
    if not tech_stack_file.exists():
        return

    manifest_name = profile.get("manifest") or profile.get("version_file") or "App.csproj"
    table_block = (
        "| Componente | Tecnologia Seleccionada | Manifiesto / Configuracion | Responsabilidad |\n"
        "| :--- | :--- | :--- | :--- |\n"
        f"| **Ecosistema y Lenguaje** | `{profile['runtime_label']}` (`{profile['language']}` / `{profile['family']}`) | `{manifest_name}` (`v{current_version}`) | Runtime nativo compilado o empaquetado de proceso unico. |\n"
        f"| **Toolkit UI y Patron** | `{profile['ui_toolkit']}` | `{profile['ui_dir']}` | Ventanas, controles nativos, binding reactivo y accesibilidad del SO. |\n"
        f"| **Arquitectura** | Monolito Modular (MVVM / MVI + Clean) | `{profile['modules_dir']}` | Aislamiento estricto por modulos `MOD-*` con fachadas publicas. |\n"
        f"| **Base de Datos Embebida** | `{profile['embedded_db']}` | Modo local con migraciones *on-startup* | Persistencia transaccional local en disco del usuario. |\n"
        "| **Resguardo de Secretos** | OS Keyring Nativo (Credential Manager / Keychain / Secret Service) | Proveedor nativo del SO | Almacenamiento cifrado de llaves locales, tokens o claves de proyecto. |\n"
        f"| **Testing Unitario y UI** | `{profile['unit_test_runner']}` + `{profile['ui_test_runner']}` | `{profile['test_pattern']}` | Pruebas de dominio, fronteras modulares y UI *headless* / automatizacion nativa. |"
    )
    updated = _replace_sync_section(
        tech_stack_file.read_text(encoding="utf-8"),
        "TECH_STACK",
        r"##\s*(?:1\.\s*)?N[uú]cleo Tecnol[oó]gico[^\n]*",
        table_block,
    )
    tech_stack_file.write_text(updated, encoding="utf-8")


def _update_config_modules(spec_dir: Path, modules: List[str]) -> None:
    cfg_path = spec_dir / "config.yaml"
    if not cfg_path.exists() or not modules:
        return
    raw = cfg_path.read_text(encoding="utf-8")
    mod_block = "modules:\n" + "\n".join(f"  - {m}" for m in modules)
    if re.search(r"^modules:\s*\r?\n(?:\s+-\s+.+\r?\n?)*", raw, re.MULTILINE):
        updated = re.sub(
            r"^modules:\s*\r?\n(?:\s+-\s+.+\r?\n?)*",
            mod_block + "\n",
            raw,
            count=1,
            flags=re.MULTILINE,
        )
        cfg_path.write_text(updated, encoding="utf-8")


def run_bootstrap(
    project_root: Path,
    mode: str = "auto",
    reset: bool = False,
) -> Path:
    """Escanea un repo desktop existente (Brownfield), pre-puebla tech-stack, config.yaml y .spec/bootstrap-report.md."""
    project_root = Path(project_root).resolve()
    spec_dir = project_root / ".spec"
    docs_dir = project_root / "docs"

    if not docs_dir.exists() or not spec_dir.exists():
        raise RuntimeError(
            "El proyecto aun no tiene estructura desktop-spec. Ejecuta 'desktop-spec init' primero."
        )

    print(f"\n[INFO] Ejecutando Brownfield Bootstrap Desktop en: {project_root}")

    detection = detect_desktop_ecosystem(project_root)
    profile = detection.get("detected") or build_profile_context(project_root)
    ver_path = detection.get("version_path")
    detected_ver = (
        extract_version(ver_path, profile["format"]) if ver_path else None
    ) or "0.1.0"

    inventory = _scan_desktop_inventory(project_root)
    legacy_docs = _scan_legacy_docs(project_root)
    god_nodes = _read_graphify_summary(project_root)
    today = datetime.date.today().isoformat()

    total_tests = len(inventory["unit_tests"]) + len(inventory["ui_tests"])
    view_count = len(inventory["views_and_windows"])
    if total_tests == 0:
        test_baseline = "none (0 tests unitarios/UI detectados: priorizar caracterizacion de dominio y UI)"
    elif len(inventory["ui_tests"]) > 0 or total_tests >= max(2, view_count):
        test_baseline = f"solid ({len(inventory['unit_tests'])} unit, {len(inventory['ui_tests'])} UI)"
    else:
        test_baseline = f"partial ({len(inventory['unit_tests'])} unit, {len(inventory['ui_tests'])} UI)"

    report_path = spec_dir / "bootstrap-report.md"
    prev_state, prev_mode = ({}, "progressive") if reset else _extract_previous_checkbox_state(report_path)
    resolved_mode = (
        ("progressive" if len(inventory["modules"]) > 3 or view_count > 8 else "full")
        if mode == "auto"
        else mode
    )
    if mode == "auto" and prev_state and not reset:
        resolved_mode = prev_mode

    def cb(label: str, auto_checked: bool = False) -> str:
        checked = prev_state.get(label, auto_checked)
        return f"- [{'x' if checked else ' '}] {label}"

    _update_tech_stack_sync(docs_dir, profile, detected_ver)
    _update_config_modules(spec_dir, inventory["modules"])

    audit_file = docs_dir / "backlog" / "audit-proposals.md"
    if not audit_file.exists():
        templates_root = locate_framework_asset("templates")
        audit_src = (
            templates_root / ".spec" / "docs" / "backlog" / "audit-proposals.md"
            if templates_root
            else None
        )
        if audit_src and audit_src.exists():
            cfg = read_config_settings(project_root)
            ctx = build_doc_context(
                project_root.name,
                profile,
                detected_ver,
                cfg["current_milestone"],
                cfg["versioning_scheme"],
                today,
            )
            audit_file.parent.mkdir(parents=True, exist_ok=True)
            audit_file.write_text(
                render_placeholders(audit_src.read_text(encoding="utf-8"), ctx),
                encoding="utf-8",
            )

    modules_md = ", ".join(f"`{m}`" for m in inventory["modules"])
    views_md = "\n".join(f"- `{v}`" for v in inventory["views_and_windows"][:20]) or "- *(Sin ventanas/vistas detectadas automaticamente)*"
    vms_md = "\n".join(f"- `{vm}`" for vm in inventory["viewmodels_presenters"][:20]) or "- *(Sin ViewModels/Presenters detectados automaticamente)*"
    db_md = "\n".join(f"- `{d}`" for d in inventory["local_persistence"][:15]) or "- *(Sin archivos de persistencia local detectados)*"
    pkg_md = "\n".join(f"- `{p}`" for p in inventory["packaging_ci"]) or "- *(Sin configuracion de empaquetado/CI detectada)*"
    god_md = "\n".join(f"- {g}" for g in god_nodes) or "- *(Sin grafo Graphify detectado: recomienda ejecutar `graphify` respetando `.graphifyignore`)*"
    legacy_md = "\n".join(f"- `{d['path']}` -- {d['drift']}" for d in legacy_docs) or "- *(Sin documentacion previa conflictiva detectada)*"

    report_md = f"""---
artifact_type: bootstrap-report
onboarding_mode: {resolved_mode}
ecosystem: {profile['ecosystem']}
test_baseline: "{test_baseline}"
generated_at: "{today}"
---

# Reporte de Adopcion Brownfield Desktop — {project_root.name}

- **Modo Seleccionado:** `{resolved_mode}`
- **Stack Detectado:** `{profile['runtime_label']}` (`{profile['language']}`, `{profile['ui_toolkit']}`)
- **Persistencia / Tests:** `{profile['embedded_db']}` | `{profile['unit_test_runner']}` / `{profile['ui_test_runner']}`
- **Linea Base de Pruebas:** `{test_baseline}`
- **Modulos Detectados:** {modules_md}

---

## Checklist GPS de Ingenieria Inversa Desktop

### Fase 1: Linea Base, Manifiesto y Empaquetado
{cb("Validar docs/technical/tech-stack.md y .spec/config.yaml con el ecosistema nativo real", True)}
{cb("Revisar manifiesto, instaladores (.wxs/.iss/Info.plist) y workflows en docs/technical/packaging-and-release.md")}

### Fase 2: Arquitectura Modular, Ventanas y Persistencia Local
{cb("Inventariar modulos MOD-* y fronteras publicas en docs/technical/modular-architecture.md")}
{cb("Documentar ventanas WIN-*, ciclo de vida y OS Keyring en docs/technical/windowing-and-os-contracts.md")}
{cb("Mapear SQLite/migraciones y repositorios en docs/technical/local-persistence.md")}
{cb("Documentar paleta light/dark/system/high-contrast y densidad en docs/design/tokens-and-themes.md")}

### Fase 3: Flujos UX (UF-*) y Casos de Uso (UC-*)
{cb("Documentar flujos de interaccion criticos iniciales en docs/functional/user-flows/UF-*.md")}
{cb("Documentar casos de uso de dominio iniciales en docs/functional/use-cases/UC-*.md")}
{cb("Verificar modulos legados pendientes (Just-In-Time) en docs/functional/index.md")}

### Fase 4: Triage de Deuda, Seguridad Local y Cierre
{cb("Registrar fugas de frontera modular, secretos planos o bloqueos del hilo UI como AUDIT-DESK-* en docs/backlog/audit-proposals.md")}

---

## Inventario Tecnico Detectado

### Ventanas y Vistas ({len(inventory['views_and_windows'])})
{views_md}

### ViewModels y Presenters ({len(inventory['viewmodels_presenters'])})
{vms_md}

### Persistencia Local ({len(inventory['local_persistence'])})
{db_md}

### Empaquetado y CI ({len(inventory['packaging_ci'])})
{pkg_md}

### Documentacion Previa / Posible Doc Drift
{legacy_md}

### Graphify God Nodes
{god_md}
"""
    report_path.write_text(report_md, encoding="utf-8")
    run_sync_index(project_root)

    print(f"[OK] Reporte Brownfield generado: {report_path.relative_to(project_root).as_posix()}")
    print(f"[OK] Tech stack actualizado en docs/technical/tech-stack.md ({profile['runtime_label']})")
    return report_path
