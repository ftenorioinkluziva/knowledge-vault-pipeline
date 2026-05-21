from __future__ import annotations

import json
import os
from pathlib import Path

import streamlit as st
import yaml

from knowledge_vault_pipeline.config import load_config
from knowledge_vault_pipeline.env import load_project_env
from knowledge_vault_pipeline.pipeline import run_pipeline
from knowledge_vault_pipeline.youtube import run_youtube_pipeline


load_project_env()

ROOT = Path(__file__).parent
GENERATED_CONFIG = ROOT / "configs" / "ui-generated.yaml"


def write_config(data: dict) -> Path:
    GENERATED_CONFIG.parent.mkdir(parents=True, exist_ok=True)
    GENERATED_CONFIG.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return GENERATED_CONFIG


def path_input(label: str, value: str) -> str:
    return st.text_input(label, value=value, help="Use caminho absoluto no Windows, por exemplo C:/projetos/meus-documentos")


def common_openai_controls(prefix: str) -> dict:
    with st.expander("OpenAI", expanded=True):
        extraction_model = st.text_input("Modelo de extração", value="gpt-5.4-mini", key=f"{prefix}_extraction_model")
        transcription_backend = st.selectbox("Backend de transcrição", ["openai", "local-whisper"], index=0, key=f"{prefix}_transcription_backend")
        transcription_model = st.text_input("Modelo de transcrição", value="gpt-4o-mini-transcribe", key=f"{prefix}_transcription_model")
        whisper_model = st.selectbox("Modelo Whisper local", ["tiny", "base", "small", "medium", "large"], index=2, key=f"{prefix}_whisper_model")
        whisper_language = st.text_input("Idioma Whisper local", value="pt", key=f"{prefix}_whisper_language")
        max_chunk_chars = st.number_input("Tamanho máximo do trecho", min_value=4000, max_value=60000, value=18000, step=1000, key=f"{prefix}_max_chunk_chars")
        max_cards_per_chunk = st.number_input("Cards por trecho", min_value=1, max_value=20, value=8, step=1, key=f"{prefix}_max_cards")
    return {
        "extraction_model": extraction_model,
        "transcription_backend": transcription_backend,
        "transcription_model": transcription_model,
        "whisper_model": whisper_model,
        "whisper_language": whisper_language,
        "max_audio_mb": 25,
        "max_chunk_chars": int(max_chunk_chars),
        "max_cards_per_chunk": int(max_cards_per_chunk),
    }


def render_result(stats: dict) -> None:
    st.success("Pipeline concluído.")
    st.json(stats)
    vault_ready = stats.get("vault_ready_dir")
    if vault_ready:
        st.code(str(vault_ready), language="text")


def run_from_config(command: str, config_path: Path) -> None:
    config = load_config(config_path)
    with st.spinner("Processando..."):
        if command == "youtube":
            stats = run_youtube_pipeline(config)
        else:
            stats = run_pipeline(config)
    render_result(stats)


def local_tab() -> None:
    st.subheader("Documentos locais")
    input_dir = path_input("Pasta de entrada", "C:/caminho/dos/documentos")
    input_files_text = st.text_area("Arquivos específicos, um por linha", value="", help="Opcional. Use para processar um vídeo/áudio específico sem varrer uma pasta inteira.")
    output_dir = path_input("Pasta de saída", "C:/caminho/da/saida")
    profile = st.selectbox(
        "Perfil",
        ["generic-openai", "huberman", "medicina-funcional", "paridade-risco-investimentos"],
        index=0,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        pdf = st.checkbox("PDF", value=True)
        text = st.checkbox("TXT/MD", value=True)
    with col2:
        audio = st.checkbox("Transcrever áudio", value=False)
        image_ocr = st.checkbox("OCR de imagens", value=False)
    with col3:
        openai_extraction = st.checkbox("Extrair cards com OpenAI", value=True)
        validate_links = st.checkbox("Validar links", value=True)

    openai = common_openai_controls("local")
    config = {
        "input_dir": input_dir,
        "input_files": [line.strip() for line in input_files_text.splitlines() if line.strip()],
        "output_dir": output_dir,
        "profile": profile,
        "language": "pt-BR",
        "features": {
            "pdf": pdf,
            "text": text,
            "audio_transcription": audio,
            "image_ocr": image_ocr,
            "openai_extraction": openai_extraction,
            "normalize_portuguese": True,
            "validate_links": validate_links,
        },
        "openai": openai,
    }

    config_path = write_config(config)
    command = f'.\\.venv\\Scripts\\python.exe -m knowledge_vault_pipeline.cli run --config "{config_path}"'
    st.caption("Comando equivalente")
    st.code(command, language="powershell")

    if st.button("Processar documentos locais", type="primary"):
        run_from_config("run", config_path)


def youtube_tab() -> None:
    st.subheader("YouTube / podcasts")
    output_dir = path_input("Pasta de saída", "C:/projetos/knowledge-vault-pipeline/output/youtube-functional")
    profile = st.selectbox("Perfil", ["youtube-functional-medicine", "generic-openai"], index=0)
    rss_url = st.text_input("RSS do canal", value="https://www.youtube.com/feeds/videos.xml?channel_id=UC2D2CMWXMOVWx7giW1n3LIg")
    urls_text = st.text_area("URLs manuais, uma por linha", value="")
    limit = st.number_input("Limite de vídeos novos", min_value=1, max_value=100, value=5)
    skip_shorts = st.checkbox("Pular Shorts", value=True)

    st.info("Tokens não são salvos no YAML. Defina OPENAI_API_KEY e APIFY_TOKEN no ambiente antes de executar.")
    st.write("OPENAI_API_KEY:", "definido" if os.getenv("OPENAI_API_KEY") else "não definido")
    st.write("APIFY_TOKEN:", "definido" if os.getenv("APIFY_TOKEN") else "não definido")

    openai = common_openai_controls("youtube")
    urls = [line.strip() for line in urls_text.splitlines() if line.strip()]
    config = {
        "input_dir": str(ROOT / "_unused"),
        "output_dir": output_dir,
        "profile": profile,
        "language": "pt-BR",
        "features": {
            "pdf": False,
            "text": True,
            "audio_transcription": False,
            "image_ocr": False,
            "openai_extraction": True,
            "normalize_portuguese": True,
            "validate_links": True,
        },
        "openai": openai,
        "youtube": {
            "rss_url": rss_url,
            "urls": urls,
            "skip_shorts": skip_shorts,
            "limit": int(limit),
            "state_file": "youtube_processed.json",
            "apify_actor": "karamelo~youtube-transcripts",
            "poll_seconds": 10,
            "timeout_seconds": 900,
        },
    }

    config_path = write_config(config)
    command = f'.\\.venv\\Scripts\\python.exe -m knowledge_vault_pipeline.cli youtube --config "{config_path}"'
    st.caption("Comando equivalente")
    st.code(command, language="powershell")

    if st.button("Processar YouTube", type="primary"):
        run_from_config("youtube", config_path)


def manual_tab() -> None:
    st.subheader("Manual rápido")
    st.markdown(
        """
### Instalação

```powershell
cd C:\\projetos\\knowledge-vault-pipeline
python -m venv .venv
.\\.venv\\Scripts\\python.exe -m pip install -e .[ui,dev]
```

### Abrir interface

```powershell
.\\.venv\\Scripts\\streamlit.exe run app.py
```

### Rodar por CLI

```powershell
.\\.venv\\Scripts\\python.exe -m knowledge_vault_pipeline.cli run --config configs\\generic-openai.yaml
.\\.venv\\Scripts\\python.exe -m knowledge_vault_pipeline.cli youtube --config configs\\youtube-functional-medicine.yaml
```

### Variáveis de ambiente

```powershell
$env:OPENAI_API_KEY="sua_chave"
$env:APIFY_TOKEN="seu_token_apify"
```

### Saída

O projeto sempre gera uma pasta `vault-ready`, pronta para copiar para o cofre Obsidian.
"""
    )


def main() -> None:
    st.set_page_config(page_title="Knowledge Vault Pipeline", layout="wide")
    st.title("Knowledge Vault Pipeline")
    st.caption("Gerador local de bases Obsidian a partir de PDFs, textos, transcrições, áudio, imagens e YouTube.")

    tab_local, tab_youtube, tab_manual = st.tabs(["Documentos locais", "YouTube / Podcasts", "Manual"])
    with tab_local:
        local_tab()
    with tab_youtube:
        youtube_tab()
    with tab_manual:
        manual_tab()


if __name__ == "__main__":
    main()
