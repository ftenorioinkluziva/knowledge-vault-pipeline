from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class Features:
    pdf: bool = True
    text: bool = True
    audio_transcription: bool = False
    image_ocr: bool = False
    openai_extraction: bool = False
    normalize_portuguese: bool = True
    validate_links: bool = True


@dataclass(frozen=True)
class OpenAIConfig:
    transcription_model: str = "gpt-4o-mini-transcribe"
    transcription_backend: str = "openai"
    whisper_model: str = "small"
    whisper_language: str = "pt"
    extraction_model: str = "gpt-5.4-mini"
    max_audio_mb: int = 25
    max_chunk_chars: int = 18000
    max_cards_per_chunk: int = 8


@dataclass(frozen=True)
class YoutubeConfig:
    rss_url: str = ""
    urls: list[str] | None = None
    skip_shorts: bool = True
    limit: int = 10
    state_file: str = "youtube_processed.json"
    apify_actor: str = "karamelo~youtube-transcripts"
    poll_seconds: float = 10.0
    timeout_seconds: int = 900


@dataclass(frozen=True)
class PipelineConfig:
    input_dir: Path
    output_dir: Path
    input_files: tuple[Path, ...] = ()
    profile: str = "default"
    language: str = "pt-BR"
    features: Features = Features()
    openai: OpenAIConfig = OpenAIConfig()
    youtube: YoutubeConfig = YoutubeConfig()

    @property
    def vault_ready_dir(self) -> Path:
        return self.output_dir / "vault-ready"


def _as_bool_map(data: dict[str, Any] | None) -> dict[str, Any]:
    return data if isinstance(data, dict) else {}


def load_config(path: str | Path) -> PipelineConfig:
    config_path = Path(path)
    data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    features = Features(**_as_bool_map(data.get("features")))
    openai = OpenAIConfig(**_as_bool_map(data.get("openai")))
    youtube = YoutubeConfig(**_as_bool_map(data.get("youtube")))
    input_files = tuple(Path(item) for item in data.get("input_files", []) or [])
    return PipelineConfig(
        input_dir=Path(data.get("input_dir", ".")),
        output_dir=Path(data["output_dir"]),
        input_files=input_files,
        profile=str(data.get("profile", "default")),
        language=str(data.get("language", "pt-BR")),
        features=features,
        openai=openai,
        youtube=youtube,
    )
