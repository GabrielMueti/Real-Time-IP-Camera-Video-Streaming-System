"""IP camera viewer.  Controls: Esc = quit, S = screenshot, R = start/stop recording."""
import os
import sys
import time

import cv2

from camera import CameraError, open_camera, reconnect
from config import load_settings
from recorder import Recorder
from utils import (FpsEstimator, format_elapsed, mask_url, target_size,
                   timestamped_name, validate_url)

WINDOW = "IP Camera Viewer"
FONT = cv2.FONT_HERSHEY_SIMPLEX
WHITE, RED, GREEN = (255, 255, 255), (0, 0, 255), (0, 200, 0)  # BGR, not RGB!


def put_text(img, text, org, color=WHITE, scale=0.55):
    """Text with a dark outline so it stays readable on any background."""
    cv2.putText(img, text, org, FONT, scale, (0, 0, 0), 3, cv2.LINE_AA)
    cv2.putText(img, text, org, FONT, scale, color, 1, cv2.LINE_AA)


def resize_frame(frame, display_width):
    h, w = frame.shape[:2]
    new_w, new_h = target_size(w, h, display_width)
    return cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)


def draw_overlay(frame, name, fps, recorder, message):
    h, w = frame.shape[:2]
    put_text(frame, time.strftime("%Y-%m-%d %H:%M:%S"), (10, 22))
    put_text(frame, name, (10, 44))
    put_text(frame, f"{w}x{h}  {fps:4.1f} FPS", (10, 66))
    if recorder.active:
        put_text(frame, f"● REC {format_elapsed(recorder.elapsed)}", (w - 150, 22), RED, 0.6)
    if message[0] and time.time() < message[1]:
        put_text(frame, message[0], (10, h - 12), GREEN, 0.6)


def save_screenshot(frame):
    os.makedirs("screenshots", exist_ok=True)
    path = os.path.join("screenshots", timestamped_name("screenshot", "jpg"))
    if not cv2.imwrite(path, frame):
        raise OSError("Could not write the screenshot file.")
    return path


def run(settings):
    url = validate_url(settings.camera_url)
    print(f"Connecting to {mask_url(url)} ...")
    cap = open_camera(url, settings.connect_timeout)
    recorder = Recorder(fps=settings.record_fps)
    fps = FpsEstimator()
    message = ["", 0.0]  # on-screen confirmation text and expiry time
    failed_reads = 0
    try:
        while True:
            ok, frame = cap.read()
            if not ok or frame is None:
                failed_reads += 1
                if failed_reads < 3:  # tolerate a glitchy frame or two
                    continue
                cap.release()
                cap = reconnect(url, settings.connect_timeout, settings.max_reconnects)
                failed_reads = 0
                fps = FpsEstimator()
                print("Reconnected.")
                continue
            failed_reads = 0

            frame = resize_frame(frame, settings.display_width)
            clean = frame.copy()  # screenshots/recordings stay free of overlay text
            draw_overlay(frame, settings.camera_name, fps.tick(), recorder, message)
            if recorder.active:
                recorder.write(clean)
            cv2.imshow(WINDOW, frame)

            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # Esc
                print("Esc pressed - shutting down.")
                break
            if cv2.getWindowProperty(WINDOW, cv2.WND_PROP_VISIBLE) < 1:
                break  # window closed with the X button
            if key in (ord("s"), ord("S")):
                try:
                    path = save_screenshot(clean)
                    message[:] = [f"Saved {os.path.basename(path)}", time.time() + 2]
                    print(f"Screenshot saved: {path}")
                except OSError as exc:
                    message[:] = [f"Screenshot failed: {exc}", time.time() + 3]
            elif key in (ord("r"), ord("R")):
                if recorder.active:
                    print(f"Recording saved: {recorder.stop()}")
                else:
                    try:
                        recorder.start(clean)
                        print(f"Recording to {recorder.path}")
                    except OSError as exc:
                        message[:] = [f"Cannot record: {exc}", time.time() + 3]
    finally:  # runs on Esc, Ctrl+C and errors
        saved = recorder.stop()
        if saved:
            print(f"Recording saved: {saved}")
        cap.release()
        cv2.destroyAllWindows()


def main():
    try:
        run(load_settings())
    except KeyboardInterrupt:
        print("\nInterrupted (Ctrl+C). Closed cleanly.")
    except (ValueError, CameraError, OSError) as exc:
        print(f"Error: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
