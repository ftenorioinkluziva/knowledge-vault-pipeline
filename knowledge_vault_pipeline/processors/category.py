from __future__ import annotations

from knowledge_vault_pipeline.utils import tag_safe


RISK_PARITY_CATEGORIES = [
    ("Comportamento do Investidor", ["comportamental", "disciplina", "fomo", "vies", "ansiedade", "emocional", "queda-desde-pico", "drawdown", "desempenho-inferior", "underperformance"]),
    ("Construção de Carteira", ["paridade-de-risco", "carteira", "diversificacao", "risco-equilibrado", "pesos-iguais", "rebalanceamento", "volatilidade", "correlacao", "classes-de-ativos", "selecao-de-ativos", "elo-causal"]),
    ("ETFs", ["etf", "etfs", "bova11", "ivvb11", "ib5m11", "b5p211", "ifrm11", "fixa11", "imab11"]),
    ("FIIs", ["fii", "fiis", "ifix", "fundo-imobiliario", "fundos-imobiliarios", "vacancia", "aluguel"]),
    ("Renda Variável", ["acoes", "acao", "ibovespa", "renda-variavel", "lucro", "valuation", "bova11"]),
    ("Renda Fixa", ["renda-fixa", "tesouro", "ipca", "ima-b", "imab", "selic", "cdi", "pre-fixado", "pos-fixado", "duration", "duracao", "titulo-publico", "titulos-publicos"]),
    ("Câmbio", ["dolar", "cambio", "balanco-de-pagamentos", "fluxo-cambial", "moeda"]),
    ("Política Fiscal", ["fiscal", "divida", "superavit", "deficit", "teto-de-gastos", "regra-de-ouro", "lrf", "tesouro", "solvencia"]),
    ("Política Monetária", ["politica-monetaria", "banco-central", "bcb", "copom", "fed", "selic", "juros", "inflacao", "expectativas", "regra-de-taylor", "pce"]),
    ("Macroeconomia", ["macroeconomia", "macro", "cenario", "cenarios", "pib", "recessao", "expansao", "ciclo", "codace", "brasil", "eua", "commodities"]),
    ("Métricas e Risco", ["risco", "volatilidade", "retorno", "premio-de-risco", "taxa-livre-de-risco", "benchmark", "referencia", "janela", "metricas"]),
]


def _infer_risk_parity_category(hay: str, raw_category: str) -> str:
    for category, needles in RISK_PARITY_CATEGORIES:
        if any(_matches_term(hay, needle) for needle in needles):
            return category
    return raw_category or "Geral"


def _matches_term(hay: str, needle: str) -> bool:
    tokens = set(hay.split("-"))
    if "-" not in needle:
        return needle in tokens
    return needle in hay


def infer_category(source_name: str, title: str, raw_category: str, tags: list[str], profile: str = "default") -> str:
    hay = tag_safe(" ".join([source_name, title, raw_category, " ".join(tags)]))
    if profile in {"paridade-risco-investimentos", "risk-parity-investments", "investimentos"}:
        return _infer_risk_parity_category(hay, raw_category)

    rules = [
        ("Sono", ["sleep", "sono", "caffeine", "circadian", "nap"]),
        ("Treino e Performance", ["exercise", "fitness", "muscle", "strength", "endurance", "recovery", "cooling", "mobility", "back", "training", "cardio", "physique"]),
        ("Nutrição e Metabolismo", ["nutrition", "foods", "diet", "sugar", "metabolism", "fasting", "hunger", "gut", "microbiome", "salt", "water", "obesity", "fat-loss"]),
        ("Suplementos", ["supplement", "creatine", "collagen", "whey", "peptide", "resveratrol", "nmn", "nr"]),
        ("Hormônios e Fertilidade", ["hormone", "fertility", "sexual", "testosterone", "estrogen", "menopause", "female", "male", "pcos", "endometriosis"]),
        ("Foco e Memória", ["adhd", "focus", "attention", "memory", "learning", "dopamine", "productivity", "goal", "habit", "procrastination"]),
        ("Saúde Mental", ["stress", "anxiety", "emotion", "mental", "trauma", "addiction", "meditation", "awe", "love", "confidence", "mindset"]),
        ("Longevidade", ["longevity", "aging", "lifespan", "vitality", "youthfulness", "mitochondria"]),
        ("Imunidade", ["immune", "immunity", "cancer"]),
        ("Dor", ["pain", "headache"]),
    ]
    for category, needles in rules:
        if any(needle in hay for needle in needles):
            return category
    return raw_category or "Geral"
