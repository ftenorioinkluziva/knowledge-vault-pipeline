from pathlib import Path

from knowledge_vault_pipeline.models import KnowledgeCard, SourceDocument
from knowledge_vault_pipeline.processors.category import infer_category
from knowledge_vault_pipeline.processors.note_generator import render_card


def test_risk_parity_profile_uses_investment_categories():
    category = infer_category(
        "M1 - Aula 3 - As 3 fontes de Retorno.mp3.pdf",
        "Paridade de risco como defesa comportamental",
        "Saúde Mental",
        ["paridade-de-risco", "disciplina"],
        profile="paridade-risco-investimentos",
    )

    assert category == "Comportamento do Investidor"


def test_risk_parity_category_does_not_match_acao_inside_inflacao():
    category = infer_category(
        "Aula 1 - Critério para datar os Cenários no Brasil.pdf",
        "Cenário 2: expansão com inflação em alta",
        "Cenários macroeconômicos",
        ["inflacao", "alocacao"],
        profile="paridade-risco-investimentos",
    )

    assert category == "Política Monetária"


def test_risk_parity_profile_standardizes_english_terms():
    document = SourceDocument(path=Path("aula.pdf"), text="texto", attachment_name="aula.pdf")
    card = KnowledgeCard(
        title="Carteira equal risk e behavioral gap",
        summary="Equal risk reduz behavioral gap.",
        detail="Evitar stock picking e underperformance.",
        protocol="Monitorar drawdown contra o benchmark.",
        tags=["equal-risk", "behavioral-gap", "stock-picking"],
        raw_category="Saúde Mental",
        source="Aula",
    )

    note_name, content = render_card(card, document, "Aula", normalize=True, profile="paridade-risco-investimentos")

    assert "equal risk" not in content.lower()
    assert "behavioral gap" not in content.lower()
    assert "stock picking" not in content.lower()
    assert "underperformance" not in content.lower()
    assert "benchmark" not in content.lower()
    assert "drawdown" not in content.lower()
    assert "risco equilibrado" in content
    assert "lacuna comportamental" in content
    assert "selecao-ativa-de-acoes" in content
    assert note_name == "Carteira risco equilibrado e lacuna comportamental"
