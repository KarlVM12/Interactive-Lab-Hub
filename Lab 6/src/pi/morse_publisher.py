#!/usr/bin/env python3
"""Publish Morse symbols based on APDS-9960 light readings."""

from __future__ import annotations

import json
import logging
import os
import time
import uuid
from collections import deque
from typing import Deque, Optional, Tuple

import board
import busio
import paho.mqtt.client as mqtt
from adafruit_apds9960.apds9960 import APDS9960

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("morse.pi")

MQTT_BROKER = os.getenv("IDD_MQTT_BROKER", "farlab.infosci.cornell.edu")
MQTT_PORT = int(os.getenv("IDD_MQTT_PORT", "1883"))
MQTT_USERNAME = os.getenv("IDD_MQTT_USER", "idd")
MQTT_PASSWORD = os.getenv("IDD_MQTT_PASS", "device@theFarm")
TEAM_TOPIC = os.getenv("IDD_MORSE_TOPIC", "IDD/lab6/morse/team42")

SYMBOL_TOPIC = f"{TEAM_TOPIC}/symbol"
STATUS_TOPIC = f"{TEAM_TOPIC}/status"

SAMPLE_INTERVAL = float(os.getenv("MORSE_SAMPLE_INTERVAL", "0.02"))
BASELINE_WINDOW = int(os.getenv("MORSE_BASELINE_WINDOW", "60"))
DARK_RATIO = float(os.getenv("MORSE_DARK_RATIO", "0.55"))
BRIGHT_RATIO = float(os.getenv("MORSE_BRIGHT_RATIO", "0.80"))
MIN_HOLD = float(os.getenv("MORSE_MIN_HOLD", "0.05"))
DOT_MAX = float(os.getenv("MORSE_DOT_MAX", "0.45"))
HEARTBEAT_INTERVAL = float(os.getenv("MORSE_HEARTBEAT_INTERVAL", "10"))

DEVICE_LABEL = os.getenv("MORSE_DEVICE_LABEL")


def get_device_id() -> str:
    """Return a stable device identifier (MAC if possible)."""
    for interface in ("wlan0", "eth0"):
        path = f"/sys/class/net/{interface}/address"
        try:
            with open(path, "r", encoding="utf-8") as handle:
                value = handle.read().strip()
            if value:
                return value
        except FileNotFoundError:
            continue
    return uuid.uuid4().hex


class AmbientTracker:
    """Maintain a running baseline for ambient light."""

    def __init__(self, window: int, dark_ratio: float, bright_ratio: float) -> None:
        self.samples: Deque[float] = deque(maxlen=window)
        self.baseline: Optional[float] = None
        self.dark_ratio = min(dark_ratio, bright_ratio - 0.05)
        self.bright_ratio = bright_ratio

    def update(self, value: float, locked: bool = False) -> float:
        if not locked:
            self.samples.append(value)
        if self.samples:
            average = sum(self.samples) / len(self.samples)
            if self.baseline is None:
                self.baseline = average
            else:
                self.baseline = (self.baseline * 0.9) + (average * 0.1)
        elif self.baseline is None:
            self.baseline = value or 1.0
        return self.baseline or value or 1.0

    def thresholds(self) -> Tuple[float, float]:
        baseline = max(self.baseline or 1.0, 1.0)
        dark_threshold = baseline * self.dark_ratio
        bright_threshold = baseline * self.bright_ratio
        return dark_threshold, bright_threshold


class MorsePublisher:
    """Read the APDS-9960 and publish dot/dash events over MQTT."""

    def __init__(self) -> None:
        self.device_id = os.getenv("MORSE_DEVICE_ID", get_device_id())
        self.label = DEVICE_LABEL
        self.ambient = AmbientTracker(BASELINE_WINDOW, DARK_RATIO, BRIGHT_RATIO)
        self.block_active = False
        self.block_started_at: Optional[float] = None
        self.last_symbol_sent: Optional[float] = None
        self.last_heartbeat: float = 0.0

        self.client = self._setup_mqtt()
        self.sensor = self._setup_sensor()

    def _setup_mqtt(self) -> mqtt.Client:
        client = mqtt.Client(client_id=f"morse-pi-{uuid.uuid4()}")
        if MQTT_USERNAME:
            client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        client.will_set(
            STATUS_TOPIC,
            json.dumps({"device_id": self.device_id, "status": "offline"}),
            retain=False,
        )
        client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
        client.loop_start()
        logger.info("MQTT connected (topic: %s)", SYMBOL_TOPIC)
        # Ensure heartbeat helper can publish immediately.
        self.client = client
        self._publish_status("online")
        return client

    def _setup_sensor(self) -> APDS9960:
        bus = busio.I2C(board.SCL, board.SDA)
        sensor = APDS9960(bus)
        sensor.enable_color = True
        try:
            sensor.integration_time = 10
            sensor.color_gain = 4
        except Exception:
            logger.debug("Sensor gain/integration adjustment skipped")
        logger.info("APDS-9960 ready (hold ambient light steady for calibration)")
        return sensor

    def _publish_status(self, status: str, **extra) -> None:
        payload = {
            "device_id": self.device_id,
            "label": self.label,
            "status": status,
            "timestamp": time.time(),
        }
        payload.update(extra)
        self.client.publish(STATUS_TOPIC, json.dumps(payload), qos=0, retain=False)

    def _publish_symbol(self, symbol: str, duration: float) -> None:
        payload = {
            "device_id": self.device_id,
            "label": self.label,
            "symbol": symbol,
            "duration": round(duration, 3),
            "timestamp": time.time(),
        }
        self.client.publish(SYMBOL_TOPIC, json.dumps(payload), qos=0, retain=False)
        logger.info("Sent %s (%.3fs)", symbol, duration)

    def calibrate(self) -> None:
        logger.info("Calibrating ambient baseline (%d samples)", BASELINE_WINDOW)
        for _ in range(BASELINE_WINDOW):
            brightness = self._read_brightness()
            self.ambient.update(brightness, locked=False)
            time.sleep(SAMPLE_INTERVAL)
        logger.info("Baseline locked at %.1f", self.ambient.baseline or 0)

    def _read_brightness(self) -> float:
        try:
            _, _, _, clear = self.sensor.color_data
            return float(clear)
        except Exception as exc:
            logger.warning("Sensor read failed: %s", exc)
            time.sleep(0.05)
            return self.ambient.baseline or 0.0

    def run(self) -> None:
        self.calibrate()
        try:
            while True:
                brightness = self._read_brightness()
                baseline = self.ambient.update(
                    brightness, locked=self.block_active
                )
                dark_threshold, bright_threshold = self.ambient.thresholds()
                now_monotonic = time.monotonic()

                if not self.block_active and brightness <= dark_threshold:
                    self.block_active = True
                    self.block_started_at = now_monotonic
                    logger.debug(
                        "Block start @ %.2f (brightness %.1f baseline %.1f)",
                        now_monotonic,
                        brightness,
                        baseline,
                    )
                elif self.block_active and brightness >= bright_threshold:
                    duration = (
                        now_monotonic - self.block_started_at
                        if self.block_started_at is not None
                        else 0.0
                    )
                    self.block_active = False
                    self.block_started_at = None
                    if duration >= MIN_HOLD:
                        symbol = "." if duration <= DOT_MAX else "-"
                        self._publish_symbol(symbol, duration)
                        self.last_symbol_sent = now_monotonic
                elif self.block_active and self.block_started_at:
                    if now_monotonic - self.block_started_at >= DOT_MAX * 3:
                        duration = now_monotonic - self.block_started_at
                        self._publish_symbol("-", duration)
                        self.block_active = False
                        self.block_started_at = None
                        self.last_symbol_sent = now_monotonic

                if (now_monotonic - self.last_heartbeat) >= HEARTBEAT_INTERVAL:
                    self._publish_status(
                        "heartbeat",
                        brightness=round(brightness, 2),
                        baseline=round(baseline, 2),
                    )
                    self.last_heartbeat = now_monotonic

                time.sleep(SAMPLE_INTERVAL)
        except KeyboardInterrupt:
            logger.info("Stopping publisher...")
        finally:
            self._publish_status("offline")
            self.client.loop_stop()
            self.client.disconnect()


def main() -> None:
    publisher = MorsePublisher()
    publisher.run()


if __name__ == "__main__":
    main()
