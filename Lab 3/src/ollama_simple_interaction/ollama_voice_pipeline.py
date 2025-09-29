#!/usr/bin/env python3
"""
Ollama Voice Pipeline (single file)
- Mic -> STT Vosk -> Ollama (streaming) -> TTS espeak
- Starts with an Ollama greeting, then takes turns:

Envs:
  OLLAMA_URL=http://192.168.1.10:11434
  OLLAMA_MODEL=phi3:mini
  ESPEAK_VOICE=en-us         # e.g. en, en-us, en+f3
  STT_BACKEND=vosk           
"""

import os, sys, json, time, subprocess, requests, io, wave, tempfile
import speech_recognition as sr

OLLAMA_URL = "http://192.168.1.10:11434"
OLLAMA_MODEL = "phi3:mini"
ESPEAK_VOICE = "en-us"
STT_BACKEND = "vosk"
TTS_BACKEND = "piper"
SYSTEM_PROMPT = "You are a concise, friendly voice assistant running on a Raspberry Pi."

# had problems with dynamic pathing for piper so had to hard code my user into the path
PIPER_VOICES_DIR = "/home/karl/.local/share/piper/voices"
TTS_PIPER_VOICE = "en_US-lessac-medium"
TTS_PIPER_MODEL = "/home/karl/.local/share/piper/voices/en_US-lessac-medium.onnx"
TTS_PIPER_CONFIG = "/home/karl/.local/share/piper/voices/en_US-lessac-medium.onnx.json"

# piper tts, with espaek fall back
def say(text: str):
    if not text:
        return
    clean = text.encode("ascii", "ignore").decode("ascii")
    print(f"\nAssistant: {clean}\n")
    try:        
        if TTS_BACKEND == "piper":
            tts_piper(clean)
        else:
            subprocess.run(["espeak", "-v", ESPEAK_VOICE, clean], check=False)
    except FileNotFoundError:
        print("[WARN] espeak not found (sudo apt-get install espeak).")

def tts_piper(text: str):
    model = TTS_PIPER_MODEL
    conf = TTS_PIPER_CONFIG

    # Synthesize to temp wav and play
    tmpwav = tempfile.mktemp(suffix=".wav")
    proc = subprocess.run(
        ["piper", "-m", model, "-c", conf, "--output_file", tmpwav],
        input=(text + "\n").encode("utf-8"),
        check=False
    )

    subprocess.run(["aplay", "-q", tmpwav], check=False)
    try:
        os.remove(tmpwav)
    except OSError:
        pass        

# using ollama (hosting it on my local laptop so that i get much faster responses)
# ensuring you are connected and model it pulled
SESSION = requests.Session()
SESSION.headers.update({"Content-Type": "application/json"})
def check_ollama():
    try:
        r = SESSION.get(f"{OLLAMA_URL}/api/tags", timeout=(5, 15))
        r.raise_for_status()
        models = [m.get("name", "") for m in r.json().get("models", [])]
        print(f"[OK] Connected to Ollama at {OLLAMA_URL}. Models: {models}")
        if OLLAMA_MODEL not in models:
            print(f"[INFO] '{OLLAMA_MODEL}' not listed. Ensure it's pulled on the host (ollama pull {OLLAMA_MODEL}).")
        return True
    except Exception as e:
        print(f"[ERROR] Cannot reach Ollama at {OLLAMA_URL}: {e}")
        print(" - Start on host: OLLAMA_HOST=0.0.0.0:11434 ollama serve")
        print(" - Or tunnel: ssh -N -L 11434:localhost:11434 <user>@<host>")
        return False

# streaming ollama vs one chunk, its just faster and more manageable and more useful for debugging
def ollama_stream(prompt: str) -> str:
    """Stream tokens so you see output as it arrives; returns full text at the end."""
    payload = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": True, "system": SYSTEM_PROMPT}
    full = []
    with SESSION.post(f"{OLLAMA_URL}/api/generate", json=payload, stream=True, timeout=(5, 300)) as r:
        r.raise_for_status()
        print("Ollama (stream): ", end="", flush=True)
        for line in r.iter_lines(decode_unicode=True):
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if "response" in obj:
                chunk = obj["response"]
                full.append(chunk)
                print(chunk, end="", flush=True)
            if obj.get("done"):
                print()
                break
    return "".join(full)

# if we want also has the option to get the whole response at once, but its slower
def ollama_once(prompt: str) -> str:
    """Non-streaming (waits for full response)."""
    payload = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False, "system": SYSTEM_PROMPT}
    r = SESSION.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=(5, 300))
    r.raise_for_status()
    return r.json().get("response", "")

# vosk STT listening set up and functionality
def stt_vosk(rec: sr.Recognizer, mic: sr.Microphone) -> str | None:
    try:
        import vosk 
    except ImportError:
        print("[ERROR] STT_BACKEND=vosk but 'vosk' is not installed (pip install vosk).")
        return None
    try:
        with mic as source:
            print("Listening…")
            audio = rec.listen(source, timeout=10, phrase_time_limit=None)

        wav_bytes = audio.get_wav_data(convert_rate=16000, convert_width=2)
        wf = wave.open(io.BytesIO(wav_bytes), "rb")
        model = vosk.Model(lang="en-us")
        recog = vosk.KaldiRecognizer(model, wf.getframerate())
        text = ""
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if recog.AcceptWaveform(data):
                text = json.loads(recog.Result()).get("text", "")
        text = json.loads(recog.FinalResult()).get("text", text)
        text = (text or "").strip()
        if text:
            print(f"You: {text}")
            return text
        print("…no speech recognized.")
        return None
    except sr.WaitTimeoutError:
        print("…timeout, no speech.")
    except Exception as e:
        print(f"[VOSK ERROR] {e}")
        return None

# convo loop pipeline
def main():
    print(f"Starting Voice Pipeline  (host={OLLAMA_URL}, model={OLLAMA_MODEL}, stt={STT_BACKEND})")
    if not check_ollama():
        sys.exit(1)
    
    # was having problems with cutting off the user responses, so made it more dynamic
    rec = sr.Recognizer()
    rec.pause_threshold = 1.5
    rec.non_speaking_duration = 0.5
    rec.dynamic_energy_threshold = True

    mic = sr.Microphone(device_index=0) #default mic, should be the c270

    print("Calibrating mic (1s for ambient noise)…")
    with mic as source:
        rec.adjust_for_ambient_noise(source, duration=1.0)
    print("Ready. Say 'exit' to quit.")

    # start with ollama custom greeting, manual speech fall back as well
    try:
        greeting = ollama_stream("Give a simple one line greeting to the user. Don't say anything else")
        say(greeting)
    except Exception as e:
        print(f"[WARN] opening greeting failed: {e}")
        say("Hello! You can start speaking whenever you're ready.")

    stt_fn = stt_vosk

    # turn based voice loop between phi3 ollama and user
    while True:
        try:
            user_text = stt_fn(rec, mic)
            if not user_text:
                continue
            if any(w in user_text.lower() for w in ("exit", "quit", "bye", "goodbye")):
                say("Goodbye!")
                break

            print("Thinking…")
            reply = ollama_stream(user_text)
            say(reply)

        except KeyboardInterrupt:
            say("Stopping now. Goodbye!")
            break
        except Exception as e:
            print(f"[ERROR] {e}")
            say("I ran into a problem. Let's try again.")

if __name__ == "__main__":
    main()

