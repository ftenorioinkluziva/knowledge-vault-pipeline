from knowledge_vault_pipeline.processors.llm_extractor import chunk_text


def test_chunk_text_splits_long_text():
    chunks = chunk_text("A. " * 100, max_chars=50)
    assert len(chunks) > 1
    assert chunks[0].index == 1
    assert all(len(chunk.text) <= 55 for chunk in chunks)

