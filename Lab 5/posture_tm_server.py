#!/usr/bin/env python3
"""Static file server + MiniTFT display bridge for the posture tmPose web app."""
from __future__ import annotations

import json
import threading
import time
from functools import partial
from http.server import SimpleHTTPRequestHandler
from pathlib import Path
from socketserver import TCPServer
from typing import Any, Dict, Optional

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent
WEB_DIR = ROOT
STATE_LOCK = threading.Lock()
LATEST_STATE: Optional[Dict[str, Any]] = None
STATE_VERSION = 0
PORT = 8000


class DisplayController:
    WIDTH = 240
    HEIGHT = 135

    def __init__(self) -> None:
        self.display = None
        try:
            import board
            import busio
            import digitalio
            import adafruit_rgb_display.st7789 as st7789

            spi = busio.SPI(clock=board.SCK, MOSI=board.MOSI)
            # Pi 5 MiniTFT wiring uses GPIO5 for CS to avoid CE0 contention
            try:
                cs_pin = digitalio.DigitalInOut(board.D5)
            except ValueError:
                cs_pin = digitalio.DigitalInOut(board.CE0)
            dc_pin = digitalio.DigitalInOut(board.D25)
            rst_pin = digitalio.DigitalInOut(board.D24)
            self.display = st7789.ST7789(
                spi,
                rotation=90,
                width=self.HEIGHT,
                height=self.WIDTH,
                x_offset=53,
                y_offset=40,
                cs=cs_pin,
                dc=dc_pin,
                rst=rst_pin,
                baudrate=24_000_000,
            )
            print("[posture_tm_server] MiniTFT ready.")
        except Exception as exc:  # noqa: BLE001
            print(f"[posture_tm_server] MiniTFT not available: {exc}")
            self.display = None
        self.font_large = ImageFont.load_default()
        self.font_small = ImageFont.load_default()

    def show_state(self, state: Optional[Dict[str, Any]]) -> None:
        if self.display is None:
            return
        label = (state or {}).get("label", "unknown") or "unknown"
        confidence = float((state or {}).get("confidence", 0.0))
        ratio = float((state or {}).get("ratio", 0.0))
        predictions = state.get("predictions", []) if state else []

        palette = {
            "upright": ((22, 120, 49), "UPRIGHT", "Nice posture"),
            "leaning": ((210, 130, 20), "LEAN", "Center yourself"),
            "slouching": ((180, 25, 45), "SLOUCH", "Sit taller"),
            "unknown": ((50, 50, 50), "NO SIGNAL", "Check camera"),
        }
        bg_color, title, subtitle = palette.get(label, palette["unknown"])
        image = Image.new("RGB", (self.WIDTH, self.HEIGHT), bg_color)
        draw = ImageDraw.Draw(image)

        draw.text((10, 10), title, font=self.font_large, fill=(255, 255, 255))
        draw.text((10, 30), subtitle, font=self.font_small, fill=(255, 255, 255))
        draw.text((10, 50), f"{confidence*100:4.1f}%", font=self.font_large, fill=(255, 255, 255))

        bar_x0, bar_y0 = 10, 85
        bar_x1, bar_y1 = self.WIDTH - 10, 105
        draw.rectangle([bar_x0, bar_y0, bar_x1, bar_y1], outline=(255, 255, 255), width=2)
        fill = bar_x0 + int((bar_x1 - bar_x0) * max(0.0, min(1.0, ratio)))
        draw.rectangle([bar_x0, bar_y0, fill, bar_y1], fill=(255, 255, 255))

        baseline = 115
        for idx, pred in enumerate(predictions[:3]):
            text = f"{pred['label'][:6]} {(pred['probability']*100):4.1f}%"
            draw.text((10 + idx * 75, baseline), text, font=self.font_small, fill=(0, 0, 0))

        self.display.image(image)


DISPLAY = DisplayController()


def display_worker() -> None:
    last_version = -1
    while True:
        with STATE_LOCK:
            version = STATE_VERSION
            state = json.loads(json.dumps(LATEST_STATE)) if LATEST_STATE else None
        if version != last_version:
            DISPLAY.show_state(state)
            last_version = version
        time.sleep(0.1)


def update_state(payload: Dict[str, Any]) -> None:
    global LATEST_STATE, STATE_VERSION
    with STATE_LOCK:
        LATEST_STATE = payload
        STATE_VERSION += 1


class PostureHandler(SimpleHTTPRequestHandler):
    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/posture-update":
            self.send_error(404, "Unknown endpoint")
            return
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)
        try:
            payload = json.loads(raw)
            update_state(payload)
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
            return
        self.send_response(204)
        self.end_headers()


def main() -> None:
    display_thread = threading.Thread(target=display_worker, daemon=True)
    display_thread.start()

    handler = partial(PostureHandler, directory=str(WEB_DIR))
    with TCPServer(("", PORT), handler) as httpd:
        print(f"Serving posture web app at http://localhost:{PORT}/posture_tm_web/")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Shutting down...")


if __name__ == "__main__":
    main()
