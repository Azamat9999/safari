"""Speech processing: STT via Whisper and TTS via various models."""

from pathlib import Path
from typing import Iterable

import whisper

class SpeechRecognizer:
    def __init__(self, model_name: str = "openai/whisper-large", device: str = "cpu"):
        self.model = whisper.load_model(model_name).to(device)

    def transcribe(self, audio_path: Path) -> str:
        """Transcribe audio using Whisper."""
        result = self.model.transcribe(str(audio_path))
        return result["text"]

class TextToSpeech:
    def __init__(self, model_name: str):
        self.model_name = model_name
        # placeholder for loading tts model

    def synthesize(self, text: str, **kwargs) -> Path:
        """Return path to synthesized speech audio."""
        raise NotImplementedError
