# Knowledge Vault Pipeline

Ferramenta local para transformar documentos em uma pasta `vault-ready` para Obsidian.

Fluxo:

```text
entrada com PDFs/TXT/MD/audio/imagens
  -> extracao/transcricao/OCR
  -> deteccao de cards
  -> notas Markdown
  -> vault-ready/
```

## Uso rapido

```powershell
cd C:\projetos\knowledge-vault-pipeline
python -m knowledge_vault_pipeline.cli run --config configs\huberman.yaml
```

## Interface visual

Instale o extra de UI:

```powershell
cd C:\projetos\knowledge-vault-pipeline
.\.venv\Scripts\python.exe -m pip install -e .[ui]
```

Abra:

```powershell
.\.venv\Scripts\streamlit.exe run app.py
```

A interface permite preencher caminhos, escolher perfil, ligar OpenAI/YouTube/OCR/transcricao, gerar o YAML e executar o pipeline. O comando equivalente tambem fica visivel na tela.

Manual completo de comandos: [docs/COMMANDS.md](docs/COMMANDS.md).

O resultado sera criado em:

```text
<output_dir>\vault-ready\
  02 - Conhecimentos\
  04 - Fontes\
  99 - PDFs\
  99 - Anexos\
```

## OpenAI API

Para transcrever audio, defina:

```powershell
$env:OPENAI_API_KEY="sua_chave"
```

Ou use um arquivo `.env` na raiz do projeto:

```powershell
copy .env.example .env
notepad .env
```

Exemplo:

```text
OPENAI_API_KEY=sk-...
APIFY_TOKEN=apify_api_...
```

Para extracao generica, o modelo padrao e `gpt-5.4-mini`, recomendado na documentacao atual para workloads novos de menor latencia/custo e com suporte a Responses API e Structured Outputs.

Para transcricao de audio, o modelo padrao configurado e `gpt-4o-mini-transcribe`. A documentacao atual tambem lista `gpt-4o-transcribe` como opcao de maior custo/qualidade. Arquivos de audio enviados para transcricao devem respeitar o limite de 25 MB por arquivo.

Para transcricao local de audio/video com `ffmpeg`, instale o backend Whisper:

```powershell
.\.venv\Scripts\python.exe -m pip install -U openai-whisper
```

Use `transcription_backend: "local-whisper"` no YAML. Esse modo aceita arquivos de video como `.mp4` sem enviar o audio para a API de transcricao.

## Configuracao

Veja `configs/huberman.yaml`.

Campos principais:

```yaml
input_dir: "C:/caminho/dos/documentos"
output_dir: "C:/caminho/da/saida"
profile: "huberman"
language: "pt-BR"

features:
  pdf: true
  text: true
  audio_transcription: false
  image_ocr: false
```

Por enquanto, o detector principal reconhece cards no formato usado nos PDFs do Huberman. Para novos assuntos, a ideia e adicionar perfis e detectores especificos.

## Perfil generico com OpenAI

Use `configs/generic-openai.yaml` para documentos que ainda nao estao em formato de cards.

Fluxo:

```text
PDF/DOCX/TXT/MD -> texto bruto -> OpenAI Structured Outputs -> notas atomicas -> vault-ready
```

Exemplo:

```powershell
cd C:\projetos\knowledge-vault-pipeline
$env:OPENAI_API_KEY="sua_chave"
.\.venv\Scripts\python.exe -m knowledge_vault_pipeline.cli run --config configs\generic-openai.yaml
```

Campos importantes:

```yaml
features:
  openai_extraction: true

openai:
  extraction_model: "gpt-5.4-mini"
  max_chunk_chars: 18000
  max_cards_per_chunk: 8
```

O pipeline primeiro tenta detectar cards ja prontos. Se nao encontrar cards e `openai_extraction` estiver ativo, ele usa a OpenAI para gerar cards estruturados.

## Perfil Paridade de Risco / Investimentos

Configuracao pronta:

```powershell
.\.venv\Scripts\python.exe -m knowledge_vault_pipeline.cli run --config configs\paridade-risco-investimentos.yaml
```

Entrada padrao:

```text
C:\Users\fteno\Downloads\Paridade Risco Base de conhecimento
```

Saida padrao:

```text
C:\projetos\knowledge-vault-pipeline\output\paridade-risco\vault-ready
```

Esse perfil aceita PDFs e DOCX e usa OpenAI para extrair conceitos atomicos sobre metodologia de paridade de risco, cenarios economicos, classes de ativos, alocacao, riscos e criterios de monitoramento.

Taxonomia usada no Obsidian para esse perfil:

- `Construção de Carteira`
- `Renda Fixa`
- `Política Monetária`
- `Política Fiscal`
- `Comportamento do Investidor`
- `Câmbio`
- `Macroeconomia`
- `Renda Variável`
- `FIIs`
- `ETFs`
- `Métricas e Risco`

O perfil tambem padroniza termos em ingles para portugues quando isso melhora a leitura, por exemplo `equal risk` -> `risco equilibrado`, `equal weight` -> `pesos iguais`, `behavioral gap` -> `lacuna comportamental`, `stock picking` -> `seleção ativa de ações` e `benchmark` -> `referência de comparação`.

## Video local com Whisper

Configuracao pronta para um arquivo `.mp4` especifico:

```powershell
.\.venv\Scripts\python.exe -m knowledge_vault_pipeline.cli run --config configs\video-local-whisper.yaml
```

O arquivo e configurado em `input_files`, por exemplo:

```yaml
input_files:
  - "C:/Users/fteno/Downloads/tsn-cywd-pvd (2025-11-23 15_41 GMT-3).mp4"
openai:
  transcription_backend: "local-whisper"
  whisper_model: "small"
  whisper_language: "pt"
```

## Pipeline YouTube/Podcast

O workflow do n8n pode ser substituido pelo comando `youtube`.

Equivalencia:

```text
n8n RSS Read/Form Trigger
  -> kvp youtube com rss_url ou urls

n8n Apify youtube-transcripts
  -> modulo youtube.py usando APIFY_TOKEN

n8n AI Agent
  -> OpenAI Structured Outputs com profile youtube-functional-medicine

n8n Google Drive/PDF
  -> vault-ready direto para Obsidian
```

Configure:

```powershell
copy .env.example .env
notepad .env
```

Rode:

```powershell
cd C:\projetos\knowledge-vault-pipeline
.\.venv\Scripts\python.exe -m knowledge_vault_pipeline.cli youtube --config configs\youtube-functional-medicine.yaml
```

O arquivo [configs/youtube-functional-medicine.yaml](configs/youtube-functional-medicine.yaml) aceita:

```yaml
youtube:
  rss_url: "https://www.youtube.com/feeds/videos.xml?channel_id=..."
  urls:
    - "https://www.youtube.com/watch?v=..."
  skip_shorts: true
  limit: 5
```

Seguranca: nao coloque tokens no YAML. Use variaveis de ambiente. Se algum token foi colado em chat/log, rotacione esse token no provedor.
