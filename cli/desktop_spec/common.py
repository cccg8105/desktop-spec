import re
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from desktop_spec import __version__

HARNESS_NAMES: Tuple[str, ...] = ("antigravity", "cursor", "claude", "windsurf")

SCHEME_LABELS: Dict[str, str] = {
    "semver": "SemVer 2.0.0",
    "calver": "CalVer (YYYY.MM.MICRO)",
    "sequential": "Sequential Versioning",
}

HARNESS_QUESTION_STRATEGIES: Dict[str, str] = {
    "antigravity": (
        "Pregunta de 2 a 4 decisiones por ronda en el chat colocando primero "
        "la opcion recomendada con trade-offs claros"
    ),
    "claude": (
        "Utiliza `AskUserQuestion` (2 a 4 decisiones por ronda, opcion "
        "`(Recommended)` primero y trade-offs concisos)"
    ),
    "cursor": (
        "Utiliza `AskQuestion` por tarjeta interactiva (2 a 4 decisiones por ronda, "
        "opcion `(Recommended)` primero)"
    ),
    "windsurf": (
        "Presenta de 2 a 4 decisiones con formato `A) (Recomendado) / B) / C)` "
        "y detente en pausa estructurada esperando respuesta"
    ),
}

_ECOSYSTEM_DEFAULT_EXT: Dict[str, str] = {
    "wpf": ".cs",
    "winui3": ".cs",
    "avalonia": ".cs",
    "maui-desktop": ".cs",
    "pyside6": ".py",
    "pyqt6": ".py",
    "flet": ".py",
    "compose-desktop": ".kt",
    "javafx": ".java",
    "rust-native": ".rs",
    "qt-cpp": ".cpp",
}


def slugify(text: str) -> str:
    """Convierte un titulo libre en un slug ASCII compacto para rutas y archivos."""
    normalized = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", normalized.strip().lower()).strip("-")
    return slug[:40] if slug else "feature"


def render_placeholders(text: str, context: Dict[str, str]) -> str:
    """Sustituye placeholders {{KEY}} dentro de una plantilla sin requerir dependencias."""
    rendered = text
    for key, val in context.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", str(val))
    return rendered


def build_doc_context(
    project_name: str,
    profile: Dict[str, Any],
    current_version: str,
    milestone_version: str,
    versioning: str,
    today_iso: str,
    harness: str = "all",
    framework_version: Optional[str] = None,
) -> Dict[str, str]:
    """Construye el diccionario completo con los 22 placeholders congelados de desktop-spec."""
    if harness == "antigravity":
        interview_trigger = "/grill-me"
    elif harness in ("claude", "cursor", "windsurf"):
        interview_trigger = "/desk-grill"
    else:
        interview_trigger = "/grill-me / /desk-grill"

    question_strategy = HARNESS_QUESTION_STRATEGIES.get(
        harness,
        "Formula de 2 a 4 decisiones ordenadas con opcion recomendada primero",
    )

    ecosystem_name = str(profile.get("ecosystem_name") or profile.get("ecosystem") or "avalonia")
    manifest_file = str(
        profile.get("manifest_file")
        or profile.get("version_file")
        or profile.get("manifest")
        or "App.csproj"
    )

    return {
        "PROJECT_NAME": project_name,
        "ECOSYSTEM_NAME": ecosystem_name,
        "ECOSYSTEM_FAMILY": str(profile.get("family", "dotnet")),
        "UI_TOOLKIT": str(profile.get("ui_toolkit", "Avalonia UI")),
        "LANGUAGE_NAME": str(profile.get("language", "C#")),
        "EMBEDDED_DB": str(profile.get("embedded_db", "SQLite (WAL)")),
        "UNIT_TEST_RUNNER": str(profile.get("unit_test_runner", "xUnit")),
        "UI_TEST_RUNNER": str(profile.get("ui_test_runner", "Avalonia.Headless")),
        "MANIFEST_FILE": manifest_file,
        "SRC_DIR": str(profile.get("src_dir", "src")),
        "UI_DIR": str(profile.get("ui_dir", "src/Views")),
        "MODULES_DIR": str(profile.get("modules_dir", "src/Modules")),
        "TEST_PATTERN": str(profile.get("test_pattern", "tests/{module}/{slug}Tests.cs")),
        "VERSIONING_SCHEME": versioning,
        "VERSIONING_SCHEME_LABEL": SCHEME_LABELS.get(versioning, versioning),
        "CURRENT_VERSION": current_version.lstrip("vV"),
        "MILESTONE_VERSION": milestone_version,
        "TODAY": today_iso,
        "RUNTIME_LABEL": str(profile.get("runtime_label", "Avalonia UI (.NET)")),
        "HARNESS_INTERVIEW_TRIGGER": interview_trigger,
        "HARNESS_QUESTION_STRATEGY": question_strategy,
        "FRAMEWORK_VERSION": str(framework_version or __version__),
    }


def _clean_yaml_scalar(raw: str) -> str:
    """Limpia comillas y comentarios YAML en linea fuera de comillas."""
    val = raw.strip()
    if not val:
        return ""
    if val[0] in ('"', "'"):
        quote = val[0]
        end_idx = 1
        while end_idx < len(val):
            if val[end_idx] == quote and val[end_idx - 1] != "\\":
                return val[1:end_idx]
            end_idx += 1
        return val[1:].strip()
    val = re.split(r"\s+#", val, maxsplit=1)[0].strip()
    return val


def read_config_settings(project_root: Path) -> Dict[str, Any]:
    """Lee campos clave desde .spec/config.yaml de desktop-spec usando defaults seguros."""
    default_paths: Dict[str, str] = {
        "user_flows_docs": "docs/functional/user-flows",
        "use_cases_docs": "docs/functional/use-cases",
        "design_docs": "docs/design",
        "technical_docs": "docs/technical",
        "backlog": "docs/backlog",
        "templates": ".spec/templates",
    }
    settings: Dict[str, Any] = {
        "framework": "desktop-spec",
        "version": __version__,
        "project_name": project_root.name or "desktop-app",
        "ecosystem": "avalonia",
        "ecosystem_family": "dotnet",
        "ui_toolkit": "Avalonia UI",
        "language": "C#",
        "embedded_db": "SQLite (WAL)",
        "unit_test_runner": "xUnit",
        "ui_test_runner": "Avalonia.Headless",
        "manifest_file": "App.csproj",
        "src_ext": ".cs",
        "src_dir": "src",
        "ui_dir": "src/Views",
        "modules_dir": "src/Modules",
        "test_pattern": "tests/{module}/{slug}Tests.cs",
        "versioning_scheme": "semver",
        "current_version": "0.1.0",
        "current_milestone": "v0.2.0",
        "manifest_path": "App.csproj",
        "manifest_format": "xml",
        "manifest_field": "Version",
        "version_file": {
            "path": "App.csproj",
            "format": "xml",
            "field": "Version",
        },
        "modules": ["core"],
        "harnesses": ["antigravity"],
        "paths": dict(default_paths),
    }

    cfg = project_root / ".spec" / "config.yaml"
    if not cfg.exists():
        return settings

    raw = cfg.read_text(encoding="utf-8", errors="ignore")
    current_section: Optional[str] = None
    parsed_lists: Dict[str, List[str]] = {}
    parsed_dicts: Dict[str, Dict[str, str]] = {}

    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(line) - len(line.lstrip(" "))
        if indent == 0:
            kv = re.match(r"^([A-Za-z0-9_-]+)\s*:\s*(.*)$", stripped)
            if not kv:
                current_section = None
                continue
            key = kv.group(1)
            raw_val = kv.group(2).strip()
            if raw_val == "":
                current_section = key
                continue
            current_section = None
            val = _clean_yaml_scalar(raw_val)
            if val and "{{" not in val:
                if key in (
                    "framework",
                    "version",
                    "project_name",
                    "versioning_scheme",
                    "current_version",
                    "current_milestone",
                ):
                    settings[key] = val
                elif key == "ecosystem":
                    settings["ecosystem"] = val
            continue

        if current_section:
            if stripped.startswith("- "):
                item = _clean_yaml_scalar(stripped[2:])
                if item and "{{" not in item:
                    parsed_lists.setdefault(current_section, []).append(item)
                continue
            sub_kv = re.match(r"^([A-Za-z0-9_-]+)\s*:\s*(.*)$", stripped)
            if sub_kv:
                sub_key = sub_kv.group(1)
                sub_val = _clean_yaml_scalar(sub_kv.group(2))
                if sub_val and "{{" not in sub_val:
                    parsed_dicts.setdefault(current_section, {})[sub_key] = sub_val

    eco = parsed_dicts.get("ecosystem", {})
    if "name" in eco:
        settings["ecosystem"] = eco["name"]
    if "family" in eco:
        settings["ecosystem_family"] = eco["family"]
    for k in (
        "ui_toolkit",
        "language",
        "embedded_db",
        "unit_test_runner",
        "ui_test_runner",
        "manifest_file",
        "src_dir",
        "ui_dir",
        "modules_dir",
        "test_pattern",
    ):
        if k in eco:
            settings[k] = eco[k]

    vf = parsed_dicts.get("version_file", {})
    if "path" in vf:
        settings["manifest_path"] = vf["path"]
        settings["version_file"]["path"] = vf["path"]
    elif "manifest_file" in eco:
        settings["manifest_path"] = eco["manifest_file"]
        settings["version_file"]["path"] = eco["manifest_file"]
    if "format" in vf:
        settings["manifest_format"] = vf["format"]
        settings["version_file"]["format"] = vf["format"]
    if "field" in vf:
        settings["manifest_field"] = vf["field"]
        settings["version_file"]["field"] = vf["field"]

    if parsed_lists.get("modules"):
        settings["modules"] = parsed_lists["modules"]
    if parsed_lists.get("harnesses"):
        settings["harnesses"] = parsed_lists["harnesses"]

    paths_sec = parsed_dicts.get("paths", {})
    for pk, pv in paths_sec.items():
        settings["paths"][pk] = pv

    eco_name = str(settings["ecosystem"])
    if eco_name in _ECOSYSTEM_DEFAULT_EXT:
        settings["src_ext"] = _ECOSYSTEM_DEFAULT_EXT[eco_name]

    return settings
