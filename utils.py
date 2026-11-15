"""Small, dependency-free helpers (easy to unit test)."""
import time
from datetime import datetime
from urllib.parse import urlparse

ALLOWED_SCHEMES = ("http", "https", "rtsp")


def validate_url(url):
    """Return the URL if it looks valid, otherwise raise ValueError."""
    if not url or not url.strip():
        raise ValueError("No camera URL set. Put CAMERA_URL in your .env file.")
    url = url.strip()
    parsed = urlparse(url)
    if parsed.scheme not in ALLOWED_SCHEMES:
        raise ValueError(
            f"Invalid URL scheme '{parsed.scheme}'. Use http://, https:// or rtsp://."
        )
    if not parsed.hostname:
        raise ValueError("Invalid URL: no host (IP address) found.")
    try:
        parsed.port  # raises ValueError if the port is not a number / out of range
    except ValueError:
        raise ValueError("Invalid URL: the port must be a number from 0 to 65535.")
    return url


def mask_url(url):
    """Hide credentials so a URL can be printed safely."""
    parsed = urlparse(url)
    if parsed.username or parsed.password:
        host = parsed.hostname + (f":{parsed.port}" if parsed.port else "")
        return parsed._replace(netloc=f"***:***@{host}").geturl()
    return url


def target_size(width, height, display_width):
    """New (w, h) at display_width, keeping aspect ratio.

    Example: 1920x1080 at 960 -> (960, round(1080 * 960 / 1920)) = (960, 540).
    """
    if width <= 0 or height <= 0 or display_width <= 0:
        raise ValueError("Sizes must be positive.")
    return display_width, max(1, round(height * display_width / width))


def timestamped_name(prefix, ext, now=None):
    """e.g. screenshot_2026-11-11_08-31-05.jpg. Sub-second part avoids overwrites."""
    now = now or datetime.now()
    return f"{prefix}_{now:%Y-%m-%d_%H-%M-%S}_{now.microsecond // 1000:03d}.{ext}"


def format_elapsed(seconds):
    seconds = int(seconds)
    return f"{seconds // 60:02d}:{seconds % 60:02d}"


class FpsEstimator:
    """FPS from the time between frames, smoothed with an exponential average."""

    def __init__(self, smoothing=0.1):
        self.smoothing = smoothing
        self.fps = 0.0
        self._last = None

    def tick(self, now=None):
        now = time.perf_counter() if now is None else now
        if self._last is not None and now > self._last:
            instant = 1.0 / (now - self._last)
            self.fps = instant if self.fps == 0 else (
                self.smoothing * instant + (1 - self.smoothing) * self.fps
            )
        self._last = now
        return self.fps
