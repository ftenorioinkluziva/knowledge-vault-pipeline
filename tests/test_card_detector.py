from knowledge_vault_pipeline.processors.card_detector import detect_huberman_cards


def test_detect_huberman_card():
    text = """
--- # Título de Teste **Tags:** #foco #[memória] **Categoria:** Foco **Fonte Original:** Aula
> **Resumo (TL;DR):** Resumo curto.
### 🧠 Explicação Detalhada Texto detalhado.
### 🛠 Aplicação Prática / Protocolo * **O que fazer:** Testar.
"""
    cards = detect_huberman_cards(text)
    assert len(cards) == 1
    assert cards[0].title == "Título de Teste"
    assert cards[0].tags == ["foco", "memoria"]

