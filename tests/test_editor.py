import sys, os; sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import os
import wave
import math

from intelligent_video.editor import VideoEditor
import webrtcvad_stub
import intelligent_video.editor as editor


def _write_wav(path, samples, sr):
    with wave.open(path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        import struct
        ints = [int(max(-1.0, min(1.0, s)) * 32767) for s in samples]
        frames = struct.pack('<' + 'h' * len(ints), *ints)
        wf.writeframes(frames)

def generate_test_audio(path):
    sr = 16000
    tone = [math.sin(2 * math.pi * 440 * t / sr) for t in range(sr)]
    silence = [0.0] * int(sr * 0.6)
    audio = tone + silence + tone
    _write_wav(path, audio, sr)


def test_split_on_silence(tmp_path):
    audio_path = tmp_path / "sample.wav"
    generate_test_audio(str(audio_path))

    editor = VideoEditor(str(audio_path))
    segments = editor.split_on_silence(output_dir=str(tmp_path))

    assert len(segments) == 2
    for seg in segments:
        assert os.path.exists(seg)
        with wave.open(seg, 'rb') as wf:
            duration = wf.getnframes() / wf.getframerate()
            assert 0.9 <= duration <= 1.1


def test_split_on_silence_vad(tmp_path, monkeypatch):
    audio_path = tmp_path / "sample.wav"
    generate_test_audio(str(audio_path))

    monkeypatch.setattr(editor, "_import_librosa", lambda: None)
    monkeypatch.setattr(editor, "_import_webrtcvad", lambda: webrtcvad_stub)

    editor_instance = VideoEditor(str(audio_path))
    segments = editor_instance.split_on_silence(output_dir=str(tmp_path))

    assert len(segments) == 2
    for seg in segments:
        assert os.path.exists(seg)
        with wave.open(seg, 'rb') as wf:
            duration = wf.getnframes() / wf.getframerate()
            assert 0.9 <= duration <= 1.1

