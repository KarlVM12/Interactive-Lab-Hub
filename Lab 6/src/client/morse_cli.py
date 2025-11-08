#!/usr/bin/env python3
"""Interactive MQTT publisher for typing Morse code from a laptop."""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
import uuid
from dataclasses import dataclass
from typing import Iterable, Optional

import paho.mqtt.client as mqtt

MQTT_BROKER = os.getenv("IDD_MQTT_BROKER", "farlab.infosci.cornell.edu")
MQTT_PORT = int(os.getenv("IDD_MQTT_PORT", "1883"))
MQTT_USERNAME = os.getenv("IDD_MQTT_USER", "idd")
MQTT_PASSWORD = os.getenv("IDD_MQTT_PASS", "device@theFarm")
TEAM_TOPIC = os.getenv("IDD_MORSE_TOPIC", "IDD/lab6/morse/coolguys")

SYMBOL_TOPIC = f"{TEAM_TOPIC}/symbol"
STATUS_TOPIC = f"{TEAM_TOPIC}/status"

DOT_DURATION = float(os.getenv("MORSE_CLI_DOT_DURATION", "0.25"))
DASH_DURATION = float(os.getenv("MORSE_CLI_DASH_DURATION", "0.75"))
LETTER_PAUSE = float(os.getenv("MORSE_CLI_LETTER_PAUSE", "3.6"))
WORD_PAUSE = float(os.getenv("MORSE_CLI_WORD_PAUSE", "6.2"))

LOGGER_LEVEL = os.getenv("MORSE_CLI_LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=LOGGER_LEVEL,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
LOGGER = logging.getLogger("morse.cli")


@dataclass(frozen=True)
class MorseSymbol:
    symbol: str
    duration: float

    @property
    def payload(self) -> dict:
        return {
            "symbol": self.symbol,
            "duration": round(self.duration, 3),
        }


def default_device_id() -> str:
    base = os.getenv("MORSE_DEVICE_ID")
    if base:
        return base
    hostname = os.uname().nodename if hasattr(os, "uname") else "laptop"
    return f"laptop-{hostname}-{uuid.uuid4().hex[:6]}"


class MorsePublisher:
    """Shared MQTT publisher for laptop CLI."""

    def __init__(self, device_id: Optional[str] = None, label: Optional[str] = None) -> None:
        self.device_id = device_id or default_device_id()
        self.label = label or os.getenv("MORSE_DEVICE_LABEL", "PI 1")
        self.client = mqtt.Client(client_id=f"morse-cli-{uuid.uuid4().hex}")
        if MQTT_USERNAME:
            self.client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        self.client.will_set(
            STATUS_TOPIC,
            json.dumps(
                {
                    "device_id": self.device_id,
                    "label": self.label,
                    "status": "offline",
                    "timestamp": time.time(),
                }
            ),
            qos=0,
            retain=False,
        )
        self.client.on_connect = self._on_connect
        self.client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
        self.client.loop_start()
        self._publish_status("online")

    def _on_connect(self, client, userdata, flags, rc) -> None:  # type: ignore[override]
        if rc == 0:
            LOGGER.info("Connected to MQTT broker %s:%s", MQTT_BROKER, MQTT_PORT)
        else:
            LOGGER.error("MQTT connection failed with code %s", rc)

    def _publish_status(self, status: str, **extra: object) -> None:
        payload = {
            "device_id": self.device_id,
            "label": self.label,
            "status": status,
            "timestamp": time.time(),
        }
        payload.update(extra)
        self.client.publish(STATUS_TOPIC, json.dumps(payload), qos=0, retain=False)

    def publish_symbol(self, morse: MorseSymbol) -> None:
        payload = {
            "device_id": self.device_id,
            "label": self.label,
            "timestamp": time.time(),
            **morse.payload,
        }
        result = self.client.publish(SYMBOL_TOPIC, json.dumps(payload), qos=0, retain=False)
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            LOGGER.info("Sent %s (%.2fs)", morse.symbol, morse.duration)
        else:
            LOGGER.error("Failed to send symbol (rc=%s)", result.rc)

    def close(self) -> None:
        try:
            self._publish_status("offline")
        finally:
            self.client.loop_stop()
            self.client.disconnect()


COMMAND_HELP = """Commands:
  dot / .          send dot (duration {dot}s)
  dash / -         send dash (duration {dash}s)
  pause            wait letter gap (~{letter}s)
  space            wait word gap (~{word}s)
  send <pattern>   publish pattern like .-.. (letter gap between chars)
  text <word>      publish letters using Morse translation
  clear            print instructions
  quit / exit      leave the program
"""

MORSE_LOOKUP = {
    "a": ".-",
    "b": "-...",
    "c": "-.-.",
    "d": "-..",
    "e": ".",
    "f": "..-.",
    "g": "--.",
    "h": "....",
    "i": "..",
    "j": ".---",
    "k": "-.-",
    "l": ".-..",
    "m": "--",
    "n": "-.",
    "o": "---",
    "p": ".--.",
    "q": "--.-",
    "r": ".-.",
    "s": "...",
    "t": "-",
    "u": "..-",
    "v": "...-",
    "w": ".--",
    "x": "-..-",
    "y": "-.--",
    "z": "--..",
    "0": "-----",
    "1": ".----",
    "2": "..---",
    "3": "...--",
    "4": "....-",
    "5": ".....",
    "6": "-....",
    "7": "--...",
    "8": "---..",
    "9": "----.",
}


def pattern_to_symbols(pattern: str) -> Iterable[MorseSymbol]:
    for char in pattern:
        if char == ".":
            yield MorseSymbol(".", DOT_DURATION)
        elif char == "-":
            yield MorseSymbol("-", DASH_DURATION)
        else:
            continue


def send_pattern(publisher: MorsePublisher, pattern: str, letter_pause: float = LETTER_PAUSE) -> None:
    for symbol in pattern_to_symbols(pattern):
        publisher.publish_symbol(symbol)
        time.sleep(0.05)
    time.sleep(letter_pause)


def send_text(publisher: MorsePublisher, text: str) -> None:
    words = text.strip().split()
    for word_index, word in enumerate(words):
        for letter in word:
            pattern = MORSE_LOOKUP.get(letter.lower())
            if not pattern:
                LOGGER.warning("Skipping unsupported character '%s'", letter)
                continue
            send_pattern(publisher, pattern)
        if word_index < len(words) - 1:
            time.sleep(WORD_PAUSE)


def interactive_mode(publisher: MorsePublisher) -> None:
    print(COMMAND_HELP.format(dot=DOT_DURATION, dash=DASH_DURATION, letter=LETTER_PAUSE, word=WORD_PAUSE))
    while True:
        try:
            line = input("morse> ").strip()
        except EOFError:
            print()
            break
        if not line:
            continue
        normalized = line.lower()
        if normalized in {"quit", "exit", "q"}:
            break
        if normalized in {"dot", ".", "d"}:
            publisher.publish_symbol(MorseSymbol(".", DOT_DURATION))
            continue
        if normalized in {"dash", "-", "da"}:
            publisher.publish_symbol(MorseSymbol("-", DASH_DURATION))
            continue
        if normalized == "pause":
            print(f" pausing {LETTER_PAUSE:.2f}s for letter gap")
            time.sleep(LETTER_PAUSE)
            continue
        if normalized == "space":
            print(f" pausing {WORD_PAUSE:.2f}s for word gap")
            time.sleep(WORD_PAUSE)
            continue
        if normalized.startswith("send "):
            pattern = normalized[5:].replace(" ", "")
            if not pattern:
                print(" supply a pattern, e.g. send .-..")
                continue
            send_pattern(publisher, pattern)
            continue
        if normalized.startswith("text "):
            text = line[5:]
            send_text(publisher, text)
            continue
        if normalized == "clear":
            print(COMMAND_HELP.format(dot=DOT_DURATION, dash=DASH_DURATION, letter=LETTER_PAUSE, word=WORD_PAUSE))
            continue
        print("Unknown command. Type 'clear' for help.")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Publish Morse symbols over MQTT from the keyboard")
    parser.add_argument("--sequence", help="Send a dot/dash sequence then exit (e.g. .-..)")
    parser.add_argument("--text", help="Send plain-text phrase using Morse lookup")
    parser.add_argument("--label", help="Override device label shown on the grid")
    parser.add_argument("--device-id", help="Override device id announced to the server")
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    publisher = MorsePublisher(device_id=args.device_id, label=args.label)
    try:
        if args.sequence:
            send_pattern(publisher, args.sequence)
            return 0
        if args.text:
            send_text(publisher, args.text)
            return 0
        interactive_mode(publisher)
        return 0
    finally:
        publisher.close()


if __name__ == "__main__":
    raise SystemExit(main())
