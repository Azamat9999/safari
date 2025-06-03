import wave
import struct
import math

# Minimal stub of librosa-like functions for silence detection

def load(path, sr=None, mono=True):
    with wave.open(path, 'rb') as wf:
        channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        framerate = wf.getframerate()
        nframes = wf.getnframes()
        frames = wf.readframes(nframes)
    fmt_map = {1: 'b', 2: 'h', 4: 'i'}
    fmt = '<' + fmt_map[sampwidth] * (len(frames) // sampwidth)
    data = struct.unpack(fmt, frames)
    if channels > 1:
        mono_data = []
        for i in range(0, len(data), channels):
            mono_sample = sum(data[i:i+channels]) / channels
            mono_data.append(mono_sample)
        data = mono_data
    max_amp = float(2 ** (8 * sampwidth - 1))
    audio = [sample / max_amp for sample in data]
    if sr and sr != framerate:
        # naive resample
        factor = sr / framerate
        resampled = []
        for i in range(int(len(audio) * factor)):
            resampled.append(audio[int(i / factor)])
        audio = resampled
        framerate = sr
    return audio, framerate

class effects:
    @staticmethod
    def split(y, top_db=40, frame_length=2048, hop_length=512):
        """Return non-silent intervals of ``y``."""
        threshold = 10 ** (-top_db / 20)
        flags = []
        for i in range(0, len(y), hop_length):
            window = y[i:i + frame_length]
            if not window:
                break
            rms = math.sqrt(sum(s * s for s in window) / len(window))
            flags.append(rms > threshold)

        intervals = []
        start = None
        for idx, flag in enumerate(flags):
            if flag:
                if start is None:
                    start = idx * hop_length
            else:
                if start is not None:
                    end = idx * hop_length
                    intervals.append((start, min(end, len(y))) )
                    start = None
        if start is not None:
            intervals.append((start, len(y)))
        return intervals

