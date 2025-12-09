# speech_api1.py
import sys
import json
import threading
import sounddevice as sd
from websocket import WebSocketApp, ABNF
import requests
import time

# --- CONFIG (API_KEY is now passed in) ---
AUDIO_SAMPLE_RATE = 16000
AUDIO_ENCODING = "pcm_s16le"
END_UTTERANCE_SILENCE_MS = 800
WS_URL_TEMPLATE = (
    "wss://streaming.assemblyai.com/v3/ws?"
    "sample_rate={sample_rate}&encoding={encoding}"
    "&end_utterance_silence_threshold={threshold}"
)
CHANNELS = 1
CHUNK_DURATION = 0.25
IGNORED_NOISE_PHRASES = {
    "hello", "thank you", "yeah", "thanks", "okay", "welcome", "you",
    "uh", "um", "oh", "hmm", "mhm", "alright", "right", "hi",
    "goodbye", "bye", "yes", "no", "done"
}

# Backend integration
BACKEND_API_BASE = "http://127.0.0.1:8000"
BACKEND_TOKEN = None

def set_backend_token(token: str):
    global BACKEND_TOKEN
    BACKEND_TOKEN = token

def get_backend_headers():
    if not BACKEND_TOKEN:
        return {}
    return {"Authorization": f"Bearer {BACKEND_TOKEN}", "Content-Type": "application/json"}

def log_transcription_to_backend(text: str):
    """Send transcription to backend /transcriptions/"""
    if not BACKEND_TOKEN:
        # skip if no backend token
        print("[TRANSCRIPT LOG SKIP] no backend token")
        return
    try:
        payload = {"transcript_text": text}
        r = requests.post(f"{BACKEND_API_BASE}/transcriptions/", json=payload, headers=get_backend_headers(), timeout=8)
        if r.status_code >= 400:
            print("[TRANSCRIPT LOG ERROR]", r.status_code, r.text)
        else:
            # optional: print or ignore
            print("[TRANSCRIPT LOGGED]", r.json())
    except Exception as e:
        print("[TRANSCRIPT LOG EXCEPTION]", e)

def get_audio_devices():
    """Returns a list of all available audio input devices."""
    devices = sd.query_devices()
    return [{'name': d['name'], 'index': i} for i, d in enumerate(devices) if d['max_input_channels'] > 0]

def start_transcription_thread(api_key, callback, stop_event, device_index):
    """Starts transcription, receiving the API key as an argument."""

    if not api_key:
        print("[ERROR] AssemblyAI API key is missing.", file=sys.stderr)
        callback("Error: AssemblyAI API key not provided.", True)
        return None

    ws_url = WS_URL_TEMPLATE.format(
        sample_rate=AUDIO_SAMPLE_RATE,
        encoding=AUDIO_ENCODING,
        threshold=END_UTTERANCE_SILENCE_MS
    )

    def transcription_loop():
        frames = int(AUDIO_SAMPLE_RATE * CHUNK_DURATION)

        def on_open(ws):
            def mic_loop():
                try:
                    with sd.RawInputStream(samplerate=AUDIO_SAMPLE_RATE, blocksize=frames, device=device_index, channels=CHANNELS, dtype="int16") as stream:
                        while not stop_event.is_set():
                            data, _ = stream.read(frames)
                            try:
                                ws.send(bytes(data), opcode=ABNF.OPCODE_BINARY)
                            except Exception:
                                break
                except Exception as e:
                    print(f"Audio stream error: {e}", file=sys.stderr)
            threading.Thread(target=mic_loop, daemon=True).start()

        def on_message(ws, message):
            # AssemblyAI realtime returns JSON with fields; adapt to actual payload shape
            try:
                msg = json.loads(message)
            except Exception:
                return
            msg_type = msg.get("type") or msg.get("message_type")
            # Extract transcript text from likely fields: 'text' or 'transcript'
            text = (msg.get("text") or msg.get("transcript") or "").strip()
            if not text:
                return
            is_final = "final" in (msg_type or "").lower()
            if is_final and (text.lower().strip(".") in IGNORED_NOISE_PHRASES or len(text.split()) < 2):
                return
            # send text up to app
            try:
                callback(text, is_final)
            except Exception as e:
                print("[CALLBACK ERROR]", e)
            # asynchronously log to backend (fire-and-forget)
            if is_final:
                try:
                    # spawn thread so we don't block WS handling
                    threading.Thread(target=log_transcription_to_backend, args=(text,), daemon=True).start()
                except Exception as e:
                    print("[LOG THREAD ERROR]", e)

        def on_error(ws, error):
            print(f"[AAI ERROR] {error}")

        def on_close(ws, code, reason):
            print(f"[AAI Closed] code={code} reason={reason}")

        headers = [f"Authorization: {api_key}"]
        ws = WebSocketApp(ws_url,
                          header=headers,
                          on_open=on_open,
                          on_message=on_message,
                          on_error=on_error,
                          on_close=on_close)
        # run forever until stop_event set or connection breaks
        while not stop_event.is_set():
            try:
                ws.run_forever(ping_interval=20, ping_timeout=10)
            except Exception as e:
                print("[WS RUN ERROR]", e)
            time.sleep(1)  # brief backoff before reconnect

    thread = threading.Thread(target=transcription_loop, daemon=True)
    thread.start()
    return thread
