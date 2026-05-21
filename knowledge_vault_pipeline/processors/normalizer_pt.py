from __future__ import annotations

REPLACEMENTS = {
    "nao": "não",
    "voce": "você",
    "atencao": "atenção",
    "cerebro": "cérebro",
    "funcao": "função",
    "pratica": "prática",
    "aplicacao": "aplicação",
    "saude": "saúde",
    "memoria": "memória",
    "nutricao": "nutrição",
    "exercicio": "exercício",
    "explicacao": "explicação",
    "informacoes": "informações",
    "relacao": "relação",
    "visao": "visão",
    "percepcao": "percepção",
    "hipotese": "hipótese",
    "dopaminergica": "dopaminérgica",
    "neurociencia": "neurociência",
    "neuroquimica": "neuroquímica",
    "hormonios": "hormônios",
    "hormonio": "hormônio",
    "musculo": "músculo",
    "musculos": "músculos",
    "longevidade": "longevidade",
    "estrogenio": "estrogênio",
    "cortex": "córtex",
    "celula": "célula",
    "celulas": "células",
    "T-cells": "células T",
    "T-cell": "célula T",
    "Default Mode Network": "rede de modo padrão",
    "Task Network": "rede de tarefa",
    "Task Networks": "redes de tarefa",
    "Vision Board": "quadro de visualização",
}


def normalize_portuguese(text: str) -> str:
    for old, new in REPLACEMENTS.items():
        text = text.replace(old, new)
        text = text.replace(old.capitalize(), new.capitalize())
    text = text.replace("**Resumo (TL;DR):**", "**Resumo:**")
    return text

