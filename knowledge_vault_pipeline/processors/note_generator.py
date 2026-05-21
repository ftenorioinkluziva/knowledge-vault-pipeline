from __future__ import annotations

import re
from pathlib import Path

from knowledge_vault_pipeline.models import KnowledgeCard, SourceDocument
from knowledge_vault_pipeline.processors.category import infer_category
from knowledge_vault_pipeline.processors.normalizer_pt import normalize_portuguese
from knowledge_vault_pipeline.processors.terminology import standardize_tags, standardize_terms
from knowledge_vault_pipeline.utils import filename_safe, unique_name, yaml_quote


def bullets_to_paragraphs(value: str) -> str:
    value = re.sub(r"(?:^|\s+)\*\s+\*\*(O que fazer|O que evitar|Sinal de Alerta|Sinal de alerta|Dica extra):\*\*", r"\n\n**\1:**", value)
    value = re.sub(r"(?:^|\s+)(\d+)\.\s+\*\*(.+?):\*\*", r"\n\n\1. **\2:**", value)
    value = re.sub(r"[ \t]{2,}", " ", value)
    value = re.sub(r"\n[ \t]+", "\n", value)
    return value.strip()


def render_card(card: KnowledgeCard, document: SourceDocument, source_note: str, normalize: bool, profile: str) -> tuple[str, str]:
    title = standardize_terms(card.title, profile)
    title = normalize_portuguese(title) if normalize else title
    note_name = filename_safe(title)
    summary = standardize_terms(card.summary, profile)
    detail = standardize_terms(card.detail, profile)
    protocol = standardize_terms(card.protocol, profile)
    tags = standardize_tags(card.tags, profile)
    category = infer_category(document.path.name, title, card.raw_category, tags, profile)
    tag_lines = "\n".join(f"  - {tag}" for tag in tags) or "  - geral"
    content = f"""---
tipo: conhecimento
categoria: {yaml_quote(category)}
tags:
{tag_lines}
fonte: {yaml_quote(card.source or source_note)}
pdf: "[[{document.attachment_name or document.path.name}]]"
nota_fonte: "[[{source_note}]]"
tem_protocolo: {"true" if card.protocol else "false"}
---

# {title}

> **Resumo:** {summary or "Resumo não identificado automaticamente."}

## Explicação Detalhada

{bullets_to_paragraphs(detail) if detail else "Explicação detalhada não identificada automaticamente."}

## Aplicação Prática / Protocolo

{bullets_to_paragraphs(protocol) if protocol else "Nenhum protocolo explícito identificado automaticamente."}

## Fonte

- [[{source_note}]]
"""
    return note_name, normalize_portuguese(content) if normalize else content


def write_vault_ready(
    documents: list[SourceDocument],
    cards_by_source: dict[Path, list[KnowledgeCard]],
    vault_ready_dir: Path,
    normalize: bool = True,
    profile: str = "default",
) -> dict[str, int]:
    knowledge_dir = vault_ready_dir / "02 - Conhecimentos"
    sources_dir = vault_ready_dir / "04 - Fontes"
    knowledge_dir.mkdir(parents=True, exist_ok=True)
    sources_dir.mkdir(parents=True, exist_ok=True)

    used_knowledge: dict[str, int] = {}
    used_sources: dict[str, int] = {}
    total_cards = 0

    for document in documents:
        cards = cards_by_source.get(document.path, [])
        source_note = unique_name(filename_safe(document.path.stem), used_sources)
        note_links: list[str] = []

        for card in cards:
            note_name, content = render_card(card, document, source_note, normalize, profile)
            final_name = unique_name(note_name, used_knowledge)
            (knowledge_dir / f"{final_name}.md").write_text(content.replace(f"[[{note_name}]]", f"[[{final_name}]]"), encoding="utf-8")
            note_links.append(final_name)
            total_cards += 1

        source_content = f"""---
tipo: fonte
categoria: {yaml_quote(infer_category(document.path.name, document.path.stem, "", [], profile))}
tags:
  - fonte
fonte: {yaml_quote(document.path.stem)}
pdf: "[[{document.attachment_name or document.path.name}]]"
---

# {document.path.stem}

## Notas extraídas

{chr(10).join(f"- [[{link}]]" for link in note_links) if note_links else "- Nenhuma nota extraída automaticamente."}

## Observação

Esta nota-fonte conecta os cards extraídos deste documento.
"""
        if normalize:
            source_content = normalize_portuguese(source_content)
        (sources_dir / f"{source_note}.md").write_text(source_content, encoding="utf-8")

    return {"documents": len(documents), "cards": total_cards}
