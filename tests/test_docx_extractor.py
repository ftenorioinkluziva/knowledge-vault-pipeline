from pathlib import Path

from knowledge_vault_pipeline.extractors.docx import extract_docx_text


def test_extract_docx_text_from_real_fixture_if_available():
    folder = Path(r"C:\Users\fteno\Downloads\Paridade Risco Base de conhecimento")
    docs = sorted(folder.glob("*.docx"))
    if not docs:
        return
    text = extract_docx_text(docs[0])
    assert len(text) > 100
