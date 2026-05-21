from __future__ import annotations

import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path


WORD_NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def _paragraph_text(paragraph: ET.Element) -> str:
    parts: list[str] = []
    for node in paragraph.iter():
        if node.tag == f"{{{WORD_NS['w']}}}t" and node.text:
            parts.append(node.text)
        elif node.tag == f"{{{WORD_NS['w']}}}tab":
            parts.append("\t")
        elif node.tag == f"{{{WORD_NS['w']}}}br":
            parts.append("\n")
    return "".join(parts).strip()


def extract_docx_text(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        xml_data = archive.read("word/document.xml")
    root = ET.fromstring(xml_data)
    paragraphs = [_paragraph_text(paragraph) for paragraph in root.findall(".//w:p", WORD_NS)]
    return "\n".join(paragraph for paragraph in paragraphs if paragraph)
