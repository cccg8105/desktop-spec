import datetime
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from desktop_spec.commands.sync_index_cmd import run_sync_index
from desktop_spec.common import _clean_yaml_scalar, read_config_settings
from desktop_spec.detector.version_extractor import (
    _infer_manifest_format,
    compare_versions,
    compute_next_milestone,
    extract_version,
    sync_multi_manifest_versions,
)


_HYBRID_COMPANIONS: Dict[str, List[Tuple[str, str]]] = {
    "tauri": [
        ("src-tauri/Cargo.toml", "toml"),
        ("src-tauri/tauri.conf.json", "json"),
        ("package.json", "json"),
    ],
    "wails": [
        ("wails.json", "json"),
        ("frontend/package.json", "json"),
    ],
    "electron": [
        ("package.json", "json"),
    ],
}


def _read_extra_version_files(project_root: Path, cfg: Dict[str, Any]) -> List[Tuple[str, Optional[str]]]:
    """Lee entradas opcionales bajo version_files en cfg o .spec/config.yaml."""
    entries: List[Tuple[str, Optional[str]]] = []
    raw_list = cfg.get("version_files")
    if isinstance(raw_list, list):
        for item in raw_list:
            if isinstance(item, dict) and item.get("path"):
                entries.append((str(item["path"]), item.get("format")))
            elif isinstance(item, str) and item.strip():
                entries.append((item.strip(), None))
        return entries

    cfg_path = project_root / ".spec" / "config.yaml"
    if not cfg_path.exists():
        return entries

    in_section = False
    current_entry: Optional[Dict[str, str]] = None
    for line in cfg_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        if indent == 0:
            if current_entry and current_entry.get("path"):
                entries.append((current_entry["path"], current_entry.get("format")))
                current_entry = None
            in_section = bool(re.match(r"^version_files\s*:\s*$", stripped))
            continue
        if not in_section:
            continue
        if stripped.startswith("- "):
            if current_entry and current_entry.get("path"):
                entries.append((current_entry["path"], current_entry.get("format")))
                current_entry = None
            item_body = stripped[2:].strip()
            kv = re.match(r"^([A-Za-z0-9_-]+)\s*:\s*(.+)$", item_body)
            if kv:
                current_entry = {kv.group(1): _clean_yaml_scalar(kv.group(2))}
            else:
                scalar = _clean_yaml_scalar(item_body)
                if scalar and "{{" not in scalar:
                    entries.append((scalar, None))
        elif current_entry is not None:
            kv = re.match(r"^([A-Za-z0-9_-]+)\s*:\s*(.+)$", stripped)
            if kv:
                current_entry[kv.group(1)] = _clean_yaml_scalar(kv.group(2))

    if current_entry and current_entry.get("path"):
        entries.append((current_entry["path"], current_entry.get("format")))
    return entries


def _collect_manifest_targets(project_root: Path, cfg: Dict[str, Any]) -> List[Tuple[Path, str]]:
    """Recopila el manifiesto principal, acompanantes hibridos existentes y version_files sin duplicados."""
    targets: List[Tuple[Path, str]] = []
    seen: Set[Path] = set()

    def _add(path_obj: Path, fmt: str) -> None:
        resolved = path_obj.resolve()
        if resolved not in seen:
            seen.add(resolved)
            targets.append((path_obj, fmt))

    main_path = project_root / cfg["manifest_path"]
    _add(main_path, cfg["manifest_format"])

    eco = str(cfg.get("ecosystem", "")).lower()
    for rel_path, fmt in _HYBRID_COMPANIONS.get(eco, []):
        cand = project_root / rel_path
        if cand.is_file():
            _add(cand, fmt)

    for rel_path, opt_fmt in _read_extra_version_files(project_root, cfg):
        cand = project_root / rel_path
        if cand.is_file() or opt_fmt == "plain":
            fmt = opt_fmt or _infer_manifest_format(cand)
            _add(cand, fmt)

    return targets


def run_resolve(
    project_root: Path,
    req_id: str,
    auto_bump: bool = False,
    force_version: bool = False,
) -> bool:
    """Archiva un REQ-DESK-* completado en changelog.md, sincroniza indices y opcionalmente hace bump."""
    project_root = Path(project_root).resolve()
    docs_dir = project_root / "docs"
    pending_file = docs_dir / "backlog" / "pending.md"
    changelog_file = docs_dir / "backlog" / "changelog.md"

    if not pending_file.exists() or not changelog_file.exists():
        print("[ERROR] docs/backlog/pending.md o changelog.md no encontrados.")
        return False

    pending_content = pending_file.read_text(encoding="utf-8")
    pattern = rf"(###\s*\[{re.escape(req_id)}\].*?)(?=###\s*\[REQ-|\n##\s+Milestone|\Z)"
    match = re.search(pattern, pending_content, re.DOTALL)
    if not match:
        print(f"[ERROR] Requerimiento {req_id} no encontrado en docs/backlog/pending.md.")
        return False

    req_block = re.sub(r"(?:\r?\n---\s*)+\Z", "", match.group(1).strip()).strip()
    v_match = re.search(r"-\s*\*\*Versi[oó]n Objetivo:\*\*\s*`?([^\n`]+)`?", req_block)
    target_version = v_match.group(1).strip() if v_match else "v0.1.0"
    if not target_version.startswith("v"):
        target_version = f"v{target_version}"

    # 1. Retirar de pending.md y sincronizar indice
    new_pending = pending_content[: match.start()] + pending_content[match.end() :]
    new_pending = re.sub(r"\n{3,}", "\n\n", new_pending).rstrip() + "\n"
    pending_file.write_text(new_pending, encoding="utf-8")
    print(f"[OK] Requerimiento {req_id} retirado de docs/backlog/pending.md")
    run_sync_index(project_root)

    # 2. Registrar en changelog.md
    changelog_content = changelog_file.read_text(encoding="utf-8")
    today = datetime.date.today().isoformat()
    resolved_block = re.sub(r"-\s*\[ \]", "- [x]", req_block)
    lines = resolved_block.splitlines()
    if lines:
        lines.insert(1, f"- **Fecha de Resolución:** `{today}`")
        resolved_block = "\n".join(lines)

    version_header_regex = rf"^##\s+Release\s+{re.escape(target_version)}\b[^\n]*"
    header_match = re.search(version_header_regex, changelog_content, re.MULTILINE)
    if header_match:
        end_pos = header_match.end()
        updated_changelog = (
            changelog_content[:end_pos]
            + f"\n\n{resolved_block}\n"
            + changelog_content[end_pos:]
        )
    else:
        updated_changelog = (
            changelog_content.rstrip()
            + f"\n\n---\n\n## Release {target_version} (Actualizado: {today})\n\n{resolved_block}\n"
        )
    changelog_file.write_text(updated_changelog, encoding="utf-8")
    print(f"[OK] Requerimiento {req_id} archivado en docs/backlog/changelog.md")

    # 3. Auto-bump opcional en manifiesto(s) real(es) + .spec/config.yaml + backlog
    if auto_bump:
        cfg = read_config_settings(project_root)
        scheme = cfg["versioning_scheme"]
        clean_ver = target_version.lstrip("vV")
        targets = _collect_manifest_targets(project_root, cfg)

        highest_ver: Optional[str] = None
        highest_path: Optional[Path] = None
        for t_path, t_fmt in targets:
            ver = extract_version(t_path, t_fmt)
            if ver and (highest_ver is None or compare_versions(ver, highest_ver) > 0):
                highest_ver = ver
                highest_path = t_path

        if (
            highest_ver
            and highest_path is not None
            and compare_versions(clean_ver, highest_ver) < 0
            and not force_version
        ):
            print(
                f"[WARN] Proteccion anti-downgrade: {clean_ver} < {highest_ver} en "
                f"{highest_path.name}. Usa --force-version para sobrescribir."
            )
        else:
            results = sync_multi_manifest_versions(targets, clean_ver)
            for p_str, updated_ok in results.items():
                if updated_ok:
                    print(f"[OK] Manifiesto {Path(p_str).name} actualizado a {clean_ver}")

            next_ms = compute_next_milestone(clean_ver, scheme)

            config_file = project_root / ".spec" / "config.yaml"
            if config_file.exists():
                cfg_txt = config_file.read_text(encoding="utf-8")
                cfg_txt = re.sub(
                    r'^current_version:\s*["\']?[^"\'\r\n]+["\']?',
                    f'current_version: "{clean_ver}"',
                    cfg_txt,
                    flags=re.MULTILINE,
                )
                cfg_txt = re.sub(
                    r'^current_milestone:\s*["\']?[^"\'\r\n]+["\']?',
                    f'current_milestone: "{next_ms}"',
                    cfg_txt,
                    flags=re.MULTILINE,
                )
                config_file.write_text(cfg_txt, encoding="utf-8")

            current_pending = pending_file.read_text(encoding="utf-8")
            remaining_targets = {
                (v if v.startswith("v") else f"v{v}").lower()
                for v in (
                    m.strip()
                    for m in re.findall(
                        r"-\s*\*\*Versi[oó]n Objetivo:\*\*\s*`?([^\n`]+)`?",
                        current_pending,
                    )
                )
            }
            if target_version.lower() not in remaining_targets:
                ms_pattern = rf"(?m)^##\s+Milestone\s+{re.escape(target_version)}\b[^\r\n]*"
                if re.search(ms_pattern, current_pending):
                    updated_pending = re.sub(
                        ms_pattern,
                        f"## Milestone {next_ms}",
                        current_pending,
                        count=1,
                    )
                    pending_file.write_text(updated_pending, encoding="utf-8")
                    print(f"[OK] Milestone en pending.md actualizado a {next_ms}")

            backlog_index = docs_dir / "backlog" / "index.md"
            if backlog_index.exists():
                idx_txt = backlog_index.read_text(encoding="utf-8")
                idx_txt = re.sub(
                    r"(?m)^(-\s*\*\*Versi[oó]n Actual:\*\*\s*)`?[^`\r\n]+`?",
                    rf"\g<1>`v{clean_ver}`",
                    idx_txt,
                    count=1,
                )
                idx_txt = re.sub(
                    r"(?m)^(-\s*\*\*Milestone Activo:\*\*\s*)`?[^`\r\n]+`?",
                    rf"\g<1>`{next_ms}`",
                    idx_txt,
                    count=1,
                )
                idx_txt = re.sub(
                    r"(?m)^(##\s*Resumen del Milestone Activo\s*\()`?[^)`\r\n]+`?(\))",
                    rf"\g<1>`{next_ms}`\g<2>",
                    idx_txt,
                    count=1,
                )
                backlog_index.write_text(idx_txt, encoding="utf-8")

    # 4. Actualizar grafo Graphify si existe
    if (project_root / "graphify-out").exists():
        try:
            res = subprocess.run(
                ["graphify", "update"],
                cwd=str(project_root),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=30,
            )
            if res.returncode == 0:
                print("[OK] Grafo Graphify actualizado (graphify update).")
        except Exception:
            pass

    return True
