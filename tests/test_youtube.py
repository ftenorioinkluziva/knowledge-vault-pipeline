from knowledge_vault_pipeline.youtube import extract_caption_text, parse_youtube_rss, video_from_url


def test_parse_youtube_rss():
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns:yt="http://www.youtube.com/xml/schemas/2015" xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <yt:videoId>abc123</yt:videoId>
    <title>Video Teste</title>
    <link rel="alternate" href="https://www.youtube.com/watch?v=abc123"/>
    <author><name>Canal</name></author>
    <published>2026-01-01T00:00:00+00:00</published>
  </entry>
</feed>"""
    videos = parse_youtube_rss(xml)
    assert len(videos) == 1
    assert videos[0].video_id == "abc123"
    assert videos[0].title == "Video Teste"


def test_video_from_url_watch_url():
    video = video_from_url("https://www.youtube.com/watch?v=abc123")
    assert video.video_id == "abc123"


def test_extract_caption_text_accepts_common_shapes():
    text = extract_caption_text(
        [
            {"captions": "texto 1"},
            {"transcript": [{"text": "texto 2"}, {"caption": "texto 3"}]},
        ]
    )
    assert "texto 1" in text
    assert "texto 2" in text
    assert "texto 3" in text

