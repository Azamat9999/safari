class Vad:
    def __init__(self, aggressiveness=1):
        # aggressiveness affects sensitivity. We just store a threshold.
        self.threshold = 500 >> aggressiveness

    def is_speech(self, frame: bytes, sample_rate: int) -> bool:
        import struct
        count = len(frame) // 2
        if count == 0:
            return False
        samples = struct.unpack('<' + 'h' * count, frame[:count*2])
        return max(abs(s) for s in samples) > self.threshold
