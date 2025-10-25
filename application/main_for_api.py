# main_for_api.py
import sys, threading, os, requests, json
from PyQt5.QtWidgets import QApplication
from dotenv import load_dotenv

# Import the enhanced UI components
from launcher_ui import LauncherWindow
from overlay_ui2 import FloatingOverlay, show_overlay  # keep as-is; file must exist
from ai_engine import get_response_from_chat_stream, estimate_tokens
from speech_api1 import start_transcription_thread, set_backend_token

# =========================
# Load ENV
# =========================
load_dotenv()
GEMINI_KEY = os.getenv("gemini_llm5")

ASSEMBLY_KEY = os.getenv("assembly_api_key")
OCR_API_KEY = os.getenv("ocr")

# =========================
# Backend config
# =========================
API_BASE = "https://se-project-backend-ddr9.onrender.com"
TOKEN_FILE = "token.json"

stop_event = threading.Event()
chat = None
transcription_thread = None
overlay_window = None
latest_transcript = ""
END_UTTERANCE_TIMEOUT = 2.0

# =========================
# Backend helpers
# =========================
def save_token(token):
    with open(TOKEN_FILE, "w") as f: json.dump({"access_token": token}, f)

def load_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            return json.load(f).get("access_token")
    return None

def backend_get_credits(token):
    try:
        r = requests.get(f"{API_BASE}/credits/balance", headers={"Authorization": f"Bearer {token}"}, timeout=6)
        if r.status_code == 200:
            return r.json().get("credits", 0)
    except Exception as e:
        print("[CREDITS ERROR]", e)
    return 0

def backend_deduct_and_log(token, question, answer, tokens_used=None):
    if tokens_used is None:
        tokens_used = estimate_tokens(answer)
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    try:
        requests.post(f"{API_BASE}/credits/deduct", headers=headers, json={"amount": tokens_used}, timeout=8)
        payload = {"query": question, "ai_response": answer, "tokens_used": tokens_used}
        requests.post(f"{API_BASE}/responses/", headers=headers, json=payload, timeout=8)
    except Exception as e:
        print("[CREDIT/LOG ERROR]", e)

# =========================
# OCR / AI pipeline
# =========================
def get_answer_from_screen():
    global overlay_window
    def do_capture():
        screenshot_path = "screenshot.png"
        try:
            # Capture the screen using PyQt5
            from PyQt5.QtWidgets import QApplication
            from PyQt5.QtGui import QPixmap
            
            app = QApplication.instance()
            screen = app.primaryScreen()
            if screen:
                # Capture the entire screen
                screenshot = screen.grabWindow(0)
                # Save the screenshot
                screenshot.save(screenshot_path, 'PNG')
                print(f"Screenshot captured and saved to {screenshot_path}")
            else:
                raise Exception("Could not access screen for capture")
        except Exception as e:
            print(f"Error capturing screenshot: {e}")
            if overlay_window:
                overlay_window.show()
            show_overlay('answer', f"Screenshot error: {e}")
            return
        finally:
            if overlay_window:
                overlay_window.show()
        threading.Thread(target=process_captured_image, args=(screenshot_path,), daemon=True).start()
    if overlay_window:
        overlay_window.hide()
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(250, do_capture)

def process_captured_image(image_path):
    global chat
    if not image_path or not os.path.exists(image_path):
        show_overlay('answer', "OCR error: screenshot not found")
        return
    try:
        show_overlay('question', "OCR processing...")
        payload = {'isOverlayRequired': False, 'apikey': OCR_API_KEY, 'language': 'eng'}
        with open(image_path, 'rb') as f:
            r = requests.post("https://api.ocr.space/parse/image", files={'filename': f}, data=payload, timeout=15)
        result = r.json()
        parsed = result.get('ParsedResults')
        if not parsed:
            raise ValueError("No OCR results")
        extracted = parsed[0].get('ParsedText', '').strip()
        question = f"Screen Question: {extracted}"
        show_overlay('question', extracted)
        full_resp = ""
        for chunk in get_response_from_chat_stream(chat, question):
            full_resp += chunk
            show_overlay('answer', f"Q: {extracted}\n\nA: {full_resp}")
        token = QApplication.instance()._backend_token
        if token:
            backend_deduct_and_log(token, question, full_resp)
    except Exception as e:
        show_overlay('answer', f"OCR error: {e}")
    finally:
        show_overlay('question', "Listening...")
        try:
            if os.path.exists(image_path):
                os.remove(image_path)
        except Exception:
            pass

def get_ai_answer():
    global latest_transcript, chat
    if not latest_transcript:
        show_overlay('answer', "No question detected.")
        return
    q = latest_transcript.strip()
    show_overlay('answer', f"Q: {q}\n\nA: ...")
    full_resp = ""
    token = QApplication.instance()._backend_token
    if token and backend_get_credits(token) <= 0:
        show_overlay('answer', "Not enough credits.")
        return
    try:
        for chunk in get_response_from_chat_stream(chat, q):
            full_resp += chunk
            show_overlay('answer', f"Q: {q}\n\nA: {full_resp}")
        if token:
            backend_deduct_and_log(token, q, full_resp)
    except Exception as e:
        show_overlay('answer', f"AI error: {e}")
    finally:
        show_overlay('question', "Listening...")
        latest_transcript = ""

def handle_transcription(text, is_final):
    global latest_transcript
    # set latest_transcript (streaming or final)
    latest_transcript = text
    show_overlay('question', latest_transcript)

# =========================
# Application class
# =========================
class MainApplication(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self._backend_token = None

        # Show login/launcher
        self.login_window = None
        token = load_token()
        if token:
            try:
                print("[AUTO LOGIN] Using saved token")
                self._backend_token = token
                self.launcher_window = LauncherWindow()
                self.launcher_window.show()
                return
            except Exception:
                pass

        self.login_window = LauncherWindow()
        self.login_window.show()

    def start_main_app(self, chat_instance, device_index, assembly_key, ocr_key):
        """Start the main interview assistant with overlay and transcription."""
        global chat, transcription_thread, overlay_window, stop_event
        chat = chat_instance
        set_backend_token(self._backend_token)

        # Create and show floating overlay
        overlay_window = FloatingOverlay(
            process_callback=get_ai_answer,
            capture_callback=get_answer_from_screen,
            stop_callback=stop_assistant
        )
        overlay_window.show()

        # reset stop_event
        stop_event = threading.Event()
        # Start transcription thread: note parameter order (api_key, callback, stop_event, device_index)
        transcription_thread = start_transcription_thread(assembly_key, handle_transcription, stop_event, device_index)

        # Hide launcher window if present
        if hasattr(self, 'launcher_window') and self.launcher_window:
            try:
                self.launcher_window.hide()
            except Exception:
                pass

def stop_assistant():
    """Stop the assistant and return to launcher"""
    global stop_event, overlay_window, transcription_thread
    
    print("Stopping assistant...")
    
    # Set stop event to signal all threads to stop
    if stop_event:
        stop_event.set()
    
    # Wait for transcription thread to finish
    if transcription_thread and transcription_thread.is_alive():
        print("Waiting for transcription thread to stop....")
        transcription_thread.join(timeout=3.0)  # Wait up to 3 seconds
        if transcription_thread.is_alive():
            print("Warning: Transcription thread did not stop gracefully")
    
    # Close overlay window
    if overlay_window:
        try:
            overlay_window.close()
        except Exception as e:
            print(f"Error closing overlay: {e}")
    
    # Reset global variables
    overlay_window = None
    transcription_thread = None
    
    # Show launcher window again
    app = QApplication.instance()
    if hasattr(app, 'launcher_window') and app.launcher_window:
        app.launcher_window.show()
        print("Returned to launcher window")
    else:
        print("No launcher window found, exiting application")
        app.quit()

def listen_for_escape_key():
    try:
        import keyboard
        keyboard.wait("esc")
        if QApplication.instance():
            QApplication.instance().quit()
    except Exception:
        pass

if __name__=="__main__":
    esc_thread=threading.Thread(target=listen_for_escape_key,daemon=True)
    esc_thread.start()
    app=MainApplication(sys.argv)
    sys.exit(app.exec_())
