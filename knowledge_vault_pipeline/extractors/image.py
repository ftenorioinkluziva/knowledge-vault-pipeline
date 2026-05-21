from __future__ import annotations

from pathlib import Path


def extract_image_text(path: Path) -> str:
    try:
        import pytesseract
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError(
            "OCR local requer extras opcionais: pip install -e .[ocr] e Tesseract instalado no Windows."
        ) from exc

    return pytesseract.image_to_string(Image.open(path), lang="por+eng")

