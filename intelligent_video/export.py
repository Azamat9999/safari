"""Export utilities for rendering final video outputs."""

from pathlib import Path
import subprocess

class Exporter:
    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        self.ffmpeg = ffmpeg_path

    def render(self, input_video: Path, output_video: Path, codec: str = "libx264") -> None:
        subprocess.run([self.ffmpeg, '-i', str(input_video), '-c:v', codec, str(output_video)], check=True)
