from __future__ import annotations

import re
import shutil
import unicodedata
from pathlib import Path


def clean_space(value: str) -> str:
    value = value.replace("\xa0", " ")
    value = re.sub(r"\s+", " ", value)
    value = re.sub(r"\s+([,.;:!?])", r"\1", value)
    return value.strip()


def strip_outer_noise(value: str) -> str:
    value = value.strip()
    value = re.sub(r"^\s*\[+\s*", "", value)
    value = re.sub(r"\s*\]+\s*$", "", value)
    value = re.sub(r"^\s*TITULO\s+", "", value, flags=re.IGNORECASE)
    return clean_space(value)


def filename_safe(value: str, max_len: int = 150) -> str:
    value = strip_outer_noise(value)
    value = re.sub(r'[<>:"/\\|?*#]', " ", value)
    value = re.sub(r"\s+", " ", value).strip(" .")
    return value[:max_len].rstrip(" .") or "Nota"


def tag_safe(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def yaml_quote(value: str) -> str:
    value = clean_space(value).replace('"', '\\"')
    return f'"{value}"'


def unique_name(name: str, used: dict[str, int]) -> str:
    if name not in used:
        used[name] = 1
        return name
    used[name] += 1
    return f"{name} {used[name]}"


def copy_attachment(source: Path, target_dir: Path) -> Path:
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / source.name.replace("#", "")
    if source.resolve() == target.resolve():
        return target
    shutil.copy2(source, target)
    return target

