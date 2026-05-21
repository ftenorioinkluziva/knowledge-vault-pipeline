from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class SourceDocument:
    path: Path
    text: str
    attachment_name: str | None = None


@dataclass
class KnowledgeCard:
    title: str
    summary: str = ""
    detail: str = ""
    protocol: str = ""
    tags: list[str] = field(default_factory=list)
    raw_category: str = ""
    source: str = ""

