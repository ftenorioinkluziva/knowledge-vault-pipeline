from __future__ import annotations

import re
from pathlib import Path


def find_missing_wikilinks(vault_ready_dir: Path) -> list[tuple[Path, str]]:
    targets = {p.stem for p in vault_ready_dir.rglob("*.md")}
    targets |= {p.stem for p in vault_ready_dir.rglob("*") if p.is_file()}
    targets |= {p.name for p in vault_ready_dir.rglob("*") if p.is_file()}

    missing: list[tuple[Path, str]] = []
    for path in vault_ready_dir.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        for link in re.findall(r"\[\[([^\]|#]+)", text):
            if link not in targets:
                missing.append((path, link))
    return missing

