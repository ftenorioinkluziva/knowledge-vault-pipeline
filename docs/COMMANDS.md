# Manual de comandos

## Preparar ambiente

```powershell
cd C:\projetos\knowledge-vault-pipeline
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .[ui,dev]
copy .env.example .env
notepad .env
```

## Interface Streamlit

```powershell
.\.venv\Scripts\streamlit.exe run app.py
```

## Documentos locais

```powershell
.\.venv\Scripts\python.exe -m knowledge_vault_pipeline.cli run --config configs\generic-openai.yaml
```

## Huberman

```powershell
.\.venv\Scripts\python.exe -m knowledge_vault_pipeline.cli run --config configs\huberman.yaml
```

## Paridade de Risco / Investimentos

Preencha `.env` com `OPENAI_API_KEY`, depois rode:

```powershell
.\.venv\Scripts\python.exe -m knowledge_vault_pipeline.cli run --config configs\paridade-risco-investimentos.yaml
```

## YouTube / Podcasts

Preencha `.env` com `OPENAI_API_KEY` e `APIFY_TOKEN`, depois rode:

```powershell
.\.venv\Scripts\python.exe -m knowledge_vault_pipeline.cli youtube --config configs\youtube-functional-medicine.yaml
```

## Vídeo local com Whisper

Instale o backend local:

```powershell
.\.venv\Scripts\python.exe -m pip install -U openai-whisper
```

Depois rode a configuração que aponta para o `.mp4` em `input_files`:

```powershell
.\.venv\Scripts\python.exe -m knowledge_vault_pipeline.cli run --config configs\video-local-whisper.yaml
```

## Saída

Todos os modos escrevem em:

```text
<output_dir>\vault-ready\
  02 - Conhecimentos\
  04 - Fontes\
  99 - PDFs\
  99 - Anexos\
```

## Observações

- Não coloque tokens em arquivos YAML.
- O arquivo `.env` e carregado automaticamente pela CLI e pela interface Streamlit.
- Use `vault-ready` como área de revisão antes de copiar para o Obsidian.
- Para OCR local, instale o extra `[ocr]` e o Tesseract no Windows.
