from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Callable

from openai import OpenAI
from pydantic import BaseModel, Field

from knowledge_vault_pipeline.config import OpenAIConfig
from knowledge_vault_pipeline.models import KnowledgeCard, SourceDocument
from knowledge_vault_pipeline.processors.profiles import instructions_for_profile
from knowledge_vault_pipeline.utils import clean_space, tag_safe


class ExtractedCard(BaseModel):
    title: str = Field(description="Titulo curto e especifico da nota atomica, em portugues.")
    category: str = Field(description="Categoria ampla em portugues.")
    tags: list[str] = Field(description="Tags curtas, sem #, em portugues quando possivel.")
    summary: str = Field(description="Resumo de uma ou duas frases.")
    detail: str = Field(description="Explicacao detalhada, fiel ao texto de origem.")
    protocol: str = Field(description="Aplicacao pratica, protocolo, riscos ou criterio de uso. Use string vazia se nao houver.")


class ExtractionResult(BaseModel):
    cards: list[ExtractedCard]


@dataclass(frozen=True)
class Chunk:
    index: int
    text: str


def chunk_text(text: str, max_chars: int) -> list[Chunk]:
    text = clean_space(text)
    if len(text) <= max_chars:
        return [Chunk(index=1, text=text)]

    chunks: list[Chunk] = []
    start = 0
    index = 1
    while start < len(text):
        end = min(start + max_chars, len(text))
        if end < len(text):
            split_at = max(text.rfind(". ", start, end), text.rfind("\n", start, end))
            if split_at > start + max_chars // 2:
                end = split_at + 1
        chunks.append(Chunk(index=index, text=text[start:end].strip()))
        start = end
        index += 1
    return chunks


def ensure_openai_key() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError(
            "OPENAI_API_KEY nao esta definido. Defina a variavel de ambiente para usar extracao generica via OpenAI."
        )


def extract_cards_with_openai(
    document: SourceDocument,
    config: OpenAIConfig,
    language: str = "pt-BR",
    profile: str = "default",
    progress: Callable[[str], None] | None = None,
) -> list[KnowledgeCard]:
    ensure_openai_key()
    client = OpenAI(timeout=120.0)
    cards: list[KnowledgeCard] = []
    chunks = chunk_text(document.text, config.max_chunk_chars)

    for chunk in chunks:
        if progress:
            progress(f"OpenAI: {document.path.name} | trecho {chunk.index}/{len(chunks)}")
        response = client.responses.parse(
            model=config.extraction_model,
            instructions=instructions_for_profile(profile),
            input=[
                {
                    "role": "user",
                    "content": (
                        f"Documento: {document.path.name}\n"
                        f"Idioma alvo: {language}\n"
                        f"Limite: no maximo {config.max_cards_per_chunk} cards para este trecho.\n\n"
                        f"Trecho {chunk.index}:\n{chunk.text}"
                    ),
                }
            ],
            text_format=ExtractionResult,
        )
        result = response.output_parsed
        if progress:
            progress(f"OpenAI: {document.path.name} | trecho {chunk.index} retornou {len(result.cards)} card(s)")
        for item in result.cards[: config.max_cards_per_chunk]:
            cards.append(
                KnowledgeCard(
                    title=clean_space(item.title),
                    summary=clean_space(item.summary),
                    detail=clean_space(item.detail),
                    protocol=clean_space(item.protocol),
                    tags=[tag_safe(tag) for tag in item.tags if tag_safe(tag)],
                    raw_category=clean_space(item.category),
                    source=document.path.stem,
                )
            )

    return cards
