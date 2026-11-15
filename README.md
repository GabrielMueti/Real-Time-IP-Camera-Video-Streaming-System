# Network Camera Viewer

A lightweight Python desktop viewer for IP cameras on your local network. It works with any camera that streams over HTTP (MJPEG) or RTSP, including an Android phone running the **IP Webcam** app.

It shows the live video with an information overlay, saves screenshots, records video, and keeps running when the network misbehaves.

## Features

- Live video in a desktop window (OpenCV)
- Every frame is resized to a fixed width, keeping its aspect ratio
- On-screen overlay: date and time, camera name, frame resolution and estimated FPS
- **S** saves a timestamped screenshot, with an on-screen confirmation
- **R** starts and stops a timestamped video recording, with a red **● REC** timer
- Clear one-line error messages (no tracebacks) for a bad URL, an unreachable camera, a login problem or a lost connection
- Automatic reconnection (limited number of tries) when the stream drops
- Safe shutdown: any recording is saved, the camera is released and every window is closed
- Camera address and settings are kept in a `.env` file that is **never committed**

## Requirements

- Python 3.10 or newer
- A camera (or a phone with the IP Webcam app) on the **same Wi-Fi network** as your computer

Python packages (installed from `requirements.txt`): `opencv-python`, `numpy`, `requests`.

## Setup

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate            # Windows
source .venv/bin/activate         # macOS / Linux

# 2. Install the dependencies
pip install -r requirements.txt
```

## Connect your camera

1. Install **IP Webcam** on your Android phone and connect the phone to the same Wi-Fi as your computer.
2. In the app, tap **Start server**. The screen shows an address such as `http://192.168.1.23:8080`.
3. Your stream URL is that address plus `/video`, for example `http://192.168.1.23:8080/video`. Open it in a browser first to check that the video appears.
4. Copy `.env.example` to a new file named `.env` and put your URL in it:

   ```
   CAMERA_URL=http://192.168.1.23:8080/video
   CAMERA_NAME=Front Door
   ```

`.env` is listed in `.gitignore`, so your camera address and any password stay on your computer.

### Settings

All settings go in `.env`.

| Setting | What it does | Default |
|---|---|---|
| `CAMERA_URL` | Stream address (`http://`, `https://` or `rtsp://`) | required |
| `CAMERA_NAME` | Name shown on the video | `Camera 1` |
| `DISPLAY_WIDTH` | Width in pixels that frames are resized to | `960` |
| `MAX_RECONNECTS` | Reconnect attempts before giving up | `5` |
| `CONNECT_TIMEOUT` | Seconds to wait for the camera to answer | `5` |
| `RECORD_FPS` | Frame rate written into recordings | `20` |

## Run

```bash
python main.py
```

## Controls

Click the video window first so it has focus.

| Key | Action |
|---|---|
| `Esc` | Quit. Any recording is saved and the camera is released |
| `S` | Save a screenshot to `screenshots/` |
| `R` | Start or stop a recording in `recordings/` |

Files are named with the date and time, so a new file never overwrites an old one, for example `screenshot_2026-11-15_14-24-00_868.jpg` and `recording_2026-11-15_15-54-36_064.mp4`. The `screenshots/` and `recordings/` folders are created automatically and are ignored by Git.

## Project structure

| File | What it does |
|---|---|
| `main.py` | The video loop, overlays, key handling and safe shutdown |
| `camera.py` | Checks the camera answers, opens the stream, reconnects after a drop |
| `recorder.py` | Video recording (`cv2.VideoWriter`) |
| `config.py` | Reads settings from `.env` or environment variables |
| `utils.py` | URL checks, resizing maths, file names, FPS estimate |
| `tests/test_utils.py` | Unit tests for the helper functions |
| `.env.example` | Template for your own `.env` |

## Tests

Run the unit tests:

```bash
python -m unittest discover tests
```

The ten manual tests (live stream, invalid URL, unavailable camera, overlays, resizing, screenshot, recording, connection drop, Esc during recording, Ctrl+C during recording) were run against a real phone camera and are described in the project report.

## Troubleshooting

| Message or problem | What to check |
|---|---|
| `No camera URL set` | You haven't created `.env`, or `CAMERA_URL` is empty |
| `Invalid URL` | The address must start with `http://`, `https://` or `rtsp://` and have a host |
| `Cannot reach the camera` | Is the app's server running? Are the phone and computer on the same Wi-Fi? Is the port right (usually `8080`)? |
| `Camera refused access` | Wrong username or password in the URL |
| Keys do nothing | Click the video window so it has focus |

## Known limitations

- **Ctrl+C is ignored while the video window is active in the PyCharm Run console.** Use **Esc** or the window's close button to stop the program.
- Recordings use the fixed `RECORD_FPS` value, not the camera's real frame rate, so a recording can play slightly faster or slower than real time. Set `RECORD_FPS` close to the FPS shown on screen if that bothers you.
- Recordings are plain files and are never deleted automatically.

## Privacy and responsible use

Only use a camera that you own or have clear permission to use, and never point it at people who have not agreed to be recorded. The viewer always shows a red **● REC** indicator while it is saving video. Never commit your camera address, username, password, screenshots or recordings to GitHub.
