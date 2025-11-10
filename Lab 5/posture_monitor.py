#!/usr/bin/env python3
"""Posture coach powered by a Teachable Machine pose model."""
from __future__ import annotations

import argparse
import collections
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Deque, Dict, Iterable, List, Optional, Tuple

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

DEFAULT_MODEL_PATH = Path(__file__).parent / "posture_teachable_machine" / "model.tflite"
DEFAULT_LABELS_PATH = Path(__file__).parent / "posture_teachable_machine" / "labels.txt"
DEFAULT_AUDIO = Path(__file__).parent / "Peaceful_Mind.wav"
BAD_POSTURE_LABELS = {"slouching", "leaning"}
DEFAULT_TM_ID = "HLqDkYUDJ"


def _download(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url) as response, destination.open("wb") as target:
        shutil.copyfileobj(response, target)


def ensure_teachable_machine_bundle(model_id: str, bundle_dir: Path) -> Path:
    """Fetches Teachable Machine export files (including model.tflite) if missing."""
    base_url = f"https://teachablemachine.withgoogle.com/models/{model_id}/"
    downloads = {
        "metadata.json": bundle_dir / "metadata.json",
        "model.json": bundle_dir / "model.json",
        "weights.bin": bundle_dir / "weights.bin",
        "model.tflite": bundle_dir / "model.tflite",
    }

    missing_files = [name for name, path in downloads.items() if not path.exists()]
    if missing_files:
        print(f"[posture_monitor] Downloading {', '.join(missing_files)} from Teachable Machine {model_id}...")
    for remote_name, local_path in downloads.items():
        if local_path.exists():
            continue
        try:
            _download(base_url + remote_name, local_path)
        except urllib.error.URLError as exc:
            raise RuntimeError(
                f"Failed to download {remote_name} from {base_url}. Check the model ID or your internet connection."
            ) from exc

    return downloads["model.tflite"]


def _load_tflite_interpreter(model_path: Path):
    if not model_path.exists():
        raise FileNotFoundError(
            f"Missing {model_path}. Export the TensorFlow Lite version of your Teachable Machine posture model "
            "and place the .tflite file here."
        )

    try:
        from tflite_runtime.interpreter import Interpreter  # type: ignore
    except ImportError:  # pragma: no cover - fallback for dev machines
        try:
            from tensorflow.lite import Interpreter  # type: ignore
        except ImportError as exc:  # pragma: no cover
            raise ImportError(
                "Neither tflite-runtime nor tensorflow is installed. Install one of them to run the model."
            ) from exc

    return Interpreter(model_path=str(model_path))


class PostureClassifier:
    def __init__(
        self,
        model_path: Path,
        labels_path: Path,
        input_mean: float = 127.5,
        input_std: float = 127.5,
    ) -> None:
        self.labels = self._load_labels(labels_path)
        self.interpreter = _load_tflite_interpreter(model_path)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()[0]
        self.output_details = self.interpreter.get_output_details()[0]
        self.height = self.input_details["shape"][1]
        self.width = self.input_details["shape"][2]
        self.input_mean = input_mean
        self.input_std = input_std
        self.uses_float = self.input_details["dtype"].__name__ == "float32"

    @staticmethod
    def _load_labels(path: Path) -> List[str]:
        if not path.exists():
            raise FileNotFoundError(f"Missing labels file at {path}")
        labels: List[str] = []
        for raw_line in path.read_text().splitlines():
            line = raw_line.strip()
            if not line:
                continue
            if line[0].isdigit():
                parts = line.split(maxsplit=1)
                label = parts[1] if len(parts) > 1 else parts[0]
            else:
                label = line
            labels.append(label)
        if not labels:
            raise ValueError("Labels file was empty")
        return labels

    def classify(self, frame: np.ndarray) -> List[Tuple[str, float]]:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        resized = cv2.resize(rgb, (self.width, self.height))
        input_data: np.ndarray
        if self.uses_float:
            input_data = (resized.astype(np.float32) - self.input_mean) / self.input_std
        else:
            input_data = resized.astype(np.uint8)
        input_data = np.expand_dims(input_data, axis=0)
        self.interpreter.set_tensor(self.input_details["index"], input_data)
        self.interpreter.invoke()
        output = self.interpreter.get_tensor(self.output_details["index"])[0]

        if self.output_details["dtype"].__name__ == "uint8":  # quantized output
            scale, zero_point = self.output_details.get("quantization", (1.0, 0))
            output = scale * (output.astype(np.float32) - zero_point)

        output = np.array(output, dtype=np.float32)
        output -= np.max(output)
        probabilities = np.exp(output)
        probabilities_sum = probabilities.sum()
        if probabilities_sum > 0:
            probabilities /= probabilities_sum
        else:
            probabilities = np.zeros_like(probabilities)

        results = [(label.lower(), prob) for label, prob in zip(self.labels, probabilities.tolist())]
        results.sort(key=lambda item: item[1], reverse=True)
        return results


class LabelSmoother:
    def __init__(self, window: int) -> None:
        self._history: Deque[Tuple[str, float]] = collections.deque(maxlen=window)

    def add(self, label: str, confidence: float) -> None:
        self._history.append((label, confidence))

    def best(self) -> Tuple[Optional[str], float]:
        if not self._history:
            return None, 0.0
        bucket: Dict[str, List[float]] = {}
        for label, score in self._history:
            bucket.setdefault(label, []).append(score)
        best_label = max(bucket.items(), key=lambda item: (len(item[1]), sum(item[1]) / len(item[1])))[0]
        avg_conf = sum(bucket[best_label]) / len(bucket[best_label])
        return best_label, avg_conf


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
            cs_pin = digitalio.DigitalInOut(board.CE0)
            dc_pin = digitalio.DigitalInOut(board.D25)
            reset_pin = digitalio.DigitalInOut(board.D24)
            self.display = st7789.ST7789(
                spi,
                rotation=90,
                width=self.HEIGHT,
                height=self.WIDTH,
                x_offset=53,
                y_offset=40,
                cs=cs_pin,
                dc=dc_pin,
                rst=reset_pin,
                baudrate=24_000_000,
            )
        except Exception as exc:  # pragma: no cover - hardware not available during dev
            print(f"[posture_monitor] MiniTFT not available: {exc}", file=sys.stderr)
            self.display = None

        self.font_large = ImageFont.load_default()
        self.font_small = ImageFont.load_default()

    def show_status(
        self,
        label: Optional[str],
        confidence: float,
        bad_ratio: float,
        raw_predictions: Iterable[Tuple[str, float]],
    ) -> None:
        if self.display is None:
            return
        label_key = label or "unknown"
        palette = {
            "upright": ((22, 120, 49), "UPRIGHT", "Nice posture"),
            "slouching": ((180, 25, 45), "SLOUCH", "Sit taller"),
            "leaning": ((210, 130, 20), "LEAN", "Center yourself"),
            "unknown": ((40, 40, 40), "NO SIGNAL", "Check camera"),
        }
        bg_color, title, subtitle = palette.get(label_key, palette["unknown"])
        image = Image.new("RGB", (self.WIDTH, self.HEIGHT), bg_color)
        draw = ImageDraw.Draw(image)

        confidence_txt = f"{confidence*100:5.1f}%" if label else "--%"
        draw.text((10, 10), title, font=self.font_large, fill=(255, 255, 255))
        draw.text((10, 30), subtitle, font=self.font_small, fill=(255, 255, 255))
        draw.text((10, 60), confidence_txt, font=self.font_large, fill=(255, 255, 255))

        bar_x0, bar_y0 = 10, 95
        bar_x1, bar_y1 = self.WIDTH - 10, 115
        draw.rectangle([bar_x0, bar_y0, bar_x1, bar_y1], outline=(255, 255, 255), width=2)
        progress = bar_x0 + int((bar_x1 - bar_x0) * max(0.0, min(1.0, bad_ratio)))
        draw.rectangle([bar_x0, bar_y0, progress, bar_y1], fill=(255, 255, 255))

        baseline_y = 125
        for idx, (name, score) in enumerate(raw_predictions):
            text = f"{name[:8]} {score*100:4.1f}%"
            draw.text((10 + idx * 75, baseline_y), text, font=self.font_small, fill=(0, 0, 0))

        self.display.image(image)

    def close(self) -> None:
        pass


class AudioNotifier:
    def __init__(self, audio_path: Path, cooldown: float) -> None:
        self.audio_path = audio_path
        self.cooldown = cooldown
        self._process: Optional[subprocess.Popen] = None
        self._last_started = 0.0

    def maybe_play(self) -> None:
        now = time.monotonic()
        if not self.audio_path.exists():
            return
        if now - self._last_started < self.cooldown:
            return
        if self._process and self._process.poll() is None:
            return
        try:
            self._process = subprocess.Popen(["aplay", "-q", str(self.audio_path)])
            self._last_started = now
        except FileNotFoundError:
            print("aplay command not found; skipping audio alert", file=sys.stderr)

    def stop(self) -> None:
        if self._process and self._process.poll() is None:
            self._process.terminate()


def resolve_model_path(args: argparse.Namespace) -> Path:
    model_path = args.model
    if model_path.exists():
        return model_path

    tm_id = args.tm_id.strip() if isinstance(args.tm_id, str) else None
    if tm_id:
        bundle_dir = model_path.parent
        downloaded = ensure_teachable_machine_bundle(tm_id, bundle_dir)
        if model_path != downloaded:
            try:
                shutil.copy(downloaded, model_path)
            except Exception:
                model_path = downloaded
        return downloaded

    raise FileNotFoundError(
        f"Model file {model_path} is missing. Either supply --tm-id to download it or point --model to an existing .tflite file."
    )


def run_monitor(args: argparse.Namespace) -> None:
    model_path = resolve_model_path(args)
    classifier = PostureClassifier(model_path, args.labels)
    smoother = LabelSmoother(args.smoothing)
    display = DisplayController()
    audio = AudioNotifier(args.audio, args.alert_cooldown)

    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        raise RuntimeError(f"Unable to access camera index {args.camera}")

    timer_start: Optional[float] = None
    last_console = 0.0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Camera frame grab failed", file=sys.stderr)
                break

            predictions = classifier.classify(frame)
            top_label, top_score = predictions[0]
            smoother.add(top_label, top_score)
            label, confidence = smoother.best()

            now = time.monotonic()
            bad_ratio = 0.0
            if label in BAD_POSTURE_LABELS:
                timer_start = timer_start or now
                bad_ratio = min(1.0, (now - timer_start) / args.alert_after)
                if (now - timer_start) >= args.alert_after:
                    audio.maybe_play()
                    timer_start = now  # restart timer for next reminder
            else:
                timer_start = None

            display.show_status(label, confidence, bad_ratio, predictions)

            if args.preview:
                status = label or "unknown"
                cv2.putText(
                    frame,
                    f"{status}: {confidence*100:4.1f}%",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0) if status == "upright" else (0, 0, 255),
                    2,
                )
                cv2.imshow("Posture Monitor", frame)
                if cv2.waitKey(1) & 0xFF == 27:
                    break

            if now - last_console > 1.0:
                print(f"label={label} conf={confidence:.2f} ratio={bad_ratio:.2f}")
                last_console = now

    except KeyboardInterrupt:
        print("Stopping posture monitor...")
    finally:
        cap.release()
        if args.preview:
            cv2.destroyAllWindows()
        display.close()
        audio.stop()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL_PATH, help="Path to Teachable Machine .tflite file")
    parser.add_argument("--labels", type=Path, default=DEFAULT_LABELS_PATH, help="Label file (one label per line)")
    parser.add_argument("--audio", type=Path, default=DEFAULT_AUDIO, help="Audio prompt to play when posture is poor")
    parser.add_argument("--camera", type=int, default=0, help="Camera index for OpenCV VideoCapture")
    parser.add_argument("--smoothing", type=int, default=5, help="Number of frames used for majority smoothing")
    parser.add_argument("--alert-after", type=float, default=10.0, help="Seconds of sustained poor posture before alert")
    parser.add_argument("--alert-cooldown", type=float, default=20.0, help="Minimum seconds between audio prompts")
    parser.add_argument("--preview", action="store_true", help="Show an OpenCV preview window (HDMI only)")
    parser.add_argument(
        "--tm-id",
        default=DEFAULT_TM_ID,
        help=(
            "Teachable Machine model ID (from shareable link) to auto-download model files when the .tflite is missing."
            " Pass an empty string to disable auto-download."
        ),
    )
    return parser.parse_args()


if __name__ == "__main__":
    run_monitor(parse_args())
