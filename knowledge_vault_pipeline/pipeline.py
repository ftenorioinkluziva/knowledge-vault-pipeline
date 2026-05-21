from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import Callable

from knowledge_vault_pipeline.config import PipelineConfig
from knowledge_vault_pipeline.extractors.audio import transcribe_audio
from knowledge_vault_pipeline.extractors.docx import extract_docx_text
from knowledge_vault_pipeline.extractors.image import extract_image_text
from knowledge_vault_pipeline.extractors.pdf import extract_pdf_text
from knowledge_vault_pipeline.extractors.text import extract_text_file
from knowledge_vault_pipeline.models import SourceDocument
from knowledge_vault_pipeline.processors.card_detector import detect_huberman_cards
from knowledge_vault_pipeline.processors.link_validator import find_missing_wikilinks
from knowledge_vault_pipeline.processors.llm_extractor import extract_cards_with_openai
from knowledge_vault_pipeline.processors.note_generator import write_vault_ready
from knowledge_vault_pipeline.utils import copy_attachment


PDF_EXTS = {".pdf"}
TEXT_EXTS = {".txt", ".md"}
DOCX_EXTS = {".docx"}
AUDIO_EXTS = {".mp3", ".mp4", ".mpeg", ".mpga", ".m4a", ".wav", ".webm"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"}


def reset_output(vault_ready_dir: Path) -> None:
    if vault_ready_dir.exists():
        shutil.rmtree(vault_ready_dir)
    (vault_ready_dir / "02 - Conhecimentos").mkdir(parents=True, exist_ok=True)
    (vault_ready_dir / "04 - Fontes").mkdir(parents=True, exist_ok=True)
    (vault_ready_dir / "99 - PDFs").mkdir(parents=True, exist_ok=True)
    (vault_ready_dir / "99 - Anexos").mkdir(parents=True, exist_ok=True)


def _print_progress(message: str) -> None:
    print(message, file=sys.stderr, flush=True)


def collect_documents(config: PipelineConfig, progress: Callable[[str], None] | None = None) -> list[SourceDocument]:
    documents: list[SourceDocument] = []
    paths = list(config.input_files) if config.input_files else [path for path in sorted(config.input_dir.rglob("*")) if path.is_file()]
    for index, path in enumerate(paths, start=1):
        if not path.is_file():
            continue
        suffix = path.suffix.lower()
        text = ""
        attachment_name: str | None = None

        if suffix in PDF_EXTS and config.features.pdf:
            if progress:
                progress(f"Lendo PDF {index}/{len(paths)}: {path.name}")
            text = extract_pdf_text(path)
            attachment_name = copy_attachment(path, config.vault_ready_dir / "99 - PDFs").name
        elif suffix in TEXT_EXTS and config.features.text:
            if progress:
                progress(f"Lendo texto {index}/{len(paths)}: {path.name}")
            text = extract_text_file(path)
            attachment_name = copy_attachment(path, config.vault_ready_dir / "99 - Anexos").name
        elif suffix in DOCX_EXTS and config.features.text:
            if progress:
                progress(f"Lendo DOCX {index}/{len(paths)}: {path.name}")
            text = extract_docx_text(path)
            attachment_name = copy_attachment(path, config.vault_ready_dir / "99 - Anexos").name
        elif suffix in AUDIO_EXTS and config.features.audio_transcription:
            if progress:
                progress(f"Transcrevendo audio {index}/{len(paths)}: {path.name}")
            text = transcribe_audio(
                path,
                config.openai.transcription_model,
                config.openai.max_audio_mb,
                backend=config.openai.transcription_backend,
                whisper_model=config.openai.whisper_model,
                whisper_language=config.openai.whisper_language,
            )
            attachment_name = copy_attachment(path, config.vault_ready_dir / "99 - Anexos").name
        elif suffix in IMAGE_EXTS and config.features.image_ocr:
            if progress:
                progress(f"Lendo imagem {index}/{len(paths)}: {path.name}")
            text = extract_image_text(path)
            attachment_name = copy_attachment(path, config.vault_ready_dir / "99 - Anexos").name

        if text.strip():
            documents.append(SourceDocument(path=path, text=text, attachment_name=attachment_name))

    return documents


def run_pipeline(config: PipelineConfig) -> dict[str, int | str]:
    progress = _print_progress
    progress(f"Preparando saida: {config.vault_ready_dir}")
    reset_output(config.vault_ready_dir)
    documents = collect_documents(config, progress=progress)
    progress(f"Documentos com texto extraido: {len(documents)}")
    cards_by_source = {}
    llm_extracted_documents = 0
    for index, doc in enumerate(documents, start=1):
        progress(f"Processando documento {index}/{len(documents)}: {doc.path.name}")
        cards = detect_huberman_cards(doc.text)
        if not cards and config.features.openai_extraction:
            cards = extract_cards_with_openai(doc, config.openai, config.language, config.profile, progress=progress)
            llm_extracted_documents += 1
        progress(f"Cards extraidos de {doc.path.name}: {len(cards)}")
        cards_by_source[doc.path] = cards
    progress("Escrevendo notas vault-ready...")
    stats = write_vault_ready(
        documents,
        cards_by_source,
        config.vault_ready_dir,
        normalize=config.features.normalize_portuguese,
        profile=config.profile,
    )
    missing = find_missing_wikilinks(config.vault_ready_dir) if config.features.validate_links else []
    progress("Pipeline concluido.")
    return {
        **stats,
        "llm_extracted_documents": llm_extracted_documents,
        "missing_links": len(missing),
        "vault_ready_dir": str(config.vault_ready_dir),
    }
