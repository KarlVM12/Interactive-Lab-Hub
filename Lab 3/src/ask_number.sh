#!/usr/bin/env bash

PROMPT="Hello! Please say your zip code"
RECORD_SECS=8
WAV_IN="ask_number_answer.wav"

# Using piper to ask initial prompt (fall back with GoogleTTS)
# on my rpi5 it seemed the pathing for models and config gave me difficulty, so if testing this yourself, might have to change those here below
say() {
  local text="$*"

  if command -v piper >/dev/null 2>&1 && [ -n "${PIPER_VOICES_DIR:-}" ]; then
    model=$(ls "$PIPER_VOICES_DIR"/*.onnx | head -n1)
    conf="${model}.json"
    tmpwav=$(mktemp --suffix=.wav)
    echo "$text" | piper --model "$model" --config "$conf" --output_file "$tmpwav" >/dev/null 2>&1
    aplay -q "$tmpwav" || true
    rm -f "$tmpwav"
  elif command -v mplayer >/dev/null 2>&1; then
    local IFS=+
    mplayer -ao alsa -really-quiet -noconsolecontrols \
      "http://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&q=$text&tl=en" \
      >/dev/null 2>&1 || true
  else
    echo ">> $text"
  fi
}

# asks user for zip and then records for specific number of seconds
say "$PROMPT"
arecord -q -d "$RECORD_SECS" -f S16_LE -r 16000 -c 1 "$WAV_IN"

# use inline python from vosk to understand what user said based on recorded wav
python - <<'PYCODE'
import re, json, wave
from vosk import Model, KaldiRecognizer

wf = wave.open("ask_number_answer.wav", "rb")
model = Model(lang="en-us")
rec = KaldiRecognizer(model, wf.getframerate())
text = ""
while True:
    data = wf.readframes(4000)
    if len(data) == 0:
        break
    if rec.AcceptWaveform(data):
        text += rec.Result()
text += rec.FinalResult()
try:
    full_text = json.loads(text.strip().splitlines()[-1]).get("text","")
except:
    full_text = text

word2digit = {"zero":"0","oh":"0","on":"1","one":"1","two":"2","three":"3","four":"4","five":"5","six":"6","seven":"7","ate":"8","eight":"8","nine":"9"}
digits = []
for token in re.findall(r"[A-Za-z0-9]+", full_text.lower()):
    if token.isdigit():
        digits.append(token)
    elif token in word2digit:
        digits.append(word2digit[token])
digits_only = "".join(digits)

print(f"Raw: {full_text}")
print(f"Digits: {digits_only}")

with open("ask_number_answer_raw.txt","w") as f: f.write(full_text+"\n")
with open("ask_number_answer_digits.txt","w") as f: f.write(digits_only+"\n")
PYCODE

# Try to make piper say the result, doesn't really work depending
DIGITS=$(cat ask_number_answer_digits.txt)
say "To confirm, I heard the following zip: $DIGITS"

