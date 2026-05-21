from __future__ import annotations

from pathlib import Path

from openai import OpenAI


def transcribe_audio_openai(path: Path, model: str, max_mb: int = 25) -> str:
    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > max_mb:
        raise ValueError(f"Audio maior que {max_mb} MB: {path.name} ({size_mb:.1f} MB)")

    client = OpenAI()
    with path.open("rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model=model,
            file=audio_file,
            response_format="text",
        )
    return str(transcript)


def transcribe_audio_local_whisper(path: Path, whisper_model: str = "small", language: str = "pt") -> str:
    try:
        import whisper
    except ImportError as exc:
        raise RuntimeError(
            "openai-whisper nao esta instalado. Rode: .\\.venv\\Scripts\\python.exe -m pip install -U openai-whisper"
        ) from exc

    model = whisper.load_model(whisper_model)
    result = model.transcribe(str(path), language=language, fp16=False)
    return str(result.get("text", "")).strip()


def transcribe_audio(
    path: Path,
    model: str,
    max_mb: int = 25,
    backend: str = "openai",
    whisper_model: str = "small",
    whisper_language: str = "pt",
) -> str:
    if backend == "local-whisper":
        return transcribe_audio_local_whisper(path, whisper_model=whisper_model, language=whisper_language)
    if backend != "openai":
        raise ValueError(f"Backend de transcricao desconhecido: {backend}")
    return transcribe_audio_openai(path, model=model, max_mb=max_mb)
