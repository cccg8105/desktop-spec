import json
import re
import textwrap
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def locate_framework_asset(subdir: str) -> Optional[Path]:
    """Localiza templates/, harnesses/ o schemas/ en repo editable o paquete instalado."""
    validator_dir = Path(__file__).resolve().parent
    pkg_dir = validator_dir.parent
    repo_root = pkg_dir.parent.parent
    candidates = [
        repo_root / subdir,
        pkg_dir / subdir,
    ]
    for cand in candidates:
        if cand.exists():
            return cand
    return None


def load_json_schema(schema_rel_path: str) -> Optional[Dict[str, Any]]:
    """Carga un esquema JSON desde schemas/ relativo a su raiz."""
    schemas_dir = locate_framework_asset("schemas")
    if not schemas_dir:
        return None
    target = schemas_dir / schema_rel_path
    if not target.exists():
        return None
    try:
        return json.loads(target.read_text(encoding="utf-8"))
    except Exception:
        return None


def _strip_inline_comment(raw: str) -> str:
    """Elimina comentarios YAML # fuera de comillas manteniendo hexadecimales #RRGGBB."""
    val = raw.strip()
    if not val:
        return ""
    if val[0] in ('"', "'"):
        quote = val[0]
        idx = 1
        while idx < len(val):
            if val[idx] == quote and val[idx - 1] != "\\":
                return val[: idx + 1]
            idx += 1
        return val
    return re.split(r"\s+#", val, maxsplit=1)[0].strip()


def _parse_scalar(raw: str) -> Any:
    val = _strip_inline_comment(raw)
    if not val:
        return ""
    if (val.startswith('"') and val.endswith('"')) or (
        val.startswith("'") and val.endswith("'")
    ):
        return val[1:-1]
    low = val.lower()
    if low == "true":
        return True
    if low == "false":
        return False
    if low in ("null", "none", "~"):
        return None
    if val.startswith("[") and val.endswith("]"):
        inner = val[1:-1].strip()
        if not inner:
            return []
        return [_parse_scalar(item) for item in inner.split(",") if item.strip()]
    if re.fullmatch(r"-?\d+", val):
        return int(val)
    if re.fullmatch(r"-?\d+\.\d+", val):
        return float(val)
    return val


def parse_yaml_frontmatter(md_text: str) -> Tuple[Dict[str, Any], str, bool]:
    """Parsea cabecera YAML Frontmatter (escalares, listas, booleanos, enteros y dicts de 1 nivel)."""
    clean_text = md_text.lstrip("\ufeff")
    match = re.match(
        r"\A---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n|$)(.*)", clean_text, re.DOTALL
    )
    if not match:
        return {}, clean_text, False

    raw_yaml = match.group(1)
    body = match.group(2)
    data: Dict[str, Any] = {}
    current_key: Optional[str] = None
    current_type: Optional[str] = None

    for line in raw_yaml.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue

        is_indented = line[0] in (" ", "\t")

        if is_indented and current_key:
            stripped = line.strip()
            list_match = re.match(r"^-\s+(.+)$", stripped)
            if list_match:
                if current_type is None:
                    current_type = "list"
                    data[current_key] = []
                if current_type == "list":
                    data[current_key].append(_parse_scalar(list_match.group(1)))
                continue

            nested_kv = re.match(r"^([A-Za-z0-9_-]+)\s*:\s*(.*)$", stripped)
            if nested_kv:
                if current_type is None:
                    current_type = "dict"
                    data[current_key] = {}
                if current_type == "dict":
                    n_key = nested_kv.group(1)
                    n_val = nested_kv.group(2).strip()
                    data[current_key][n_key] = _parse_scalar(n_val) if n_val else ""
                continue

        kv_match = re.match(r"^([A-Za-z0-9_-]+)\s*:\s*(.*)$", line)
        if kv_match:
            key = kv_match.group(1)
            val_part = _strip_inline_comment(kv_match.group(2))
            if val_part == "":
                current_key = key
                current_type = None
                data[key] = []
            elif val_part.startswith("[") and val_part.endswith("]"):
                data[key] = _parse_scalar(val_part)
                current_key = key
                current_type = "list"
            else:
                data[key] = _parse_scalar(val_part)
                current_key = key
                current_type = None

    return data, body, True


def _matches_single_type(val: Any, expected_type: str) -> bool:
    if expected_type == "object":
        return isinstance(val, dict)
    if expected_type == "array":
        return isinstance(val, list)
    if expected_type == "string":
        return isinstance(val, str)
    if expected_type == "boolean":
        return isinstance(val, bool)
    if expected_type == "integer":
        return isinstance(val, int) and not isinstance(val, bool)
    if expected_type == "number":
        return isinstance(val, (int, float)) and not isinstance(val, bool)
    if expected_type == "null":
        return val is None
    return True


def _check_json_type(val: Any, expected_type: Any) -> bool:
    allowed = expected_type if isinstance(expected_type, list) else [expected_type]
    return any(_matches_single_type(val, t) for t in allowed)


def _schema_allows_null(schema: Dict[str, Any]) -> bool:
    expected = schema.get("type")
    if expected == "null":
        return True
    if isinstance(expected, list):
        return "null" in expected
    return False


def validate_against_schema(
    data: Any, schema: Dict[str, Any], path: str = "$"
) -> List[str]:
    """Validador JSON Schema Draft-07 stdlib con soporte para type string o lista (incluyendo null)."""
    errors: List[str] = []

    expected_type = schema.get("type")
    if expected_type and not _check_json_type(data, expected_type):
        errors.append(
            f"{path}: se esperaba tipo '{expected_type}', se obtuvo '{type(data).__name__}'"
        )
        return errors

    if "enum" in schema and data not in schema["enum"]:
        errors.append(
            f"{path}: valor '{data}' no permitido; valores validos: {schema['enum']}"
        )

    if isinstance(data, str):
        min_len = schema.get("minLength")
        if min_len is not None and len(data.strip()) < min_len:
            errors.append(
                f"{path}: longitud minima requerida {min_len} caracteres (actual: {len(data.strip())})"
            )
        pat = schema.get("pattern")
        if pat and not re.search(pat, data):
            errors.append(f"{path}: '{data}' no cumple patron '{pat}'")

    if isinstance(data, dict):
        props = schema.get("properties", {})
        for req_key in schema.get("required", []):
            allows_null = _schema_allows_null(props.get(req_key, {}))
            if (
                req_key not in data
                or (data[req_key] is None and not allows_null)
                or data[req_key] == ""
            ):
                errors.append(f"{path}.{req_key}: campo obligatorio ausente o vacio")

        for k, subschema in props.items():
            if k in data and data[k] is not None:
                errors.extend(validate_against_schema(data[k], subschema, f"{path}.{k}"))

    if isinstance(data, list) and "items" in schema:
        item_schema = schema["items"]
        for idx, item in enumerate(data):
            errors.extend(validate_against_schema(item, item_schema, f"{path}[{idx}]"))

    return errors


def _extract_markdown_table_rows(section_text: str) -> List[List[str]]:
    rows: List[List[str]] = []
    for line in section_text.splitlines():
        stripped = line.strip()
        if not (stripped.startswith("|") and stripped.endswith("|")):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if all(re.fullmatch(r":?-+:?", c) for c in cells if c):
            continue
        rows.append(cells)
    return rows[1:] if len(rows) > 1 else []


def _extract_sub_bullets(section_text: str, bullet_pattern: str) -> List[str]:
    """Extrae items indentados debajo de un bullet encabezado dado."""
    items: List[str] = []
    lines = section_text.splitlines()
    capturing = False
    header_re = re.compile(bullet_pattern, re.IGNORECASE)
    for line in lines:
        stripped = line.strip()
        if not capturing:
            if header_re.match(stripped):
                capturing = True
            continue
        if not stripped:
            if items:
                break
            continue
        if not line[0].isspace() and stripped.startswith(("- ", "#", "---")):
            break
        if stripped.startswith("- "):
            item_text = stripped[2:].strip()
            if item_text and item_text.strip("` ").upper() != "N/A":
                items.append(item_text)
    return items


def extract_use_case_data(md_text: str) -> Tuple[Dict[str, Any], bool]:
    """Extrae metadatos y secciones de UC-*.md para validar schemas/use-case.schema.json."""
    fm, body, has_fm = parse_yaml_frontmatter(md_text)

    h1_match = re.search(r"^#\s+(UC-[A-Z0-9]+-[0-9]+)\s*:\s*(.+)$", body, re.MULTILINE)
    uc_id = fm.get("id") or (h1_match.group(1).strip() if h1_match else "")
    title = fm.get("title") or (h1_match.group(2).strip() if h1_match else "")

    mod_match = re.search(r"-\s*\*\*M[oó]dulo:\*\*\s*`?([^\n`]+)`?", body)
    actor_match = re.search(r"-\s*\*\*Actor Principal:\*\*\s*`?([^\n`]+)`?", body)
    trig_match = re.search(
        r"-\s*\*\*Disparador(?:\s*\(Trigger\))?:\*\*\s*`?([^\n`]+)`?", body
    )
    mermaid_match = re.search(r"```mermaid\s*\r?\n(.*?)\r?\n[ \t]*```", body, re.DOTALL)

    preconditions: List[str] = []
    if isinstance(fm.get("preconditions"), list):
        preconditions = [str(p).strip() for p in fm["preconditions"] if str(p).strip()]
    else:
        preconditions = _extract_sub_bullets(body, r"^-\s*\*\*Precondiciones:\*\*")

    inputs_list: List[Dict[str, Any]] = []
    inputs_sec = re.search(
        r"###\s*Inputs Requeridos:(.*?)(?=###|\n---|\n##|\Z)", body, re.DOTALL
    )
    if inputs_sec:
        for row in _extract_markdown_table_rows(inputs_sec.group(1)):
            if len(row) >= 3:
                req_flag = row[2].strip().lower() in ("si", "sí", "yes", "true")
                inputs_list.append(
                    {
                        "name": row[0].strip("` "),
                        "type": row[1].strip("` "),
                        "required": req_flag,
                        "validation": row[3].strip() if len(row) >= 4 else "",
                    }
                )

    outputs_list: List[Dict[str, str]] = []
    outputs_sec = re.search(
        r"###\s*Output Esperado:(.*?)(?=###|\n---|\n##|\Z)", body, re.DOTALL
    )
    if outputs_sec:
        for row in _extract_markdown_table_rows(outputs_sec.group(1)):
            if len(row) >= 2:
                outputs_list.append(
                    {
                        "name": row[0].strip("` "),
                        "type": row[1].strip("` "),
                        "description": row[2].strip() if len(row) >= 3 else "",
                    }
                )

    br_matches = re.findall(
        r"-\s*\*\*\[(BR-[0-9]{2,})\]\s*([^:*]+):\*\*(.*?)(?=-\s*\*\*\[BR-|\n---|\n##|\Z)",
        body,
        re.DOTALL,
    )
    rules_list: List[Dict[str, Any]] = []
    for br_id, br_name, br_body in br_matches:
        desc_match = re.search(r"-\s*\*\*Descripci[oó]n:\*\*\s*(.+)", br_body)
        desc = desc_match.group(1).strip() if desc_match else br_name.strip()
        ocl_match = re.search(r"```ocl\s*\r?\n(.*?)\r?\n[ \t]*```", br_body, re.DOTALL)
        rule_obj: Dict[str, Any] = {
            "id": br_id.strip(),
            "name": br_name.strip(),
            "description": desc,
        }
        if ocl_match:
            rule_obj["ocl_contract"] = textwrap.dedent(ocl_match.group(1)).strip()
        rules_list.append(rule_obj)

    side_effects: Dict[str, List[str]] = {}
    if isinstance(fm.get("side_effects"), dict):
        for k, v in fm["side_effects"].items():
            if isinstance(v, list):
                side_effects[str(k)] = [str(x).strip() for x in v if str(x).strip()]
    else:
        se_sec = re.search(
            r"##\s*(?:5\.\s*)?Efectos Secundarios[^\n]*\n(.*?)(?=\n---|\n##|\Z)",
            body,
            re.DOTALL,
        )
        if se_sec:
            se_text = se_sec.group(1)
            se_patterns = {
                "local_database": r"^-\s*\*\*(?:Base de Datos Local|.*local_database.*):\*\*",
                "local_files": r"^-\s*\*\*(?:Archivos Locales|.*local_files.*):\*\*",
                "os_keyring": r"^-\s*\*\*(?:OS Keyring|.*os_keyring.*):\*\*",
                "internal_domain_events": r"^-\s*\*\*(?:Bus de Eventos Interno|Eventos Internos|.*internal_domain_events.*):\*\*",
            }
            for key, pat in se_patterns.items():
                extracted = _extract_sub_bullets(se_text, pat)
                if extracted:
                    side_effects[key] = extracted

    data: Dict[str, Any] = {
        "id": str(uc_id),
        "title": str(title),
        "module": str(fm.get("module") or (mod_match.group(1).strip() if mod_match else "")),
        "actor": str(fm.get("actor") or (actor_match.group(1).strip() if actor_match else "")),
        "status": str(fm.get("status", "Activo")),
        "trigger": str(fm.get("trigger") or (trig_match.group(1).strip() if trig_match else "")),
        "process_diagram_mermaid": mermaid_match.group(1).strip() if mermaid_match else "",
        "inputs": inputs_list,
        "outputs": outputs_list,
        "business_rules": rules_list,
    }
    if "ocl_applied" in fm:
        data["ocl_applied"] = fm["ocl_applied"]
    if preconditions:
        data["preconditions"] = preconditions
    if side_effects:
        data["side_effects"] = side_effects

    return data, has_fm


def extract_user_flow_data(md_text: str) -> Tuple[Dict[str, Any], bool]:
    """Extrae metadatos y secciones de UF-*.md para validar schemas/user-flow.schema.json."""
    fm, body, has_fm = parse_yaml_frontmatter(md_text)

    h1_match = re.search(r"^#\s+(UF-[A-Z0-9]+-[0-9]+)\s*:\s*(.+)$", body, re.MULTILINE)
    uf_id = fm.get("id") or (h1_match.group(1).strip() if h1_match else "")
    title = fm.get("title") or (h1_match.group(2).strip() if h1_match else "")

    mod_match = re.search(r"-\s*\*\*M[oó]dulo:\*\*\s*`?([^\n`]+)`?", body)
    actor_match = re.search(r"-\s*\*\*Actor Principal:\*\*\s*`?([^\n`]+)`?", body)
    win_match = re.search(
        r"-\s*\*\*Ventana(?:\s*/\s*Vista)?\s*Destino:\*\*\s*`?([^`\n(]+)`?", body
    )
    entry_match = re.search(
        r"-\s*\*\*(?:Disparador de Entrada|Disparador(?:\s*\(Trigger\))?):\*\*\s*`?([^\n`]+)`?",
        body,
    )
    shortcut_match = re.search(
        r"-\s*\*\*Atajo(?:\s*Multiplataforma)?:\*\*\s*`?([^\n`]+)`?", body
    )
    uc_match = re.search(
        r"-\s*\*\*Caso de Uso Delegado:\*\*\s*`?(UC-[A-Z0-9]+-[0-9]+|N/A)`?", body
    )
    mermaid_match = re.search(r"```mermaid\s*\r?\n(.*?)\r?\n[ \t]*```", body, re.DOTALL)

    inputs_list: List[Dict[str, Any]] = []
    inputs_sec = re.search(
        r"###\s*Eventos\s*/\s*Entradas del Usuario:(.*?)(?=###|\n---|\n##|\Z)",
        body,
        re.DOTALL,
    )
    if inputs_sec:
        for row in _extract_markdown_table_rows(inputs_sec.group(1)):
            if len(row) >= 3:
                req_flag = row[2].strip().lower() in ("si", "sí", "yes", "true")
                inputs_list.append(
                    {
                        "name": row[0].strip("` "),
                        "type": row[1].strip("` "),
                        "required": req_flag,
                        "validation": row[3].strip() if len(row) >= 4 else "",
                    }
                )

    outputs_list: List[Dict[str, str]] = []
    outputs_sec = re.search(
        r"###\s*Salidas Visuales y Efectos:(.*?)(?=###|\n---|\n##|\Z)",
        body,
        re.DOTALL,
    )
    if outputs_sec:
        for row in _extract_markdown_table_rows(outputs_sec.group(1)):
            if len(row) >= 3:
                outputs_list.append(
                    {
                        "element": row[0].strip("` "),
                        "condition": row[1].strip("` "),
                        "behavior": row[2].strip(),
                    }
                )

    states_list: List[Dict[str, str]] = []
    states_sec = re.search(
        r"##\s*(?:4\.\s*)?Matriz de Estados de Interfaz[^\n]*\n(.*?)(?=\n---|\n##|\Z)",
        body,
        re.DOTALL,
    )
    if states_sec:
        for row in _extract_markdown_table_rows(states_sec.group(1)):
            if len(row) >= 3:
                state_obj: Dict[str, str] = {
                    "state": row[0].strip("*` "),
                    "trigger": row[1].strip(),
                    "feedback": row[2].strip(),
                }
                if len(row) >= 4 and row[3].strip():
                    state_obj["recovery"] = row[3].strip()
                states_list.append(state_obj)

    fm_a11y = fm.get("accessibility") if isinstance(fm.get("accessibility"), dict) else {}
    a11y_sec_match = re.search(
        r"##\s*(?:6\.\s*)?Accesibilidad Nativa[^\n]*\n(.*?)(?=\n---|\n##|\Z)",
        body,
        re.DOTALL,
    )
    a11y_body = a11y_sec_match.group(1) if a11y_sec_match else body

    focus_m = re.search(r"-\s*\*\*Foco Inicial[^:]*:\*\*\s*(.+)", a11y_body)
    roles_m = re.search(r"-\s*\*\*Roles[^:]*:\*\*\s*(.+)", a11y_body)
    kbd_m = re.search(r"-\s*\*\*Navegaci[oó]n por Teclado:\*\*\s*(.+)", a11y_body)

    accessibility: Dict[str, str] = {
        "focus_management": str(
            fm_a11y.get("focus_management") or (focus_m.group(1).strip() if focus_m else "")
        ),
        "os_accessibility_roles": str(
            fm_a11y.get("os_accessibility_roles") or (roles_m.group(1).strip() if roles_m else "")
        ),
        "keyboard_navigation": str(
            fm_a11y.get("keyboard_navigation") or (kbd_m.group(1).strip() if kbd_m else "")
        ),
    }

    data: Dict[str, Any] = {
        "id": str(uf_id),
        "title": str(title),
        "module": str(fm.get("module") or (mod_match.group(1).strip() if mod_match else "")),
        "actor": str(fm.get("actor") or (actor_match.group(1).strip() if actor_match else "")),
        "window_target": str(
            fm.get("window_target") or (win_match.group(1).strip() if win_match else "")
        ),
        "entry_trigger": str(
            fm.get("entry_trigger") or (entry_match.group(1).strip() if entry_match else "")
        ),
        "status": str(fm.get("status", "Activo")),
        "flow_diagram_mermaid": mermaid_match.group(1).strip() if mermaid_match else "",
        "ui_states": states_list,
        "accessibility": accessibility,
    }

    invokes_val = fm.get("invokes_use_case") or (uc_match.group(1).strip() if uc_match else "")
    if invokes_val:
        data["invokes_use_case"] = str(invokes_val)

    shortcut_val = fm.get("shortcut") or (shortcut_match.group(1).strip() if shortcut_match else "")
    if shortcut_val:
        data["shortcut"] = str(shortcut_val)

    if "fsm_required" in fm:
        data["fsm_required"] = fm["fsm_required"]

    if isinstance(fm.get("window_geometry"), dict):
        data["window_geometry"] = fm["window_geometry"]

    if inputs_list:
        data["user_inputs"] = inputs_list
    if outputs_list:
        data["visual_outputs"] = outputs_list

    return data, has_fm


def _parse_ref_list(raw_value: str) -> List[str]:
    """Extrae rutas o identificadores desde spans `...` o lista separada por comas, limpiando N/A."""
    raw = raw_value.strip()
    if not raw or raw.upper().startswith("N/A"):
        return []
    code_spans = re.findall(r"`([^`]+)`", raw)
    candidates = code_spans if code_spans else raw.split(",")
    cleaned: List[str] = []
    for item in candidates:
        token = item.strip()
        if not token or token.upper() == "N/A" or token.upper().startswith(("N/A ", "N/A(")):
            continue
        cleaned.append(token)
    return cleaned


def extract_requirement_data(full_req_block: str) -> Dict[str, Any]:
    """Convierte un bloque ### [REQ-DESK-...] de pending.md al formato de requirement.schema.json."""
    header_match = re.search(r"###\s*\[(REQ-[^\]]+)\]\s*(.+)", full_req_block)
    req_id = header_match.group(1).strip() if header_match else ""
    title = header_match.group(2).strip() if header_match else ""

    prio_match = re.search(r"-\s*\*\*Prioridad:\*\*\s*(P[123])\b", full_req_block)
    priority = prio_match.group(1).strip() if prio_match else ""

    impact_match = re.search(r"-\s*\*\*Tipo:\*\*\s*([^\n]+)", full_req_block)
    raw_impact = impact_match.group(1).strip() if impact_match else ""
    imp_token = re.search(r"\b(MAJOR|MINOR|PATCH)\b", raw_impact)
    impact_type = imp_token.group(1).strip() if imp_token else ""
    track = (
        "FAST_TRACK"
        if ("fast-track" in raw_impact.lower() or impact_type == "PATCH")
        else "FULL"
    )

    scope_match = re.search(r"-\s*\*\*Alcance[^:]*:\*\*\s*([^\n]+)", full_req_block)
    raw_scope = scope_match.group(1).strip() if scope_match else ""
    scope_token = re.search(
        r"\b(ui-only|domain-only|full-module|packaging-infra)\b", raw_scope
    )
    scope = scope_token.group(1) if scope_token else raw_scope.strip("` ")

    ver_match = re.search(r"-\s*\*\*Versi[oó]n Objetivo:\*\*\s*`?([^\n`]+)`?", full_req_block)
    target_version = ver_match.group(1).strip() if ver_match else ""

    uf_match = re.search(r"-\s*\*\*Flujos UX[^:]*:\*\*\s*(.+)", full_req_block)
    user_flows = _parse_ref_list(uf_match.group(1)) if uf_match else []

    uc_match = re.search(r"-\s*\*\*Casos de Uso[^:]*:\*\*\s*(.+)", full_req_block)
    use_cases = _parse_ref_list(uc_match.group(1)) if uc_match else []

    tech_match = re.search(r"-\s*\*\*Referencias? T[eé]cnicas?:\*\*\s*(.+)", full_req_block)
    technical_refs = _parse_ref_list(tech_match.group(1)) if tech_match else []

    mods_match = re.search(r"-\s*\*\*M[oó]dulos Afectados:\*\*\s*(.+)", full_req_block)
    affected_modules = _parse_ref_list(mods_match.group(1)) if mods_match else []

    artifacts: List[Dict[str, str]] = []
    for path_str, action_str in re.findall(
        r"-\s*`([^`]+)`\s*\[(NEW|MODIFY|DELETE)\]", full_req_block
    ):
        artifacts.append({"path": path_str.strip(), "action": action_str.strip()})

    restrictions: List[str] = []
    rest_sec = re.search(
        r"-\s*\*\*Restricciones:\*\*(.*?)(?=####|\Z)", full_req_block, re.DOTALL
    )
    if rest_sec:
        for line in rest_sec.group(1).splitlines():
            cleaned = line.strip()
            if cleaned.startswith("- "):
                restrictions.append(cleaned[2:].strip())
            elif cleaned:
                restrictions.append(cleaned)

    criteria: List[Dict[str, Any]] = []
    crit_sec = re.search(
        r"####\s*Criterios de Aceptaci[oó]n:(.*)", full_req_block, re.DOTALL
    )
    if crit_sec:
        for state_char, desc in re.findall(r"-\s*\[([ xX])\]\s*(.+)", crit_sec.group(1)):
            criteria.append(
                {
                    "description": desc.strip(),
                    "completed": state_char.lower() == "x",
                }
            )

    return {
        "id": req_id,
        "title": title,
        "priority": priority,
        "impact_type": impact_type,
        "scope": scope,
        "track": track,
        "target_version": target_version,
        "references": {
            "user_flows": user_flows,
            "use_cases": use_cases,
            "technical": technical_refs,
        },
        "boundaries": {
            "affected_modules": affected_modules,
            "artifacts": artifacts,
            "restrictions": restrictions,
        },
        "acceptance_criteria": criteria,
    }


def extract_design_tokens_summary(md_text: str) -> Dict[str, Any]:
    """Extrae frontmatter, colores semanticos (4 o 5 columnas) y tipografia de tokens-and-themes.md."""
    fm, body, has_fm = parse_yaml_frontmatter(md_text)
    colors: List[Dict[str, Any]] = []
    color_sec = re.search(
        r"##\s*(?:1\.\s*)?Colores Sem[aá]nticos[^\n]*\n(.*?)(?=\n---|\n##|\Z)",
        body,
        re.DOTALL,
    )
    if color_sec:
        for row in _extract_markdown_table_rows(color_sec.group(1)):
            if len(row) >= 5:
                raw_hc = row[3].strip("` ")
                hc_val: Optional[str] = (
                    None
                    if not raw_hc or raw_hc.upper() in ("N/A", "NULL", "-", "~")
                    else raw_hc
                )
                colors.append(
                    {
                        "token": row[0].strip("` "),
                        "light_hex": row[1].strip("` "),
                        "dark_hex": row[2].strip("` "),
                        "high_contrast_hex": hc_val,
                        "role": row[4].strip(),
                    }
                )
            elif len(row) == 4:
                colors.append(
                    {
                        "token": row[0].strip("` "),
                        "light_hex": row[1].strip("` "),
                        "dark_hex": row[2].strip("` "),
                        "role": row[3].strip(),
                    }
                )

    disp_m = re.search(r"-\s*\*\*Display(?:\s*/\s*UI)?:\*\*\s*(.+)", body)
    ui_m = re.search(r"-\s*\*\*UI:\*\*\s*(.+)", body)
    mono_m = re.search(r"-\s*\*\*Monospace:\*\*\s*(.+)", body)

    display_font = disp_m.group(1).strip() if disp_m else ""
    ui_font = ui_m.group(1).strip() if ui_m else display_font
    mono_font = mono_m.group(1).strip() if mono_m else ""

    summary: Dict[str, Any] = {
        "has_fm": has_fm,
        "artifact_type": str(fm.get("artifact_type", "")),
        "theme_modes": fm.get("theme_modes") if isinstance(fm.get("theme_modes"), list) else [],
        "density_modes": fm.get("density_modes") if isinstance(fm.get("density_modes"), list) else [],
        "window_chrome": (
            fm["window_chrome"]
            if isinstance(fm.get("window_chrome"), dict) and fm.get("window_chrome")
            else None
        ),
        "semantic_colors": colors,
        "display_font": display_font,
        "ui_font": ui_font,
        "mono_font": mono_font,
        "typography": {
            "display_font": display_font,
            "ui_font": ui_font,
            "mono_font": mono_font,
        },
    }
    return summary


def count_rolling_history_rows(md_text: str) -> int:
    """Cuenta las filas de datos en '## Historial de Revisiones' (limite Rolling Window: 3)."""
    match = re.search(
        r"##\s*Historial de Revisiones.*?\n(.*?)(?=\n##\s|\n>\s*\*Nota:|\Z)",
        md_text,
        re.DOTALL,
    )
    if not match:
        return 0
    return len(_extract_markdown_table_rows(match.group(1)))


W3C_DTCG_VALID_TYPES = {
    "color",
    "dimension",
    "fontFamily",
    "fontWeight",
    "duration",
    "cubicBezier",
    "number",
    "shadow",
    "typography",
    "border",
    "transition",
    "gradient",
}

_W3C_COLOR_RE = re.compile(
    r"^(?:#(?:[0-9A-Fa-f]{3}|[0-9A-Fa-f]{6}|[0-9A-Fa-f]{8})|\{[a-zA-Z0-9._-]+\})$"
)


def export_w3c_design_tokens(md_text: str) -> Dict[str, Any]:
    """Exporta tokens desktop claro/oscuro/alto-contraste y tipografia a formato W3C DTCG."""
    summary = extract_design_tokens_summary(md_text)
    color_group: Dict[str, Any] = {}

    for item in summary.get("semantic_colors", []):
        raw_token = str(item.get("token", "")).strip("` ").lstrip("-")
        if not raw_token:
            continue
        key_name = (
            raw_token[len("color-") :]
            if raw_token.startswith("color-") and len(raw_token) > len("color-")
            else raw_token
        )
        light_hex = str(item.get("light_hex", "")).strip("` ")
        dark_hex = str(item.get("dark_hex", "")).strip("` ")
        hc_hex = item.get("high_contrast_hex")

        token_node: Dict[str, Any] = {
            "$type": "color",
            "$value": light_hex,
        }
        role = str(item.get("role", "")).strip()
        if role:
            token_node["$description"] = role

        mode_ext: Dict[str, str] = {}
        if light_hex:
            mode_ext["light"] = light_hex
        if dark_hex:
            mode_ext["dark"] = dark_hex
        if isinstance(hc_hex, str) and hc_hex.strip():
            mode_ext["high_contrast"] = hc_hex.strip()
        if mode_ext:
            token_node["$extensions"] = {"mode": mode_ext}

        color_group[key_name] = token_node

    payload: Dict[str, Any] = {
        "$description": "W3C DTCG Design Tokens exported by desktop-spec (dspec sync --export-tokens)",
        "color": color_group,
    }

    disp = str(summary.get("display_font", "")).strip("` ")
    ui = str(summary.get("ui_font", "")).strip("` ")
    mono = str(summary.get("mono_font", "")).strip("` ")
    font_family: Dict[str, Any] = {}
    if disp:
        font_family["display"] = {"$type": "fontFamily", "$value": disp}
    if ui:
        font_family["ui"] = {"$type": "fontFamily", "$value": ui}
    if mono:
        font_family["mono"] = {"$type": "fontFamily", "$value": mono}
    if font_family:
        payload["typography"] = {"fontFamily": font_family}

    return payload


def validate_w3c_tokens_dict(
    data: Any, label: str = "design.tokens.json"
) -> List[str]:
    """Valida la estructura de un diccionario *.tokens.json contra reglas del formato W3C DTCG."""
    errors: List[str] = []
    if not isinstance(data, dict) or not data:
        return [
            f"{label}: debe ser un objeto JSON no vacio con grupos de tokens W3C DTCG"
        ]

    token_count = 0

    def _walk(node: Any, path: str, inherited_type: Optional[str]) -> None:
        nonlocal token_count
        if not isinstance(node, dict):
            errors.append(f"{label}#{path}: se esperaba un objeto token o grupo DTCG")
            return

        explicit_type = node.get("$type")
        if explicit_type is not None:
            if not isinstance(explicit_type, str) or explicit_type not in W3C_DTCG_VALID_TYPES:
                errors.append(
                    f"{label}#{path}: '$type' '{explicit_type}' no pertenece a los tipos W3C DTCG soportados"
                )
        eff_type = explicit_type if isinstance(explicit_type, str) else inherited_type

        if "$value" in node:
            token_count += 1
            if not eff_type or eff_type not in W3C_DTCG_VALID_TYPES:
                errors.append(
                    f"{label}#{path}: token con '$value' debe definir o heredar un '$type' valido"
                )
            val = node["$value"]
            if val is None or val == "":
                errors.append(f"{label}#{path}: '$value' no puede estar vacio")
            elif eff_type == "color":
                if not isinstance(val, str) or not _W3C_COLOR_RE.match(val.strip()):
                    errors.append(
                        f"{label}#{path}: valor de color '{val}' debe ser hex (#RRGGBB) o alias {{grupo.token}}"
                    )
                ext = node.get("$extensions")
                if isinstance(ext, dict) and isinstance(ext.get("mode"), dict):
                    for mode_name, mode_val in ext["mode"].items():
                        if not isinstance(mode_val, str) or not _W3C_COLOR_RE.match(
                            mode_val.strip()
                        ):
                            errors.append(
                                f"{label}#{path}.$extensions.mode.{mode_name}: color '{mode_val}' invalido"
                            )
            non_meta_children = [k for k in node if not k.startswith("$")]
            if non_meta_children:
                errors.append(
                    f"{label}#{path}: un token hoja con '$value' no puede mezclar sub-tokens ({', '.join(non_meta_children)})"
                )
            return

        for key, child in node.items():
            if key.startswith("$"):
                continue
            child_path = f"{path}.{key}" if path else key
            _walk(child, child_path, eff_type)

    _walk(data, "", None)
    if token_count == 0 and not errors:
        errors.append(f"{label}: no contiene ningun token W3C DTCG valido con '$value'")
    return errors
