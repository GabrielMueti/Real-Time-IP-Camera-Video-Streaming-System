"""Video recording wrapper around cv2.VideoWriter."""
import os
import time

import cv2

from utils import timestamped_name


class Recorder:
    def __init__(self, folder="recordings", fps=20.0):
        self.folder = folder
        self.fps = fps
        self._writer = None
        self._size = None
        self._started = 0.0
        self.path = None

    @property
    def active(self):
        return self._writer is not None

    @property
    def elapsed(self):
        return time.time() - self._started if self.active else 0.0

    def start(self, frame):
        os.makedirs(self.folder, exist_ok=True)
        h, w = frame.shape[:2]
        self._size = (w, h)
        self.path = os.path.join(self.folder, timestamped_name("recording", "mp4"))
        self._writer = cv2.VideoWriter(
            self.path, cv2.VideoWriter_fourcc(*"mp4v"), self.fps, self._size
        )
        if not self._writer.isOpened():
            self._writer = None
            raise OSError("Could not create the video file (codec problem?).")
        self._started = time.time()

    def write(self, frame):
        if not self.active:
            return
        h, w = frame.shape[:2]
        if (w, h) != self._size:  # a mismatched size makes the file unplayable
            frame = cv2.resize(frame, self._size)
        self._writer.write(frame)

    def stop(self):
        """Finish and save the file. Safe to call when not recording."""
        if self._writer is not None:
            self._writer.release()
            self._writer = None
            return self.path
        return None
