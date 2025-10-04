#!/usr/bin/env python3
"""Plant Pal voice pipeline with display and button integration.

This script runs on a Raspberry Pi with the Adafruit mini PiTFT display.
It combines the speech pipeline from Lab 3 with the tactile/visual cues
from Lab 2:

- Button A wakes Plant Pal and starts a single speech interaction.
- The screen turns BLUE while Plant Pal is listening.
- During LLM thinking the screen pulses between BLUE and WHITE.
- After answering, the screen returns to a soft YELLOW idle state.
- Button B exits the program at any time while idle.

Environment variables (optional):
    OLLAMA_URL, OLLAMA_MODEL, SYSTEM_PROMPT
    TTS_BACKEND, ESPEAK_VOICE, PIPER_VOICE, PIPER_MODEL, PIPER_CONFIG

Hardware wiring matches the Lab 2 samples (GPIO5 CS, GPIO25 DC, GPIO22 backlight,
GPIO23 button A, GPIO24 button B).
"""

from __future__ import annotations

import io
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
import wave
from typing import List, Sequence, Tuple

import requests
import speech_recognition as sr

import board
import digitalio
from adafruit_rgb_display.rgb import color565
import adafruit_rgb_display.st7789 as st7789

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://192.168.1.6:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2:3b")
SYSTEM_PROMPT = os.environ.get(
    "SYSTEM_PROMPT",
    (
        "You are Plant Pal, a cheerful houseplant who loves sharing quick,"
        " kind replies. Stay under ~30 words unless asked otherwise. Sprinkle"
        " in gentle plant-care knowledge when it fits."
    ),
)

ESPEAK_VOICE = os.environ.get("ESPEAK_VOICE", "en-us")
TTS_BACKEND = os.environ.get("TTS_BACKEND", "piper")

PIPER_VOICE = os.environ.get("PIPER_VOICE", "en_US-lessac-medium")
DEFAULT_VOICE_DIR = os.path.join(os.path.expanduser("~"), ".local", "share", "piper", "voices")
PIPER_MODEL = os.environ.get("PIPER_MODEL", os.path.join(DEFAULT_VOICE_DIR, f"{PIPER_VOICE}.onnx"))
PIPER_CONFIG = os.environ.get("PIPER_CONFIG", os.path.join(DEFAULT_VOICE_DIR, f"{PIPER_VOICE}.onnx.json"))

LISTENING_COLOR = color565(60, 120, 255)      # calm blue
RESPONDING_COLOR = color565(170, 240, 180)    # soft green while speaking
IDLE_COLOR = color565(255, 230, 140)          # warm soft yellow
THINKING_COLORS = (
    color565(80, 150, 255),
    color565(110, 185, 255),
    color565(140, 210, 255),
)
ERROR_COLOR = color565(255, 80, 80)

BUTTON_DEBOUNCE = 0.02
MAX_EMPTY_TURNS = 2

# ---------------------------------------------------------------------------
# Display and button setup
# ---------------------------------------------------------------------------
display = None
backlight = None
button_a = None
button_b = None


def init_display() -> None:
    global display, backlight, button_a, button_b

    cs_pin = digitalio.DigitalInOut(board.D5)
    dc_pin = digitalio.DigitalInOut(board.D25)
    reset_pin = None
    spi = board.SPI()

    display = st7789.ST7789(
        spi,
        cs=cs_pin,
        dc=dc_pin,
        rst=reset_pin,
        baudrate=64_000_000,
        width=135,
        height=240,
        x_offset=53,
        y_offset=40,
    )

    backlight_pin = digitalio.DigitalInOut(board.D22)
    backlight_pin.switch_to_output(value=True)
    backlight = backlight_pin

    button_a_pin = digitalio.DigitalInOut(board.D23)
    button_a_pin.switch_to_input(pull=digitalio.Pull.UP)
    button_a = button_a_pin

    button_b_pin = digitalio.DigitalInOut(board.D24)
    button_b_pin.switch_to_input(pull=digitalio.Pull.UP)
    button_b = button_b_pin

    display.fill(IDLE_COLOR)


init_display()

# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------
_animation_stop: threading.Event | None = None
_animation_thread: threading.Thread | None = None


def set_display_color(color: int) -> None:
    if display is not None:
        display.fill(color)


def show_idle() -> None:
    set_display_color(IDLE_COLOR)


def show_listening() -> None:
    set_display_color(LISTENING_COLOR)


def show_responding() -> None:
    set_display_color(RESPONDING_COLOR)


def show_error() -> None:
    set_display_color(ERROR_COLOR)


def start_thinking_animation() -> None:
    global _animation_stop, _animation_thread

    stop_event = threading.Event()
    _animation_stop = stop_event

    def _pulse() -> None:
        idx = 0
        while not stop_event.is_set():
            set_display_color(THINKING_COLORS[idx % len(THINKING_COLORS)])
            idx += 1
            time.sleep(0.55)

    thread = threading.Thread(target=_pulse, daemon=True)
    _animation_thread = thread
    thread.start()


def stop_thinking_animation() -> None:
    global _animation_stop, _animation_thread
    if _animation_stop is not None:
        _animation_stop.set()
        _animation_stop = None
    if _animation_thread is not None:
        _animation_thread.join(timeout=0.6)
        _animation_thread = None


# ---------------------------------------------------------------------------
# Button helpers
# ---------------------------------------------------------------------------
def button_pressed(btn: digitalio.DigitalInOut) -> bool:
    return btn.value is False


def wait_for_button() -> str:
    while True:
        if button_a and button_pressed(button_a):
            # simple debounce: wait for release
            time.sleep(BUTTON_DEBOUNCE)
            while button_pressed(button_a):
                time.sleep(BUTTON_DEBOUNCE)
            return "A"
        if button_b and button_pressed(button_b):
            time.sleep(BUTTON_DEBOUNCE)
            while button_pressed(button_b):
                time.sleep(BUTTON_DEBOUNCE)
            return "B"
        time.sleep(0.05)


# ---------------------------------------------------------------------------
# TTS helpers
# ---------------------------------------------------------------------------
def say(text: str) -> None:
    if not text:
        return
    cleaned = text.encode("ascii", "ignore").decode("ascii")
    print(f"\nPlant Pal: {cleaned}\n")
    try:
        if TTS_BACKEND.lower() == "piper":
            tts_piper("... " + cleaned)
        else:
            subprocess.run(["espeak", "-v", ESPEAK_VOICE, cleaned], check=False)
    except FileNotFoundError:
        print("[WARN] Missing TTS backend binary.")


def tts_piper(text: str) -> None:
    if not os.path.exists(PIPER_MODEL):
        raise FileNotFoundError(f"piper model not found at {PIPER_MODEL}")
    if not os.path.exists(PIPER_CONFIG):
        raise FileNotFoundError(f"piper config not found at {PIPER_CONFIG}")

    tmpwav = tempfile.mktemp(suffix=".wav")
    try:
        subprocess.run(
            ["piper", "-m", PIPER_MODEL, "-c", PIPER_CONFIG, "--output_file", tmpwav],
            input=(text + "\n").encode("utf-8"),
            check=False,
        )
        subprocess.run(["aplay", "-q", tmpwav], check=False)
    finally:
        try:
            os.remove(tmpwav)
        except OSError:
            pass


# ---------------------------------------------------------------------------
# Ollama helpers
# ---------------------------------------------------------------------------
SESSION = requests.Session()
SESSION.headers.update({"Content-Type": "application/json"})


def check_ollama() -> bool:
    try:
        resp = SESSION.get(f"{OLLAMA_URL}/api/tags", timeout=(5, 15))
        resp.raise_for_status()
        models = [m.get("name", "") for m in resp.json().get("models", [])]
        print(f"[OK] Ollama reachable at {OLLAMA_URL}. Available models: {models}")
        if OLLAMA_MODEL not in models:
            print(f"[INFO] {OLLAMA_MODEL} not listed; ensure it's pulled on the host.")
        return True
    except Exception as exc:  # pylint: disable=broad-except
        print(f"[ERROR] Unable to reach Ollama at {OLLAMA_URL}: {exc}")
        print("    Start on host with: OLLAMA_HOST=0.0.0.0 ollama serve")
        return False


def build_prompt(history: Sequence[Tuple[str, str]], user_text: str) -> str:
    parts: List[str] = []
    for role, content in history:
        label = "User" if role == "user" else "Plant Pal"
        parts.append(f"{label}: {content}")
    parts.append(f"User: {user_text}")
    parts.append("Plant Pal:")
    return "\n".join(parts)


def ollama_stream(prompt: str) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": True,
        "system": SYSTEM_PROMPT,
    }
    full: List[str] = []
    with SESSION.post(
        f"{OLLAMA_URL}/api/generate",
        json=payload,
        stream=True,
        timeout=(5, 300),
    ) as response:
        response.raise_for_status()
        print("Ollama: ", end="", flush=True)
        for line in response.iter_lines(decode_unicode=True):
            if not line:
                continue
            try:
                chunk = json.loads(line)
            except json.JSONDecodeError:
                continue
            text = chunk.get("response")
            if text:
                full.append(text)
                print(text, end="", flush=True)
            if chunk.get("done"):
                print()
                break
    return "".join(full)


# ---------------------------------------------------------------------------
# Speech recognition
# ---------------------------------------------------------------------------
def stt_vosk(recognizer: sr.Recognizer, mic: sr.Microphone) -> str | None:
    try:
        import vosk
    except ImportError:
        print("[ERROR] Vosk not installed. pip install vosk")
        return None

    try:
        with mic as source:
            print("Listening…")
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=None)
    except sr.WaitTimeoutError:
        print("…no speech detected (timeout).")
        return None

    wav_data = audio.get_wav_data(convert_rate=16000, convert_width=2)
    wf = wave.open(io.BytesIO(wav_data), "rb")
    model = vosk.Model(lang="en-us")
    recog = vosk.KaldiRecognizer(model, wf.getframerate())

    result_text = ""
    while True:
        data = wf.readframes(4000)
        if not data:
            break
        if recog.AcceptWaveform(data):
            result_text = json.loads(recog.Result()).get("text", "")
    result_text = json.loads(recog.FinalResult()).get("text", result_text)
    text = (result_text or "").strip()

    if text:
        print(f"You: {text}")
        return text
    print("…no speech recognized.")
    return None


# ---------------------------------------------------------------------------
# Main flow
# ---------------------------------------------------------------------------
EXIT_WORDS = {"exit", "quit", "goodbye", "bye", "sleep"}


def run_session(recognizer: sr.Recognizer, mic: sr.Microphone) -> None:
    history: List[Tuple[str, str]] = []
    empty_turns = 0

    show_responding()
    say("Hello! What would you like to know?")
    show_listening()

    while True:
        if button_b and button_pressed(button_b):
            show_responding()
            say("Alright, heading back to my planter.")
            show_idle()
            return

        user_text = stt_vosk(recognizer, mic)
        if not user_text:
            empty_turns += 1
            if empty_turns >= MAX_EMPTY_TURNS:
                show_responding()
                say("I'll be here soaking up sun. Tap me when you need me again.")
                show_idle()
                return
            show_listening()
            continue

        empty_turns = 0
        lowered = user_text.lower()
        if any(word in lowered for word in EXIT_WORDS):
            show_responding()
            say("Okay, I'll soak up the sun quietly.")
            show_idle()
            return

        prompt = build_prompt(history, user_text)

        try:
            start_thinking_animation()
            reply = ollama_stream(prompt)
        except Exception as exc:  # pylint: disable=broad-except
            stop_thinking_animation()
            print(f"[ERROR] Ollama request failed: {exc}")
            show_error()
            say("Something went wrong reaching my roots. Can you try again later?")
            time.sleep(1.5)
            show_idle()
            return
        finally:
            stop_thinking_animation()

        if not reply:
            show_error()
            say("I do not have an answer right now. Maybe check back soon.")
            time.sleep(1.0)
            show_idle()
            return

        history.extend([("user", user_text), ("assistant", reply)])

        show_responding()
        say(reply)
        show_listening()


def main() -> None:
    print(
        f"Starting Plant Pal pipeline (ollama={OLLAMA_MODEL}, url={OLLAMA_URL}, tts={TTS_BACKEND})"
    )
    if not check_ollama():
        sys.exit(1)

    recognizer = sr.Recognizer()
    recognizer.pause_threshold = 1.5
    recognizer.non_speaking_duration = 0.5
    recognizer.dynamic_energy_threshold = True

    mic = sr.Microphone(device_index=0)

    print("Calibrating microphone…")
    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=1.0)
    print("Ready. Press button A to wake Plant Pal, button B to exit.")

    show_idle()

    try:
        while True:
            pressed = wait_for_button()
            if pressed == "B":
                print("Button B pressed — shutting down.")
                say("Going back to photosynthesis mode. See you later!")
                break
            print("Button A pressed — starting interaction.")
            run_session(recognizer, mic)
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt — exiting.")
    finally:
        show_idle()
        backlight.value = True
        print("Plant Pal stopped.")


if __name__ == "__main__":
    main()
