from __future__ import annotations

import re

from knowledge_vault_pipeline.utils import tag_safe


RISK_PARITY_TERM_REPLACEMENTS = [
    (r"\bbehavioral gap\b", "lacuna comportamental"),
    (r"\bstock picking\b", "seleção ativa de ações"),
    (r"\bunderperformance\b", "desempenho inferior"),
    (r"\bequal risk\b", "risco equilibrado"),
    (r"\bequal weight\b", "pesos iguais"),
    (r"\brisk parity\b", "paridade de risco"),
    (r"\bportfolio\b", "portfólio"),
    (r"\bbenchmark\b", "referência de comparação"),
    (r"\bdrawdown\b", "queda desde o pico"),
]

RISK_PARITY_TAG_REPLACEMENTS = {
    "behavioral-gap": "lacuna-comportamental",
    "stock-picking": "selecao-ativa-de-acoes",
    "underperformance": "desempenho-inferior",
    "equal-risk": "risco-equilibrado",
    "equal-weight": "pesos-iguais",
    "risk-parity": "paridade-de-risco",
    "portfolio": "portfolio",
    "benchmark": "referencia-de-comparacao",
    "drawdown": "queda-desde-o-pico",
}


def standardize_risk_parity_terms(text: str) -> str:
    for pattern, replacement in RISK_PARITY_TERM_REPLACEMENTS:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    text = re.sub(r"\bo lacuna comportamental\b", "a lacuna comportamental", text, flags=re.IGNORECASE)
    return text


def standardize_terms(text: str, profile: str) -> str:
    if profile in {"paridade-risco-investimentos", "risk-parity-investments", "investimentos"}:
        return standardize_risk_parity_terms(text)
    return text


def standardize_tags(tags: list[str], profile: str) -> list[str]:
    cleaned: list[str] = []
    for tag in tags:
        safe = tag_safe(tag)
        if profile in {"paridade-risco-investimentos", "risk-parity-investments", "investimentos"}:
            safe = RISK_PARITY_TAG_REPLACEMENTS.get(safe, safe)
        if safe and safe not in cleaned:
            cleaned.append(safe)
    return cleaned
