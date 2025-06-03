"""Input module for loading raw data and handling local/remote models."""

from pathlib import Path
import requests

class InputHandler:
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def download_model(self, url: str) -> Path:
        """Download model if not present in cache."""
        fname = self.cache_dir / Path(url).name
        if not fname.exists():
            response = requests.get(url, stream=True)
            with open(fname, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
        return fname

    def load_script(self, path: Path) -> bytes:
        return path.read_bytes()
