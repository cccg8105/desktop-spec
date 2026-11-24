import json
import re
from pathlib import Path
from typing import List, Set, Tuple

from desktop_spec.validator.schema_validator import (
    export_w3c_design_tokens,
    extract_design_tokens_summary,
    extract_requirement_data,
    extract_use_case_data,
    extract_user_flow_data,
)


def _replace_sync_section(
    doc_text: str, marker: str, fallback_heading_regex: str, new_block: str
) -> str:
    start_tag = f"<!-- SYNC:{marker}:START -->"
    end_tag = f"<!-- SYNC:{marker}:END -->"

    if start_tag in doc_text and end_tag in doc_text:
        pattern = re.compile(rf"{re.escape(start_tag)}.*?{re.escape(end_tag)}", re.DOTALL)
        replacement = f"{start_tag}\n{new_block.strip()}\n{end_tag}"
        return pattern.sub(lambda _: replacement, doc_text, count=1)

    heading_match = re.search(fallback_heading_regex, doc_text)
    if heading_match:
        insert_start = heading_match.end()
        next_sec = re.search(r"\n---\s*\n|\n##\s+", doc_text[insert_start:])
        if next_sec:
            end_pos = insert_start + next_sec.start()
            return (
                doc_text[:insert_start]
                + f"\n\n{start_tag}\n{new_block.strip()}\n{end_tag}\n"
                + doc_text[end_pos:]
            )
        return doc_text[:insert_start].rstrip() + f"\n\n{start_tag}\n{new_block.strip()}\n{end_tag}\n"

    return doc_text.rstrip() + f"\n\n{start_tag}\n{new_block.strip()}\n{end_tag}\n"


def _discover_user_flow_files(func_dir: Path) -> List[Path]:
    files: List[Path] = []
    uf_dir = func_dir / "user-flows"
    if uf_dir.exists():
        for md in sorted(uf_dir.rglob("*.md")):
            if not md.name.startswith("_") and md.name != "index.md":
                files.append(md)

    for sub in sorted(func_dir.iterdir()):
        if sub.is_dir() and sub.name not in ("user-flows", "use-cases"):
            for md in sorted(sub.rglob("*.md")):
                if (
                    not md.name.startswith("_")
                    and md.name != "index.md"
                    and md.name.upper().startswith("UF-")
                ):
                    files.append(md)
    return files


def _discover_use_case_files(func_dir: Path) -> List[Path]:
    files: List[Path] = []
    uc_dir = func_dir / "use-cases"
    if uc_dir.exists():
        for md in sorted(uc_dir.rglob("*.md")):
            if not md.name.startswith("_") and md.name != "index.md":
                files.append(md)

    for sub in sorted(func_dir.iterdir()):
        if sub.is_dir() and sub.name not in ("user-flows", "use-cases"):
            for md in sorted(sub.rglob("*.md")):
                if (
                    not md.name.startswith("_")
                    and md.name != "index.md"
                    and md.name.upper().startswith("UC-")
                ):
                    files.append(md)
    return files


def _read_detected_modules(project_root: Path) -> List[str]:
    report_file = project_root / ".spec" / "bootstrap-report.md"
    config_file = project_root / ".spec" / "config.yaml"
    modules: Set[str] = set()

    if report_file.exists():
        try:
            text = report_file.read_text(encoding="utf-8")
            m = re.search(
                r"-\s*\*\*M[oó]dulos(?:\s+Desktop)?\s+(?:Detectados|Sugeridos):\*\*\s*(.+)",
                text,
            )
            if m:
                modules.update(re.findall(r"`([a-zA-Z0-9_-]+)`", m.group(1)))
        except Exception:
            pass

    if not modules and config_file.exists():
        try:
            cfg_text = config_file.read_text(encoding="utf-8")
            sec_m = re.search(r"^modules:\s*\r?\n((?:\s+-\s+.+\r?\n?)*)", cfg_text, re.MULTILINE)
            if sec_m:
                for item in re.findall(r"^\s+-\s+([a-zA-Z0-9_-]+)", sec_m.group(1), re.MULTILINE):
                    modules.add(item.strip())
        except Exception:
            pass

    return sorted(modules)


def _sync_backlog_index(docs_dir: Path) -> int:
    pending_file = docs_dir / "backlog" / "pending.md"
    backlog_index = docs_dir / "backlog" / "index.md"
    if not (pending_file.exists() and backlog_index.exists()):
        return 0

    pending_content = pending_file.read_text(encoding="utf-8")
    req_blocks = re.findall(
        r"(###\s*\[REQ-[A-Z0-9-]+\].*?)(?=###\s*\[REQ-|\n##\s+Milestone|\Z)",
        pending_content,
        re.DOTALL,
    )

    rows: List[str] = []
    for raw_block in req_blocks:
        req_data = extract_requirement_data(raw_block)
        req_id = req_data["id"]
        if not req_id:
            continue
        criteria = req_data["acceptance_criteria"]
        if criteria and all(c["completed"] for c in criteria):
            status = "Completado"
        elif any(c["completed"] for c in criteria):
            status = "En Progreso"
        else:
            status = "Pendiente"

        uf_refs = req_data["references"]["user_flows"]
        uc_refs = req_data["references"]["use_cases"]
        func_parts = [f"`{r}`" for r in (uf_refs + uc_refs)]
        func_disp = ", ".join(func_parts) if func_parts else "`N/A`"
        tech_refs = ", ".join(f"`{t}`" for t in req_data["references"]["technical"]) or "N/A"
        rows.append(
            f"| `{req_id}` | {req_data['title']} | `{req_data['impact_type'] or 'MINOR'}` | "
            f"`{req_data['priority'] or 'P2'}` | {status} | {func_disp} | {tech_refs} |"
        )

    if rows:
        table_md = (
            "| ID Requerimiento | Titulo | Impacto | Prioridad | Estado | Ref. Funcional | Ref. Tecnica |\n"
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
            + "\n".join(rows)
        )
    else:
        table_md = "_Sin requerimientos pendientes en el milestone actual._"

    updated = _replace_sync_section(
        backlog_index.read_text(encoding="utf-8"),
        "BACKLOG_TABLE",
        r"##\s*Resumen del Milestone Activo[^\n]*",
        table_md,
    )
    backlog_index.write_text(updated, encoding="utf-8")
    return len(rows)


def _sync_functional_index(project_root: Path, docs_dir: Path) -> Tuple[int, int]:
    func_dir = docs_dir / "functional"
    func_index = func_dir / "index.md"
    if not func_index.exists():
        return 0, 0

    documented_modules: Set[str] = set()

    # 1. User Flows (UF-*)
    uf_files = _discover_user_flow_files(func_dir)
    uf_rows: List[str] = []
    for uf_path in uf_files:
        uf_data, _ = extract_user_flow_data(uf_path.read_text(encoding="utf-8"))
        uf_id = uf_data.get("id") or uf_path.stem
        title = uf_data.get("title") or uf_path.stem
        module = (uf_data.get("module") or "core").lower()
        window_target = uf_data.get("window_target") or "MainWindow"
        status = uf_data.get("status") or "Activo"
        fsm_flag = "Si" if uf_data.get("fsm_required") else "No"
        documented_modules.add(module)

        rel_link = uf_path.relative_to(func_dir).as_posix()
        uf_rows.append(
            f"| `{uf_id}` | {title} | `{window_target}` | `{module}` | {fsm_flag} | {status} | [{uf_path.name}](./{rel_link}) |"
        )

    if uf_rows:
        uf_block = (
            "| ID Flujo | Titulo | Ventana | Modulo | FSM | Estado | Documento |\n"
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
            + "\n".join(uf_rows)
        )
    else:
        uf_block = (
            "_Aun no hay flujos de interaccion registrados. Se agregaran automaticamente al "
            "formalizar requerimientos `MAJOR` o `MINOR` en `docs/functional/user-flows/`._"
        )

    updated_func = _replace_sync_section(
        func_index.read_text(encoding="utf-8"),
        "USER_FLOWS_CATALOG",
        r"##\s*Catalogo de Flujos de Interacci[oó]n[^\n]*",
        uf_block,
    )

    # 2. Use Cases (UC-*)
    uc_files = _discover_use_case_files(func_dir)
    uc_rows: List[str] = []
    for uc_path in uc_files:
        uc_data, _ = extract_use_case_data(uc_path.read_text(encoding="utf-8"))
        uc_id = uc_data.get("id") or uc_path.stem
        title = uc_data.get("title") or uc_path.stem
        module = (uc_data.get("module") or "core").lower()
        actor = uc_data.get("actor") or "Usuario"
        status = uc_data.get("status") or "Activo"
        ocl_flag = "Si" if uc_data.get("ocl_applied") else "No"
        documented_modules.add(module)

        rel_link = uc_path.relative_to(func_dir).as_posix()
        uc_rows.append(
            f"| `{uc_id}` | {title} | `{module}` | `{actor}` | {ocl_flag} | {status} | [{uc_path.name}](./{rel_link}) |"
        )

    if uc_rows:
        uc_block = (
            "| ID Caso de Uso | Titulo | Modulo | Actor | OCL | Estado | Documento |\n"
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
            + "\n".join(uc_rows)
        )
    else:
        uc_block = (
            "_Aun no hay casos de uso registrados. Se agregaran automaticamente al "
            "formalizar requerimientos `MAJOR` o `MINOR` en `docs/functional/use-cases/`._"
        )

    updated_func = _replace_sync_section(
        updated_func,
        "USE_CASES_CATALOG",
        r"##\s*Catalogo de Casos de Uso de Dominio[^\n]*",
        uc_block,
    )

    # 3. Modulos pendientes As-Is
    candidate_modules = _read_detected_modules(project_root)
    pending_modules = [
        m for m in candidate_modules if m.lower() != "core" and m.lower() not in documented_modules
    ]
    if pending_modules:
        pending_rows = "\n".join(
            f"| `{m}` | Pendiente As-Is | Ejecutar `/desk-bootstrap` o documentar `UF-{m.upper()}-001` / `UC-{m.upper()}-001` al tocar el modulo |"
            for m in pending_modules
        )
        pending_block = (
            "| Modulo Legado | Estado | Accion Recomendada (Just-In-Time) |\n"
            "| :--- | :--- | :--- |\n"
            + pending_rows
        )
    else:
        pending_block = "_Sin modulos legados pendientes de levantamiento._"

    updated_func = _replace_sync_section(
        updated_func,
        "PENDING_MODULES",
        r"##\s*M[oó]dulos Legados Detectados[^\n]*",
        pending_block,
    )
    func_index.write_text(updated_func, encoding="utf-8")
    return len(uf_rows), len(uc_rows)


def _sync_design_index(docs_dir: Path) -> None:
    design_dir = docs_dir / "design"
    design_index = design_dir / "index.md"
    tokens_file = design_dir / "tokens-and-themes.md"
    if not (design_index.exists() and tokens_file.exists()):
        return

    summary = extract_design_tokens_summary(tokens_file.read_text(encoding="utf-8"))
    theme_modes = (
        ", ".join(f"`{m}`" for m in summary["theme_modes"])
        or "`light`, `dark`, `system`, `high-contrast`"
    )
    density_modes = (
        ", ".join(f"`{d}`" for d in summary["density_modes"])
        or "`compact`, `standard`, `comfortable`"
    )
    color_count = len(summary["semantic_colors"])
    disp = summary["display_font"] or "Fuente de interfaz del SO"
    mono = summary["mono_font"] or "Monoespaciada tabular"

    summary_block = (
        f"- **Modos de tema activos:** {theme_modes} ({color_count} tokens cromaticos semanticos).\n"
        f"- **Modos de densidad desktop:** {density_modes}.\n"
        f"- **Tipografias:** {disp} (display/UI) y {mono} (monoespacio tabular).\n"
        "- **Regla estricta:** Prohibido hardcodear colores hex, tamanos o estilos fuera del catalogo semantico definido en [`tokens-and-themes.md`](./tokens-and-themes.md)."
    )
    updated = _replace_sync_section(
        design_index.read_text(encoding="utf-8"),
        "DESIGN_TOKENS_SUMMARY",
        r"##\s*Resumen de Tokens Activos[^\n]*",
        summary_block,
    )
    design_index.write_text(updated, encoding="utf-8")


def _export_w3c_tokens_file(project_root: Path, docs_dir: Path) -> bool:
    tokens_md = docs_dir / "design" / "tokens-and-themes.md"
    if not tokens_md.exists():
        print("[WARN] No se encontro docs/design/tokens-and-themes.md para exportar tokens W3C.")
        return False

    payload = export_w3c_design_tokens(tokens_md.read_text(encoding="utf-8"))
    out_file = project_root / ".spec" / "specs" / "design.tokens.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    color_count = len(payload.get("color", {}))
    print(f"[OK] Design tokens W3C DTCG exportados en .spec/specs/design.tokens.json ({color_count} colores)")
    return True


def run_sync_index(project_root: Path, export_tokens: bool = False) -> Tuple[int, int, int]:
    """Sincroniza en disco docs/backlog/index.md, docs/functional/index.md y docs/design/index.md."""
    project_root = Path(project_root).resolve()
    docs_dir = project_root / "docs"
    if not docs_dir.exists():
        print("[ERROR] Directorio docs/ no encontrado.")
        return 0, 0, 0

    print("\n[INFO] Sincronizando catalogos index.md en disco...")
    synced_reqs = _sync_backlog_index(docs_dir)
    synced_ufs, synced_ucs = _sync_functional_index(project_root, docs_dir)
    _sync_design_index(docs_dir)

    if export_tokens:
        _export_w3c_tokens_file(project_root, docs_dir)

    print(
        f"[OK] Indices sincronizados: {synced_reqs} req(s) en backlog/index.md, "
        f"{synced_ufs} flujo(s) UF-* y {synced_ucs} caso(s) de uso UC-* en functional/index.md."
    )
    return synced_reqs, synced_ufs, synced_ucs
