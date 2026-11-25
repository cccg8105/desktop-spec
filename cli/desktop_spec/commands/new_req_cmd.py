import re
from pathlib import Path
from typing import Dict, Optional

from desktop_spec.commands.sync_index_cmd import run_sync_index
from desktop_spec.common import read_config_settings, slugify
from desktop_spec.detector.ecosystem_detector import build_profile_context

VALID_SCOPES = ("ui-only", "domain-only", "full-module", "packaging-infra")


def _find_audit_proposal(project_root: Path, audit_id: str) -> Optional[Dict[str, str]]:
    """Busca una propuesta AUDIT-DESK-* en docs/backlog/audit-proposals.md."""
    audit_file = project_root / "docs" / "backlog" / "audit-proposals.md"
    if not audit_file.exists():
        return None
    content = audit_file.read_text(encoding="utf-8")
    clean_id = audit_id.strip("[]")
    pattern = rf"###\s*\[{re.escape(clean_id)}\]\s*([^\n\r]+)(.*?)(?=###\s*\[|\Z)"
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        return None

    title = match.group(1).strip()
    body = match.group(2)

    m_mod = re.search(r"-\s*\*\*(?:Dominio|M[oó]dulo):\*\*\s*`?([a-zA-Z0-9_-]+)`?", body)
    m_imp = re.search(
        r"-\s*\*\*Impacto Estimado:\*\*\s*`?(MAJOR|MINOR|PATCH)`?", body, re.IGNORECASE
    )
    m_sev = re.search(r"-\s*\*\*Severidad Sugerida:\*\*\s*`?(P[123])`?", body, re.IGNORECASE)
    m_evid = re.search(r"-\s*\*\*Evidencia en C[oó]digo:\*\*\s*`?([^`\n\r]+)`?", body)

    return {
        "id": clean_id,
        "title": title,
        "module": m_mod.group(1).strip() if m_mod else "core",
        "impact": m_imp.group(1).strip().upper() if m_imp else "PATCH",
        "priority": m_sev.group(1).strip().upper() if m_sev else "P2",
        "evidence": m_evid.group(1).strip() if m_evid else "",
    }


def _mark_audit_promoted(project_root: Path, audit_id: str, req_id: str) -> bool:
    """Marca una propuesta AUDIT-DESK-* como promovida en audit-proposals.md."""
    audit_file = project_root / "docs" / "backlog" / "audit-proposals.md"
    if not audit_file.exists():
        return False
    content = audit_file.read_text(encoding="utf-8")
    clean_id = audit_id.strip("[]")
    pattern = rf"(###\s*\[{re.escape(clean_id)}\][^\n\r]*\n.*?-\s*\*\*Estado:\*\*\s*)([^\n\r]+)"
    updated, count = re.subn(
        pattern, rf"\1Promovido a {req_id}", content, count=1, flags=re.DOTALL
    )
    if count > 0:
        audit_file.write_text(updated, encoding="utf-8")
        return True
    return False


def _resolve_desktop_artifact(
    cfg: Dict,
    ecosystem: str,
    scope: str,
    module: str,
    slug: str,
    slug_snake: str,
    slug_pascal: str,
) -> str:
    """Calcula la ruta del artefacto principal segun ecosistema, alcance y modulo."""
    ui_dir = str(cfg.get("ui_dir", "src/Views")).rstrip("/")
    modules_dir = str(cfg.get("modules_dir", "src/Modules")).rstrip("/")
    src_ext = str(cfg.get("src_ext", ".cs"))
    mod_lower = module.lower()
    mod_pascal = "".join(p.capitalize() for p in re.split(r"[-_]", mod_lower) if p) or "Core"

    if scope == "packaging-infra":
        return f".github/workflows/{slug}.yml"

    if scope == "ui-only":
        if ecosystem == "avalonia":
            return f"{ui_dir}/{mod_pascal}/{slug_pascal}View.axaml"
        if ecosystem in ("wpf", "winui3", "maui-desktop"):
            return f"{ui_dir}/{mod_pascal}/{slug_pascal}View.xaml"
        if ecosystem in ("pyside6", "pyqt6", "flet"):
            return f"{ui_dir}/{mod_lower}/{slug_snake}_view.py"
        if ecosystem == "compose-desktop":
            return f"{ui_dir}/{mod_lower}/{slug_pascal}Screen.kt"
        if ecosystem == "javafx":
            return f"{ui_dir}/{mod_lower}/{slug_pascal}Controller.java"
        if ecosystem == "rust-native":
            return f"{ui_dir}/{mod_lower}/{slug_snake}.rs"
        if ecosystem == "qt-cpp":
            return f"{ui_dir}/{mod_lower}/{slug_pascal}View.qml"
        if ecosystem in ("tauri", "electron", "wails"):
            return f"{ui_dir}/{mod_lower}/{slug_pascal}.tsx"
        if ecosystem == "flutter-desktop":
            return f"{ui_dir}/{mod_lower}/{slug_snake}_page.dart"
        if ecosystem == "swift-macos":
            return f"{ui_dir}/{mod_pascal}/{slug_pascal}View.swift"
        return f"{ui_dir}/{mod_lower}/{slug_pascal}{src_ext}"

    if ecosystem in ("pyside6", "pyqt6", "flet"):
        return f"{modules_dir}/{mod_lower}/{slug_snake}.py"
    if ecosystem in ("rust-native", "tauri"):
        return f"{modules_dir}/{mod_lower}/{slug_snake}.rs"
    if ecosystem == "electron":
        return f"{modules_dir}/{mod_lower}/{slug_snake}.ts"
    if ecosystem == "wails":
        return f"{modules_dir}/{mod_lower}/{slug_snake}.go"
    if ecosystem == "flutter-desktop":
        return f"{modules_dir}/{mod_lower}/{slug_snake}.dart"
    if ecosystem == "swift-macos":
        return f"{modules_dir}/{mod_pascal}/{slug_pascal}.swift"
    if ecosystem == "qt-cpp":
        return f"{modules_dir}/{mod_lower}/{slug_pascal}.cpp"
    return f"{modules_dir}/{mod_lower}/{slug_pascal}{src_ext}"


def run_new_req(
    project_root: Path,
    title: Optional[str] = None,
    module: str = "core",
    priority: str = "P2",
    impact: str = "MINOR",
    scope: Optional[str] = None,
    target_version: Optional[str] = None,
    uf_ref: Optional[str] = None,
    uc_ref: Optional[str] = None,
    tokens: Optional[str] = None,
    fast_track: bool = False,
    from_audit: Optional[str] = None,
) -> Optional[str]:
    """Registra un requerimiento REQ-DESK-* en docs/backlog/pending.md y sincroniza indices."""
    project_root = Path(project_root).resolve()
    pending_file = project_root / "docs" / "backlog" / "pending.md"
    changelog_file = project_root / "docs" / "backlog" / "changelog.md"

    if not pending_file.exists():
        print("[ERROR] docs/backlog/pending.md no encontrado. Ejecuta 'desktop-spec init' primero.")
        return None

    audit_info: Optional[Dict[str, str]] = None
    if from_audit:
        audit_info = _find_audit_proposal(project_root, from_audit)
        if not audit_info:
            print(f"[ERROR] Propuesta '{from_audit}' no encontrada en docs/backlog/audit-proposals.md.")
            return None
        title = title or audit_info["title"]
        module = audit_info["module"]
        impact = audit_info["impact"]
        priority = priority if priority != "P2" else audit_info["priority"]
        print(f"[INFO] Promoviendo [{audit_info['id']}]: '{title}' ({impact}, {priority})")
    elif not title:
        print("[ERROR] Debes indicar un titulo o usar --from-audit <ID>.")
        return None

    if scope is not None and scope not in VALID_SCOPES:
        print(f"[ERROR] Scope invalido '{scope}'. Valores permitidos: {', '.join(VALID_SCOPES)}")
        return None

    if scope is None:
        if uf_ref and not uc_ref:
            resolved_scope = "ui-only"
        elif uc_ref and not uf_ref:
            resolved_scope = "domain-only"
        else:
            resolved_scope = "full-module"
    else:
        resolved_scope = scope

    pending_content = pending_file.read_text(encoding="utf-8")
    changelog_content = changelog_file.read_text(encoding="utf-8") if changelog_file.exists() else ""

    mod_upper = re.sub(r"[^A-Z0-9]", "", module.upper()) or "CORE"
    mod_lower = re.sub(r"[^a-zA-Z0-9_-]", "", module.lower()) or "core"
    combined = re.sub(r"```.*?```", "", pending_content + "\n" + changelog_content, flags=re.DOTALL)
    existing_ids = re.findall(rf"REQ-(?:DESK-)?{mod_upper}-(\d+)", combined)
    next_num = max(int(i) for i in existing_ids) + 1 if existing_ids else 1
    req_id = f"REQ-DESK-{mod_upper}-{next_num:03d}"

    cfg = read_config_settings(project_root)
    profile = build_profile_context(project_root, ecosystem_key=cfg["ecosystem"])

    if not target_version:
        v_match = re.search(r"##\s+Milestone\s+([^\s\n]+)", pending_content)
        target_version = v_match.group(1).strip() if v_match else cfg["current_milestone"]

    is_fast_track = fast_track or (impact.upper() == "PATCH")
    slug = slugify(title)
    slug_snake = slug.replace("-", "_")
    slug_pascal = "".join(p.capitalize() for p in slug.split("-")) or "Feature"

    src_artifact = _resolve_desktop_artifact(
        cfg=cfg,
        ecosystem=profile["ecosystem"],
        scope=resolved_scope,
        module=mod_lower,
        slug=slug,
        slug_snake=slug_snake,
        slug_pascal=slug_pascal,
    )
    test_artifact = (
        str(cfg["test_pattern"])
        .replace("{slug}", slug)
        .replace("{slug_snake}", slug_snake)
        .replace("{slug_pascal}", slug_pascal)
        .replace("{module}", mod_lower)
        .replace("{domain}", mod_lower)
    )

    if audit_info and audit_info.get("evidence"):
        clean_evid = audit_info["evidence"].split(":")[0].strip()
        if (project_root / clean_evid).exists():
            src_artifact = clean_evid

    action_src = "MODIFY" if (project_root / src_artifact).exists() else "NEW"
    token_line = tokens or "color-surface, color-primary, color-text-main"
    token_spans = ", ".join(
        f"`{t.strip('` ')}`" for t in token_line.split(",") if t.strip("` ")
    )

    if is_fast_track:
        resolved_uf = uf_ref or "N/A (PATCH / Fast-Track)"
        resolved_uc = uc_ref or "N/A (PATCH / Fast-Track)"
        tech_refs = "`docs/design/tokens-and-themes.md`, `docs/technical/modular-architecture.md`"
        tipo_label = "Hotfix / Fix (PATCH - Fast-Track)"
        restrictions_block = (
            "  - Carril Fast-Track (`PATCH`): prohibido romper fachadas de modulo, "
            "contratos de ventana, migraciones destructivas o quemar colores hex fuera de tokens."
        )
        criteria_block = (
            "- [ ] Reproducir el defecto mediante test automatizado de regresion en rojo antes del fix.\n"
            "- [ ] Aplicar correccion minima verificando tests unitarios y de UI al 100%."
        )
    else:
        if resolved_scope == "ui-only":
            resolved_uf = uf_ref or f"docs/functional/user-flows/UF-{mod_upper}-{next_num:03d}-{slug}.md"
            resolved_uc = uc_ref or "N/A (ui-only)"
            tech_refs = "`docs/design/tokens-and-themes.md`, `docs/technical/windowing-and-os-contracts.md`"
        elif resolved_scope == "domain-only":
            resolved_uf = uf_ref or "N/A (domain-only)"
            resolved_uc = uc_ref or f"docs/functional/use-cases/UC-{mod_upper}-{next_num:03d}-{slug}.md"
            tech_refs = "`docs/technical/modular-architecture.md`, `docs/technical/local-persistence.md`"
        elif resolved_scope == "packaging-infra":
            resolved_uf = uf_ref or "N/A (packaging-infra)"
            resolved_uc = uc_ref or "N/A (packaging-infra)"
            tech_refs = "`docs/technical/packaging-and-release.md`, `docs/technical/tech-stack.md`"
        else:
            resolved_uf = uf_ref or f"docs/functional/user-flows/UF-{mod_upper}-{next_num:03d}-{slug}.md"
            resolved_uc = uc_ref or f"docs/functional/use-cases/UC-{mod_upper}-{next_num:03d}-{slug}.md"
            tech_refs = (
                "`docs/design/tokens-and-themes.md`, `docs/technical/modular-architecture.md`, "
                "`docs/technical/windowing-and-os-contracts.md`, `docs/technical/local-persistence.md`"
            )

        tipo_label = f"Feature ({impact.upper()})"
        restrictions_block = (
            "  - Respetar fronteras del monolito modular (fachadas publicas), no bloquear el hilo UI, "
            "usar OS Keyring para secretos y consumir semantic design tokens."
        )
        criteria_block = (
            "- [ ] Implementar flujo UX y/o caso de uso segun alcance respetando invariantes OCL y estados borde.\n"
            "- [ ] Pruebas unitarias, de arquitectura modular y de UI headless pasando al 100%."
        )

    req_block = f"""
### [{req_id}] {title}
- **Prioridad:** {priority}
- **Tipo:** {tipo_label}
- **Alcance (Scope):** `{resolved_scope}`
- **Versión Objetivo:** `{target_version}`
- **Flujos UX (`UF-*`):** `{resolved_uf}`
- **Casos de Uso (`UC-*`):** `{resolved_uc}`
- **Referencias Técnicas:** {tech_refs}
- **Módulos Afectados:** `{mod_lower}`
- **Tokens Consumidos:** {token_spans}

#### Fronteras y Artefactos:
- **Artefactos a Modificar / Crear:**
  - `{src_artifact}` [{action_src}]
  - `{test_artifact}` [NEW]
- **Restricciones:**
{restrictions_block}

#### Criterios de Aceptación:
{criteria_block}
"""

    pending_file.write_text(pending_content.rstrip() + "\n" + req_block, encoding="utf-8")

    if from_audit and _mark_audit_promoted(project_root, from_audit, req_id):
        print(f"[OK] Estado actualizado en audit-proposals.md: Promovido a {req_id}")

    run_sync_index(project_root)
    print(f"[OK] Requerimiento creado: {req_id} en docs/backlog/pending.md")
    if not is_fast_track:
        if not resolved_uf.upper().startswith("N/A"):
            print(f"[INFO] Crea/actualiza '{resolved_uf}' antes de ejecutar 'desktop-spec check'.")
        if not resolved_uc.upper().startswith("N/A"):
            print(f"[INFO] Crea/actualiza '{resolved_uc}' antes de ejecutar 'desktop-spec check'.")
    return req_id
