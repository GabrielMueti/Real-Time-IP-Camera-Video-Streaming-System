"""Load settings from environment variables / a local .env file (never from code)."""
import os
from dataclasses import dataclass
from pathlib import Path


def _load_env_file(path=".env"):
    """Minimal .env reader: KEY=VALUE lines; real environment variables win."""
    file = Path(path)
    if not file.is_file():
        return
    for line in file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


@dataclass
class Settings:
    camera_url: str
    camera_name: str
    display_width: int
    max_reconnects: int
    connect_timeout: float
    record_fps: float


def load_settings():
    _load_env_file()
    try:
        return Settings(
            camera_url=os.environ.get("CAMERA_URL", ""),
            camera_name=os.environ.get("CAMERA_NAME", "Camera 1"),
            display_width=int(os.environ.get("DISPLAY_WIDTH", "960")),
            max_reconnects=int(os.environ.get("MAX_RECONNECTS", "5")),
            connect_timeout=float(os.environ.get("CONNECT_TIMEOUT", "5")),
            record_fps=float(os.environ.get("RECORD_FPS", "20")),
        )
    except ValueError as exc:
        raise ValueError(f"A number in your .env file is not valid: {exc}")
