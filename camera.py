"""Connecting to the camera: reachability check, opening, reconnecting."""
import socket
import time
from urllib.parse import urlparse

import cv2
import requests

from utils import mask_url


class CameraError(Exception):
    """Any problem reaching or reading the camera (message is user-friendly)."""


def check_reachable(url, timeout):
    """Fail fast (no hang) if the camera does not answer."""
    parsed = urlparse(url)
    try:
        if parsed.scheme in ("http", "https"):
            # stream=True: read headers only, don't download an endless MJPEG body
            with requests.get(url, stream=True, timeout=timeout) as resp:
                if resp.status_code in (401, 403):
                    raise CameraError("Camera refused access (check username/password).")
                if resp.status_code >= 400:
                    raise CameraError(f"Camera answered with HTTP {resp.status_code}. Check the URL path.")
        else:  # rtsp: just test that the port accepts a TCP connection
            port = parsed.port or 554
            with socket.create_connection((parsed.hostname, port), timeout=timeout):
                pass
    except CameraError:
        raise
    except (requests.exceptions.RequestException, OSError) as exc:
        raise CameraError(
            f"Cannot reach the camera at {mask_url(url)} within {timeout:g}s. "
            "Is it on, on the same Wi-Fi, and is the port right?"
        ) from exc


def open_camera(url, timeout):
    check_reachable(url, timeout)
    cap = cv2.VideoCapture(url)
    # Best-effort read timeouts (ignored by builds that lack these properties)
    cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, timeout * 1000)
    cap.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, timeout * 1000)
    if not cap.isOpened():
        cap.release()
        raise CameraError("Camera answered, but OpenCV could not open the stream (wrong path/format?).")
    return cap


def reconnect(url, timeout, max_attempts, on_attempt=print):
    """Try to reopen the stream with growing pauses; raise CameraError when exhausted."""
    for attempt in range(1, max_attempts + 1):
        on_attempt(f"Connection lost. Reconnecting ({attempt}/{max_attempts})...")
        try:
            return open_camera(url, timeout)
        except CameraError:
            time.sleep(min(2 * attempt, 10))  # 2s, 4s, 6s ... capped at 10s
    raise CameraError(f"Could not reconnect after {max_attempts} attempts. Giving up.")
