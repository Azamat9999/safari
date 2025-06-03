import os
import struct
import wave
from typing import List, Tuple


def _import_librosa():
    try:
        import librosa  # type: ignore
        return librosa
    except Exception:
        return None


def _import_webrtcvad():
    try:
        import webrtcvad  # type: ignore
        return webrtcvad
    except Exception:
        return None


def _load_audio(path: str, sr: int | None = None) -> Tuple[List[float], int]:
    """Load audio using librosa if available, otherwise the bundled stub."""
    librosa = _import_librosa()
    if librosa is None:
        import librosa_stub as librosa  # local minimal implementation
    return librosa.load(path, sr=sr)


class VideoEditor:
    def __init__(self, media_path: str):
        self.media_path = media_path

    @staticmethod
    def _write_wav(path: str, audio: List[float], sr: int) -> None:
        """Write a mono wav file from float samples."""
        with wave.open(path, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            ints = [int(max(-1.0, min(1.0, s)) * 32767) for s in audio]
            frames = struct.pack('<' + 'h' * len(ints), *ints)
            wf.writeframes(frames)

    def _split_with_vad(self, audio: List[float], sr: int, vad_module) -> List[Tuple[int, int]]:
        """Return non-silent intervals using webrtcvad."""
        vad = vad_module.Vad(1)
        frame_ms = 30
        frame_len = int(sr * frame_ms / 1000)
        bytes_per_sample = 2
        pcm = b''.join(struct.pack('<h', int(max(-1.0, min(1.0, s)) * 32767)) for s in audio)

        intervals: List[Tuple[int, int]] = []
        start = None
        for i in range(0, len(pcm), frame_len * bytes_per_sample):
            frame = pcm[i:i + frame_len * bytes_per_sample]
            if len(frame) < frame_len * bytes_per_sample:
                frame = frame + b'\x00' * (frame_len * bytes_per_sample - len(frame))
            is_speech = vad.is_speech(frame, sr)
            if is_speech:
                if start is None:
                    start = i // bytes_per_sample
            else:
                if start is not None:
                    end = i // bytes_per_sample
                    intervals.append((start, min(end, len(audio))))
                    start = None
        if start is not None:
            intervals.append((start, len(audio)))
        return intervals

    def split_on_silence(self, top_db: int = 40, min_len: float = 0.5, output_dir: str | None = None) -> List[str]:
        """Split the media on silent intervals using librosa or webrtcvad."""
        librosa = _import_librosa()
        vad_module = None
        if librosa is None:
            vad_module = _import_webrtcvad()
            if vad_module is None:
                import librosa_stub as librosa  # fallback stub
        audio, sr = _load_audio(self.media_path, sr=16000 if vad_module else None)
        if vad_module:
            intervals = self._split_with_vad(audio, sr, vad_module)
        else:
            intervals = librosa.effects.split(audio, top_db=top_db)

        output_dir = output_dir or os.path.dirname(self.media_path)
        base = os.path.splitext(os.path.basename(self.media_path))[0]
        segment_paths: List[str] = []

        min_samples = int(min_len * sr)
        for i, (start, end) in enumerate(intervals):
            if end - start < min_samples:
                continue
            segment_audio = audio[start:end]
            seg_path = os.path.join(output_dir, f"{base}_segment_{i}.wav")
            self._write_wav(seg_path, segment_audio, sr)
            segment_paths.append(seg_path)
        return segment_paths

