from __future__ import annotations

import re

from knowledge_vault_pipeline.models import KnowledgeCard
from knowledge_vault_pipeline.utils import clean_space, strip_outer_noise, tag_safe


def detect_huberman_cards(text: str) -> list[KnowledgeCard]:
    text = clean_space(text)
    chunks = re.split(r"(?=(?:---|\*\*\*)\s*#\s+)", text)
    cards: list[KnowledgeCard] = []
    for chunk in chunks:
        if not re.match(r"(?:---|\*\*\*)\s*#\s+", chunk):
            continue

        title_match = re.search(r"#\s+(.+?)\s+\*\*Tags:\*\*", chunk)
        if not title_match:
            continue

        tags_match = re.search(r"\*\*Tags:\*\*\s+(.+?)\s+\*\*Categoria:\*\*", chunk)
        cat_match = re.search(r"\*\*Categoria:\*\*\s+(.+?)\s+\*\*Fonte Original:\*\*", chunk)
        source_match = re.search(r"\*\*Fonte Original:\*\*\s+(.+?)\s+>\s+\*\*Resumo \(TL;DR\):\*\*", chunk)
        summary_match = re.search(r">\s+\*\*Resumo \(TL;DR\):\*\*\s+(.+?)\s+###\s+[^A-Za-zÀ-ÿ0-9]*Explica(?:ç|c)ão Detalhada", chunk)
        detail_match = re.search(r"###\s+[^A-Za-zÀ-ÿ0-9]*Explica(?:ç|c)ão Detalhada\s+(.+?)\s+###\s+[^A-Za-zÀ-ÿ0-9]*(?:Aplicação Prática|Aplicacao Pratica)\s*/\s*Protocolo", chunk)
        protocol_match = re.search(r"###\s+[^A-Za-zÀ-ÿ0-9]*(?:Aplicação Prática|Aplicacao Pratica)\s*/\s*Protocolo\s+(.+)$", chunk)

        raw_tags = tags_match.group(1) if tags_match else ""
        tag_values = re.findall(r"#\[([^\]]+)\]|#([\w\-À-ÿ]+)", raw_tags)
        tags = [tag_safe(a or b) for a, b in tag_values]
        tags = [tag for tag in dict.fromkeys(tags) if tag]

        cards.append(
            KnowledgeCard(
                title=strip_outer_noise(title_match.group(1)),
                tags=tags,
                raw_category=clean_space(cat_match.group(1)) if cat_match else "",
                source=clean_space(source_match.group(1)) if source_match else "",
                summary=clean_space(summary_match.group(1)) if summary_match else "",
                detail=clean_space(detail_match.group(1)) if detail_match else "",
                protocol=clean_space(protocol_match.group(1)) if protocol_match else "",
            )
        )
    return cards

