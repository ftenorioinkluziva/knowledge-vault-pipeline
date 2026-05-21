from pathlib import Path

from knowledge_vault_pipeline.config import Features, OpenAIConfig, PipelineConfig
from knowledge_vault_pipeline.models import KnowledgeCard
from knowledge_vault_pipeline.pipeline import run_pipeline


def test_generic_openai_profile_uses_llm_for_unstructured_text(tmp_path, monkeypatch):
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "aula.txt").write_text("Texto livre sobre sono e cafeina.", encoding="utf-8")

    def fake_extract(document, config, language, profile, progress=None):
        return [
            KnowledgeCard(
                title="Cafeína e Sono",
                summary="Cafeína pode afetar o sono.",
                detail="A cafeína interfere no sono em pessoas sensíveis.",
                protocol="Evitar cafeína tarde no dia.",
                tags=["cafeina", "sono"],
                raw_category="Sono",
                source=document.path.stem,
            )
        ]

    monkeypatch.setattr("knowledge_vault_pipeline.pipeline.extract_cards_with_openai", fake_extract)
    config = PipelineConfig(
        input_dir=input_dir,
        output_dir=tmp_path / "out",
        profile="generic-openai",
        features=Features(openai_extraction=True),
        openai=OpenAIConfig(),
    )

    stats = run_pipeline(config)

    assert stats["cards"] == 1
    assert stats["llm_extracted_documents"] == 1
    assert (config.vault_ready_dir / "02 - Conhecimentos" / "Cafeína e Sono.md").exists()
