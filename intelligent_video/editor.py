import os
import struct
import wave
from typing import List

try:
    import librosa
except Exception:
    import librosa_stub as librosa


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

    def split_on_silence(self, top_db: int = 40, min_len: float = 0.5, output_dir: str | None = None) -> List[str]:
        """Split the media on silent intervals using librosa and return segment paths."""
        audio, sr = librosa.load(self.media_path, sr=None)
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

