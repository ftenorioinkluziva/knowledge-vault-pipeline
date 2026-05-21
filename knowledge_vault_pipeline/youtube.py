from __future__ import annotations

import json
import os
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

import httpx

from knowledge_vault_pipeline.config import PipelineConfig
from knowledge_vault_pipeline.pipeline import run_pipeline
from knowledge_vault_pipeline.utils import filename_safe


@dataclass(frozen=True)
class YoutubeVideo:
    video_id: str
    title: str
    link: str
    published: str = ""
    author: str = ""


def load_state(path: Path) -> set[str]:
    if not path.exists():
        return set()
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return set(str(item) for item in data)
    return set(str(item) for item in data.get("processed_video_ids", []))


def save_state(path: Path, processed: set[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"processed_video_ids": sorted(processed)}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def is_short_url(url: str) -> bool:
    return "/shorts/" in urlparse(url).path.lower()


def parse_youtube_rss(xml_text: str) -> list[YoutubeVideo]:
    root = ET.fromstring(xml_text)
    ns = {
        "atom": "http://www.w3.org/2005/Atom",
        "yt": "http://www.youtube.com/xml/schemas/2015",
    }
    videos: list[YoutubeVideo] = []
    for entry in root.findall("atom:entry", ns):
        video_id = entry.findtext("yt:videoId", default="", namespaces=ns)
        title = entry.findtext("atom:title", default="", namespaces=ns)
        published = entry.findtext("atom:published", default="", namespaces=ns)
        author = entry.findtext("atom:author/atom:name", default="", namespaces=ns)
        link_el = entry.find("atom:link", ns)
        link = link_el.attrib.get("href", "") if link_el is not None else ""
        if video_id and link:
            videos.append(YoutubeVideo(video_id=video_id, title=title, link=link, published=published, author=author))
    return videos


def fetch_rss_videos(rss_url: str) -> list[YoutubeVideo]:
    response = httpx.get(rss_url, timeout=30)
    response.raise_for_status()
    return parse_youtube_rss(response.text)


def video_from_url(url: str) -> YoutubeVideo:
    parsed = urlparse(url)
    video_id = ""
    if "youtu.be" in parsed.netloc:
        video_id = parsed.path.strip("/")
    elif "youtube.com" in parsed.netloc:
        query = dict(part.split("=", 1) for part in parsed.query.split("&") if "=" in part)
        video_id = query.get("v", "")
    return YoutubeVideo(video_id=video_id or filename_safe(url, 40), title=video_id or url, link=url)


def apify_headers() -> dict[str, str]:
    token = os.getenv("APIFY_TOKEN")
    if not token:
        raise RuntimeError("APIFY_TOKEN nao esta definido. Rotacione o token exposto e defina a variavel de ambiente.")
    return {"Authorization": f"Bearer {token}"}


def start_apify_transcript_run(actor: str, url: str) -> dict:
    payload = {
        "channelIDBoolean": True,
        "channelNameBoolean": True,
        "commentsBoolean": False,
        "datePublishedBoolean": True,
        "descriptionBoolean": False,
        "keywordsBoolean": False,
        "likesBoolean": False,
        "maxRetries": 8,
        "outputFormat": "singleStringText",
        "relativeDateTextBoolean": False,
        "thumbnailBoolean": False,
        "urls": [url],
        "viewCountBoolean": False,
    }
    response = httpx.post(
        f"https://api.apify.com/v2/acts/{actor}/runs",
        headers=apify_headers(),
        json=payload,
        timeout=60,
    )
    response.raise_for_status()
    return response.json()["data"]


def wait_apify_run(run: dict, poll_seconds: float, timeout_seconds: int) -> dict:
    act_id = run["actId"]
    run_id = run["id"]
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        response = httpx.get(
            f"https://api.apify.com/v2/acts/{act_id}/runs/{run_id}",
            headers=apify_headers(),
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()["data"]
        if data["status"] == "SUCCEEDED":
            return data
        if data["status"] in {"FAILED", "ABORTED", "TIMED-OUT"}:
            raise RuntimeError(f"Apify run terminou com status {data['status']}: {run_id}")
        time.sleep(poll_seconds)
    raise TimeoutError(f"Timeout aguardando Apify run: {run_id}")


def extract_caption_text(items: list[dict]) -> str:
    chunks: list[str] = []
    for item in items:
        for key in ["captions", "transcript", "text", "subtitles"]:
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                chunks.append(value.strip())
            elif isinstance(value, list):
                for part in value:
                    if isinstance(part, str):
                        chunks.append(part)
                    elif isinstance(part, dict):
                        text = part.get("text") or part.get("caption")
                        if text:
                            chunks.append(str(text))
    return "\n".join(chunks).strip()


def fetch_dataset_text(dataset_id: str) -> str:
    response = httpx.get(
        f"https://api.apify.com/v2/datasets/{dataset_id}/items",
        headers=apify_headers(),
        timeout=60,
    )
    response.raise_for_status()
    return extract_caption_text(response.json())


def fetch_transcript(video: YoutubeVideo, config: PipelineConfig) -> str:
    run = start_apify_transcript_run(config.youtube.apify_actor, video.link)
    completed = wait_apify_run(run, config.youtube.poll_seconds, config.youtube.timeout_seconds)
    return fetch_dataset_text(completed["defaultDatasetId"])


def prepare_youtube_transcripts(config: PipelineConfig) -> dict[str, int | str]:
    ingest_dir = config.output_dir / "youtube-ingest"
    transcripts_dir = ingest_dir / "transcripts"
    transcripts_dir.mkdir(parents=True, exist_ok=True)

    state_path = ingest_dir / config.youtube.state_file
    processed = load_state(state_path)

    videos: list[YoutubeVideo] = []
    if config.youtube.rss_url:
        videos.extend(fetch_rss_videos(config.youtube.rss_url))
    if config.youtube.urls:
        videos.extend(video_from_url(url) for url in config.youtube.urls)

    selected = []
    for video in videos:
        if config.youtube.skip_shorts and is_short_url(video.link):
            continue
        if video.video_id in processed:
            continue
        selected.append(video)
        if len(selected) >= config.youtube.limit:
            break

    written = 0
    for video in selected:
        transcript = fetch_transcript(video, config)
        if not transcript:
            continue
        content = (
            f"# {video.title}\n\n"
            f"video_id: {video.video_id}\n"
            f"link: {video.link}\n"
            f"published: {video.published}\n"
            f"author: {video.author}\n\n"
            "## Transcrição\n\n"
            f"{transcript}\n"
        )
        (transcripts_dir / f"{filename_safe(video.title or video.video_id)}.txt").write_text(content, encoding="utf-8")
        processed.add(video.video_id)
        written += 1

    save_state(state_path, processed)
    return {
        "videos_selected": len(selected),
        "transcripts_written": written,
        "transcripts_dir": str(transcripts_dir),
    }


def run_youtube_pipeline(config: PipelineConfig) -> dict[str, int | str]:
    ingest_stats = prepare_youtube_transcripts(config)
    local_config = PipelineConfig(
        input_dir=Path(str(ingest_stats["transcripts_dir"])),
        output_dir=config.output_dir,
        profile=config.profile,
        language=config.language,
        features=config.features,
        openai=config.openai,
        youtube=config.youtube,
    )
    pipeline_stats = run_pipeline(local_config)
    return {**ingest_stats, **pipeline_stats}
