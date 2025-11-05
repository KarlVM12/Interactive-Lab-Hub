#!/usr/bin/env python3
"""Morse code MQTT bridge and web dashboard."""

from __future__ import annotations

try:
    import eventlet  # type: ignore

    eventlet.monkey_patch()
    ASYNC_MODE = "eventlet"
except ImportError:  # pragma: no cover
    ASYNC_MODE = "threading"

import json
import logging
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Dict, List, Optional, Tuple

import paho.mqtt.client as mqtt
from flask import Flask, jsonify, render_template
from flask_socketio import SocketIO, emit

if __package__:
    from .morse import decode_morse, VALID_SYMBOLS
else:  # pragma: no cover - allows `python src/server/app.py`
    from pathlib import Path as _Path
    import sys as _sys

    _sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
    from server.morse import decode_morse, VALID_SYMBOLS  # type: ignore  # noqa: E402

BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = BASE_DIR / "templates"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("morse.server")

MQTT_BROKER = os.getenv("IDD_MQTT_BROKER", "farlab.infosci.cornell.edu")
MQTT_PORT = int(os.getenv("IDD_MQTT_PORT", "1883"))
MQTT_USERNAME = os.getenv("IDD_MQTT_USER", "idd")
MQTT_PASSWORD = os.getenv("IDD_MQTT_PASS", "device@theFarm")

TEAM_TOPIC = os.getenv("IDD_MORSE_TOPIC", "IDD/lab6/morse/coolguys")
SYMBOL_TOPIC = f"{TEAM_TOPIC}/symbol"
STATUS_TOPIC = f"{TEAM_TOPIC}/status"

LETTER_TIMEOUT = float(os.getenv("MORSE_LETTER_TIMEOUT", "3.5"))
WORD_TIMEOUT = float(os.getenv("MORSE_WORD_TIMEOUT", "6.0"))
STALE_TIMEOUT = float(os.getenv("MORSE_STALE_TIMEOUT", "20.0"))
MAX_MESSAGE_LEN = int(os.getenv("MORSE_MAX_MESSAGE", "160"))
HISTORY_WINDOW = 18

app = Flask(__name__, template_folder=str(TEMPLATE_DIR))
socketio = SocketIO(app, cors_allowed_origins="*", async_mode=ASYNC_MODE)


@dataclass
class DeviceState:
    """Track the in-flight Morse state for one device."""

    device_id: str
    display_name: Optional[str] = None
    current_symbols: List[Dict[str, float]] = field(default_factory=list)
    decoded_message: str = ""
    history: List[Dict[str, str]] = field(default_factory=list)
    last_update: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_symbol_at: Optional[datetime] = None
    last_letter_at: Optional[datetime] = None
    last_space_at: Optional[datetime] = None
    awaiting_word_gap: bool = False
    total_symbols: int = 0
    is_online: bool = True
    last_letter: Optional[str] = None
    last_pattern: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.display_name:
            sanitized = self.device_id.replace(":", "").replace("-", "")
            tail = sanitized[-4:].upper() if sanitized else self.device_id[:4].upper()
            self.display_name = f"Pi-{tail}"

    def touch(self, event_time: datetime) -> None:
        self.last_update = event_time
        self.is_online = True

    def add_symbol(
        self, symbol: str, duration: float, event_time: datetime
    ) -> None:
        entry = {
            "type": "symbol",
            "symbol": symbol,
            "duration": duration,
            "timestamp": event_time.isoformat(),
        }
        self.current_symbols.append(entry)
        self.history.append(entry)
        self._trim_history()
        self.last_symbol_at = event_time
        self.awaiting_word_gap = False
        self.total_symbols += 1
        self.touch(event_time)

    def finalize_letter(self, event_time: datetime) -> Optional[Tuple[str, str]]:
        pattern = "".join(item["symbol"] for item in self.current_symbols)
        if not pattern:
            return None
        letter = decode_morse(pattern)
        entry = {
            "type": "letter",
            "letter": letter,
            "pattern": pattern,
            "timestamp": event_time.isoformat(),
        }
        self.decoded_message += letter
        if len(self.decoded_message) > MAX_MESSAGE_LEN:
            self.decoded_message = self.decoded_message[-MAX_MESSAGE_LEN:]
        self.history.append(entry)
        self._trim_history()
        self.last_letter = letter
        self.last_pattern = pattern
        self.current_symbols.clear()
        self.awaiting_word_gap = True
        self.last_letter_at = event_time
        self.touch(event_time)
        return letter, pattern

    def add_space(self, event_time: datetime) -> bool:
        if not self.decoded_message or self.decoded_message.endswith(" "):
            return False
        self.decoded_message += " "
        self.history.append(
            {"type": "space", "timestamp": event_time.isoformat()}
        )
        self._trim_history()
        self.awaiting_word_gap = False
        self.last_space_at = event_time
        self.touch(event_time)
        return True

    def clear(self, event_time: datetime) -> None:
        self.current_symbols.clear()
        self.decoded_message = ""
        self.history.append({"type": "clear", "timestamp": event_time.isoformat()})
        self._trim_history()
        self.awaiting_word_gap = False
        self.last_letter_at = None
        self.last_symbol_at = None
        self.last_letter = None
        self.last_pattern = None
        self.touch(event_time)

    def as_dict(self) -> Dict[str, object]:
        return {
            "device_id": self.device_id,
            "display_name": self.display_name,
            "current_sequence": "".join(
                item["symbol"] for item in self.current_symbols
            ),
            "current_symbols": [
                dict(item) for item in self.current_symbols
            ],
            "decoded_message": self.decoded_message,
            "history": [dict(item) for item in self.history],
            "last_update": self.last_update.isoformat(),
            "last_symbol_at": self.last_symbol_at.isoformat()
            if self.last_symbol_at
            else None,
            "last_letter_at": self.last_letter_at.isoformat()
            if self.last_letter_at
            else None,
            "total_symbols": self.total_symbols,
            "is_online": self.is_online,
            "last_letter": self.last_letter,
            "last_pattern": self.last_pattern,
        }

    def _trim_history(self) -> None:
        if len(self.history) > HISTORY_WINDOW:
            del self.history[:-HISTORY_WINDOW]


class MorseController:
    """Coordinate device state transitions and websocket broadcasts."""

    def __init__(
        self,
        socketio_instance: SocketIO,
        letter_timeout: float,
        word_timeout: float,
        stale_timeout: float,
    ) -> None:
        self.socketio = socketio_instance
        self.letter_timeout = letter_timeout
        self.word_timeout = word_timeout
        self.stale_timeout = stale_timeout
        self.devices: Dict[str, DeviceState] = {}
        self._lock = Lock()
        self.socketio.start_background_task(self._idle_watcher)

    def snapshot(self) -> List[Dict[str, object]]:
        with self._lock:
            return [device.as_dict() for device in self.devices.values()]

    def ingest_symbol(self, payload: Dict[str, object]) -> None:
        symbol = payload.get("symbol")
        if symbol not in VALID_SYMBOLS:
            logger.debug("Ignoring payload without symbol: %s", payload)
            return

        device_id = (
            payload.get("device_id")
            or payload.get("mac")
            or payload.get("id")
        )
        if not device_id:
            logger.warning("Dropping event without device id: %s", payload)
            return

        display_name = payload.get("label") or payload.get("name")
        try:
            duration = float(payload.get("duration", 0.0))
        except (TypeError, ValueError):
            duration = 0.0

        timestamp = payload.get("timestamp")
        if isinstance(timestamp, (int, float)):
            event_time = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        else:
            event_time = datetime.now(timezone.utc)

        with self._lock:
            device = self.devices.get(device_id)
            if not device:
                device = DeviceState(device_id=str(device_id), display_name=display_name)
                self.devices[device_id] = device
            elif display_name:
                device.display_name = str(display_name)

            device.add_symbol(str(symbol), duration, event_time)
            snapshot = device.as_dict()

        socketio.emit(
            "device_update",
            {
                "event": "symbol",
                "symbol": symbol,
                "duration": duration,
                "device": snapshot,
            },
            namespace="/",
        )
        logger.info(
            "Symbol %s (%.2fs) from %s",
            symbol,
            duration,
            snapshot["display_name"],
        )

    def clear_device(self, device_id: str) -> Optional[Dict[str, object]]:
        with self._lock:
            device = self.devices.get(device_id)
            if not device:
                return None
            now = datetime.now(timezone.utc)
            device.clear(now)
            return device.as_dict()

    def _idle_watcher(self) -> None:
        """Resolve letters and detect offline devices."""
        while True:
            self.socketio.sleep(0.25)
            now = datetime.now(timezone.utc)
            letter_events: List[Tuple[Dict[str, object], str, str]] = []
            space_events: List[Dict[str, object]] = []
            status_events: List[Dict[str, object]] = []

            with self._lock:
                for device in self.devices.values():
                    if device.current_symbols and device.last_symbol_at:
                        delta = (now - device.last_symbol_at).total_seconds()
                        if delta >= self.letter_timeout:
                            resolved = device.finalize_letter(now)
                            if resolved:
                                letter_events.append(
                                    (device.as_dict(), resolved[0], resolved[1])
                                )
                    elif (
                        device.awaiting_word_gap
                        and device.last_letter_at
                        and (now - device.last_letter_at).total_seconds()
                        >= self.word_timeout
                    ):
                        if device.add_space(now):
                            space_events.append(device.as_dict())

                    if device.is_online and (
                        now - device.last_update
                    ).total_seconds() >= self.stale_timeout:
                        device.is_online = False
                        status_events.append(device.as_dict())

            for snapshot, letter, pattern in letter_events:
                socketio.emit(
                    "device_update",
                    {
                        "event": "letter",
                        "letter": letter,
                        "pattern": pattern,
                        "device": snapshot,
                    },
                    namespace="/",
                )
                logger.info(
                    "Letter %s (%s) resolved for %s",
                    letter,
                    pattern,
                    snapshot["display_name"],
                )

            for snapshot in space_events:
                socketio.emit(
                    "device_update",
                    {"event": "space", "device": snapshot},
                    namespace="/",
                )
                logger.info("Word break inserted for %s", snapshot["display_name"])

            for snapshot in status_events:
                socketio.emit(
                    "device_update",
                    {"event": "status", "device": snapshot},
                    namespace="/",
                )
                logger.info("%s marked offline", snapshot["display_name"])


controller = MorseController(
    socketio_instance=socketio,
    letter_timeout=LETTER_TIMEOUT,
    word_timeout=WORD_TIMEOUT,
    stale_timeout=STALE_TIMEOUT,
)


@app.route("/")
def index() -> str:
    return render_template(
        "morse_grid.html",
        symbol_topic=SYMBOL_TOPIC,
        status_topic=STATUS_TOPIC,
        letter_timeout=LETTER_TIMEOUT,
        word_timeout=WORD_TIMEOUT,
    )


@app.route("/api/state")
def api_state():
    return jsonify({"devices": controller.snapshot(), "topic": SYMBOL_TOPIC})


@socketio.on("connect")
def handle_connect():
    emit(
        "state_snapshot",
        {
            "devices": controller.snapshot(),
            "topic": SYMBOL_TOPIC,
            "letter_timeout": LETTER_TIMEOUT,
            "word_timeout": WORD_TIMEOUT,
        },
    )
    logger.info("Client connected")


@socketio.on("request_snapshot")
def handle_snapshot_request():
    emit(
        "state_snapshot",
        {
            "devices": controller.snapshot(),
            "topic": SYMBOL_TOPIC,
            "letter_timeout": LETTER_TIMEOUT,
            "word_timeout": WORD_TIMEOUT,
        },
    )


@socketio.on("clear_device")
def handle_clear_device(data):
    device_id = data.get("device_id") if isinstance(data, dict) else None
    if not device_id:
        return
    snapshot = controller.clear_device(str(device_id))
    if snapshot:
        socketio.emit(
            "device_update",
            {"event": "cleared", "device": snapshot},
            namespace="/",
        )


def _on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("Connected to MQTT broker %s:%s", MQTT_BROKER, MQTT_PORT)
        client.subscribe(SYMBOL_TOPIC)
        client.subscribe(STATUS_TOPIC)
    else:
        logger.error("MQTT connection failed with code %s", rc)


def _on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
    except json.JSONDecodeError as exc:
        logger.warning("Invalid JSON on %s: %s", msg.topic, exc)
        return

    if msg.topic == SYMBOL_TOPIC:
        controller.ingest_symbol(payload)
    elif msg.topic == STATUS_TOPIC:
        logger.debug("Status message: %s", payload)


def _start_mqtt_client() -> mqtt.Client:
    client = mqtt.Client(client_id=f"morse-server-{uuid.uuid4()}")
    if MQTT_USERNAME:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.on_connect = _on_connect
    client.on_message = _on_message
    client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
    client.loop_start()
    return client


mqtt_client = _start_mqtt_client()


if __name__ == "__main__":
    logger.info("Starting Morse grid server (topic: %s)", SYMBOL_TOPIC)
    socketio.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5000")),
        debug=True,
    )
