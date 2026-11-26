"""Extractor y actualizador multi-manifiesto de versiones para desktop-spec."""

import datetime
import json
import re
from pathlib import Path
from typing import List, Optional, Tuple, Union


_XML_IGNORED_BLOCKS = (
    r"<!--.*?-->",
    r"<parent>.*?</parent>",
    r"<dependencies>.*?</dependencies>",
    r"<dependencyManagement>.*?</dependencyManagement>",
    r"<build>.*?</build>",
    r"<plugins>.*?</plugins>",
    r"<reporting>.*?</reporting>",
    r"<profiles>.*?</profiles>",
)

_TOML_SECTION_RE = re.compile(
    r"(?m)^\[(?:project|package|tool\.poetry|workspace\.package)\][ \t]*\r?\n(.*?)(?=\n\[|\Z)",
    re.DOTALL,
)

_CFG_METADATA_RE = re.compile(
    r"(?m)^\[metadata\][ \t]*\r?\n(.*?)(?=\n\[|\Z)",
    re.DOTALL,
)

_CMAKE_PROJECT_RE = re.compile(
    r"(?im)^[ \t]*project\s*\(([^)]*)\)",
    re.DOTALL,
)


def _ignored_xml_spans(content: str) -> List[Tuple[int, int]]:
    spans: List[Tuple[int, int]] = []
    for block_pat in _XML_IGNORED_BLOCKS:
        for match in re.finditer(block_pat, content, re.DOTALL):
            spans.append((match.start(), match.end()))
    return spans


def _in_spans(pos: int, spans: List[Tuple[int, int]]) -> bool:
    return any(start <= pos < end for start, end in spans)


def _find_xml_version_match(content: str) -> Optional[re.Match]:
    ignored = _ignored_xml_spans(content)
    version_re = re.compile(r"<([vV]ersion)>\s*([^<\s][^<]*?)\s*</\1>")
    for match in version_re.finditer(content):
        if not _in_spans(match.start(), ignored):
            return match

    maui_re = re.compile(r"<(ApplicationDisplayVersion)>\s*([^<\s][^<]*?)\s*</\1>")
    for match in maui_re.finditer(content):
        if not _in_spans(match.start(), ignored):
            return match

    comment_spans = [
        (m.start(), m.end()) for m in re.finditer(r"<!--.*?-->", content, re.DOTALL)
    ]
    for match in version_re.finditer(content):
        if not _in_spans(match.start(), comment_spans):
            return match
    return None


def extract_version(manifest_path: Union[str, Path], file_format: str) -> Optional[str]:
    """Extrae la version actual desde el archivo manifiesto segun su formato."""
    path = Path(manifest_path)
    if not path.exists() or not path.is_file():
        return None

    content = path.read_text(encoding="utf-8")

    if file_format == "plain":
        for line in content.splitlines():
            cleaned = line.strip()
            if cleaned and not cleaned.startswith("#"):
                return cleaned.lstrip("vV")
        return None

    if file_format == "json":
        try:
            data = json.loads(content)
            val = data.get("version")
            return str(val).strip().lstrip("vV") if val else None
        except Exception:
            return None

    if file_format == "toml":
        section_match = _TOML_SECTION_RE.search(content)
        target = section_match.group(1) if section_match else content
        match = re.search(
            r'(?m)^[ \t]*version[ \t]*=[ \t]*["\']([^"\']+)["\']', target
        )
        if match:
            return match.group(1).strip().lstrip("vV")
        return None

    if file_format == "xml":
        match = _find_xml_version_match(content)
        if match:
            return match.group(2).strip().lstrip("vV")
        return None

    if file_format == "cfg":
        section_match = _CFG_METADATA_RE.search(content)
        target = section_match.group(1) if section_match else content
        match = re.search(
            r'(?m)^[ \t]*version[ \t]*=[ \t]*["\']?([^\s#"\']+)["\']?', target
        )
        if match:
            return match.group(1).strip().lstrip("vV")
        return None

    if file_format == "gradle":
        match = re.search(
            r'(?m)^[ \t]*version[ \t]*(?:=[ \t]*|[ \t]+)["\']([^"\']+)["\']',
            content,
        )
        if match:
            return match.group(1).strip().lstrip("vV")
        return None

    if file_format == "cmake":
        for proj_match in _CMAKE_PROJECT_RE.finditer(content):
            ver_match = re.search(
                r'\bVERSION\s+["\']?([^\s)"\']+)["\']?', proj_match.group(1)
            )
            if ver_match:
                return ver_match.group(1).strip().lstrip("vV")
        return None

    if file_format == "yaml":
        match = re.search(
            r'(?m)^[ \t]*version[ \t]*:[ \t]*["\']?([0-9]+\.[0-9]+\.[0-9]+(?:[+-][^\s#"\']+)?)["\']?',
            content,
        )
        if match:
            return match.group(1).strip().lstrip("vV")
        return None

    generic_match = re.search(
        r'version["\']?\s*[:=]\s*["\']([^"\']+)["\']', content, re.IGNORECASE
    )
    if generic_match:
        return generic_match.group(1).strip().lstrip("vV")

    return None


def _replace_in_slice(
    content: str, start: int, end: int, pattern: str, replacement: str
) -> Optional[str]:
    segment = content[start:end]
    new_segment, count = re.subn(pattern, replacement, segment, count=1)
    if count == 0:
        return None
    return content[:start] + new_segment + content[end:]


def update_version(
    manifest_path: Union[str, Path], file_format: str, new_version: str
) -> bool:
    """Actualiza la version en el archivo manifiesto preservando formato y comentarios."""
    path = Path(manifest_path)
    clean_ver = new_version.strip().lstrip("vV")
    if not clean_ver:
        return False

    if file_format == "plain":
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"{clean_ver}\n", encoding="utf-8")
        return True

    if not path.exists() or not path.is_file():
        return False

    content = path.read_text(encoding="utf-8")

    if file_format == "json":
        try:
            data = json.loads(content)
            data["version"] = clean_ver
            path.write_text(
                json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            return True
        except Exception:
            return False

    if file_format == "toml":
        quoted_pat = r'(?m)^([ \t]*version[ \t]*=[ \t]*["\'])[^"\']+(["\'])'
        section_match = _TOML_SECTION_RE.search(content)
        if section_match:
            updated = _replace_in_slice(
                content,
                section_match.start(1),
                section_match.end(1),
                quoted_pat,
                rf"\g<1>{clean_ver}\g<2>",
            )
            if updated is not None:
                path.write_text(updated, encoding="utf-8")
                return True
        if re.search(quoted_pat, content):
            new_content = re.sub(
                quoted_pat, rf"\g<1>{clean_ver}\g<2>", content, count=1
            )
            path.write_text(new_content, encoding="utf-8")
            return True
        return False

    if file_format == "cfg":
        quoted_pat = r'(?m)^([ \t]*version[ \t]*=[ \t]*["\'])[^"\']+(["\'])'
        unquoted_pat = r'(?m)^([ \t]*version[ \t]*=[ \t]*)([^\s#"\']+)'
        section_match = _CFG_METADATA_RE.search(content)
        start, end = (
            (section_match.start(1), section_match.end(1))
            if section_match
            else (0, len(content))
        )
        for pat, repl in (
            (quoted_pat, rf"\g<1>{clean_ver}\g<2>"),
            (unquoted_pat, rf"\g<1>{clean_ver}"),
        ):
            updated = _replace_in_slice(content, start, end, pat, repl)
            if updated is not None:
                path.write_text(updated, encoding="utf-8")
                return True
        return False

    if file_format == "xml":
        match = _find_xml_version_match(content)
        if match:
            new_content = (
                content[: match.start(2)] + clean_ver + content[match.end(2) :]
            )
            path.write_text(new_content, encoding="utf-8")
            return True
        return False

    if file_format == "gradle":
        pattern = r'(?m)^([ \t]*version[ \t]*(?:=[ \t]*|[ \t]+)["\'])[^"\']+(["\'])'
        if re.search(pattern, content):
            new_content = re.sub(
                pattern, rf"\g<1>{clean_ver}\g<2>", content, count=1
            )
            path.write_text(new_content, encoding="utf-8")
            return True
        return False

    if file_format == "cmake":
        for proj_match in _CMAKE_PROJECT_RE.finditer(content):
            args_text = proj_match.group(1)
            ver_match = re.search(
                r'\bVERSION\s+(["\']?)([^\s)"\']+)(["\']?)', args_text
            )
            if ver_match:
                v_start = proj_match.start(1) + ver_match.start(2)
                v_end = proj_match.start(1) + ver_match.end(2)
                new_content = content[:v_start] + clean_ver + content[v_end:]
                path.write_text(new_content, encoding="utf-8")
                return True
        return False

    if file_format == "yaml":
        pattern = r'(?m)^([ \t]*version[ \t]*:[ \t]*["\']?)([0-9]+\.[0-9]+\.[0-9]+(?:[+-][^\s#"\']+)?)([ \t]*["\']?)'
        if re.search(pattern, content):
            new_content = re.sub(
                pattern, rf"\g<1>{clean_ver}\g<3>", content, count=1
            )
            path.write_text(new_content, encoding="utf-8")
            return True
        return False

    fallback_pattern = r'(version["\']?\s*[:=]\s*["\'])[^"\']+(["\'])'
    if re.search(fallback_pattern, content, re.IGNORECASE):
        new_content = re.sub(
            fallback_pattern,
            rf"\g<1>{clean_ver}\g<2>",
            content,
            count=1,
            flags=re.IGNORECASE,
        )
        path.write_text(new_content, encoding="utf-8")
        return True

    return False


def _infer_manifest_format(path: Path) -> str:
    name = path.name.lower()
    if name.endswith(".json"):
        return "json"
    if name.endswith(".toml"):
        return "toml"
    if name.endswith((".yaml", ".yml")):
        return "yaml"
    if name.endswith((".csproj", ".xml")):
        return "xml"
    if name == "cmakelists.txt":
        return "cmake"
    if name.startswith("build.gradle"):
        return "gradle"
    if name == "setup.cfg":
        return "cfg"
    return "regex"


def sync_multi_manifest_versions(
    paths: List[Union[str, Path, Tuple[Union[str, Path], str]]],
    new_version: str,
) -> dict:
    """Sincroniza la version en multiples manifiestos de proyectos hibridos."""
    results = {}
    for item in paths:
        if isinstance(item, tuple):
            raw_path, file_format = item
        else:
            raw_path = item
            file_format = _infer_manifest_format(Path(raw_path))
        p = Path(raw_path)
        results[str(p)] = update_version(p, file_format, new_version)
    return results


def parse_version_tuple(version_str: str) -> Tuple[int, ...]:
    """Convierte 'v1.2.3-beta', '2026.11.1' o '4' en tupla numerica comparable."""
    cleaned = version_str.strip().lstrip("vV")
    core = re.split(r"[-+]", cleaned)[0]
    nums = re.findall(r"\d+", core)
    if not nums:
        return (0,)
    return tuple(int(n) for n in nums)


def compare_versions(v_new: str, v_current: str) -> int:
    """Retorna 1 si v_new > v_current, 0 si son iguales, -1 si v_new < v_current."""
    t_new = parse_version_tuple(v_new)
    t_cur = parse_version_tuple(v_current)
    max_len = max(len(t_new), len(t_cur))
    t_new_padded = t_new + (0,) * (max_len - len(t_new))
    t_cur_padded = t_cur + (0,) * (max_len - len(t_cur))
    if t_new_padded > t_cur_padded:
        return 1
    if t_new_padded < t_cur_padded:
        return -1
    return 0


def compute_next_milestone(current_version: str, scheme: str = "semver") -> str:
    """Calcula el siguiente milestone logico segun esquema semver, calver o sequential."""
    clean = current_version.strip().lstrip("vV")
    parts = parse_version_tuple(clean)

    if scheme == "calver":
        today = datetime.date.today()
        if (
            len(parts) >= 3
            and parts[0] >= 2000
            and parts[0] == today.year
            and parts[1] == today.month
        ):
            return f"v{today.year}.{today.month:02d}.{parts[2] + 1}"
        return f"v{today.year}.{today.month:02d}.1"

    if scheme == "sequential":
        last = parts[-1] + 1
        prefix = ".".join(str(p) for p in parts[:-1])
        return f"v{prefix}.{last}" if prefix else f"v{last}"

    major = parts[0] if len(parts) >= 1 else 0
    minor = parts[1] if len(parts) >= 2 else 1
    return f"v{major}.{minor + 1}.0"
