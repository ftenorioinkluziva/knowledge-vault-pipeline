from knowledge_vault_pipeline.config import Features, OpenAIConfig, PipelineConfig
from knowledge_vault_pipeline.pipeline import collect_documents


def test_pipeline_can_collect_specific_audio_file_with_local_whisper(tmp_path, monkeypatch):
    video = tmp_path / "aula.mp4"
    video.write_bytes(b"fake video")

    def fake_transcribe_audio(path, model, max_mb, backend, whisper_model, whisper_language):
        assert path == video
        assert backend == "local-whisper"
        assert whisper_model == "small"
        assert whisper_language == "pt"
        return "Transcrição local do vídeo."

    monkeypatch.setattr("knowledge_vault_pipeline.pipeline.transcribe_audio", fake_transcribe_audio)
    config = PipelineConfig(
        input_dir=tmp_path / "unused",
        input_files=(video,),
        output_dir=tmp_path / "out",
        features=Features(pdf=False, text=False, audio_transcription=True),
        openai=OpenAIConfig(transcription_backend="local-whisper", whisper_model="small", whisper_language="pt"),
    )
    config.vault_ready_dir.mkdir(parents=True)

    documents = collect_documents(config)

    assert len(documents) == 1
    assert documents[0].text == "Transcrição local do vídeo."
