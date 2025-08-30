# main_for_api.py
import sys, threading, os, requests, json, mss
from PyQt5.QtWidgets import (
    QApplication, QWidget, QFormLayout, QLineEdit, QPushButton,
    QVBoxLayout, QLabel, QFileDialog, QComboBox, QMessageBox
)
from PyQt5.QtCore import Qt
from dotenv import load_dotenv

from resume_parser import get_resume_summary
from ai_engine import configure_google_ai, build_chat, get_response_from_chat_stream, estimate_tokens
from speech_api1 import start_transcription_thread, set_backend_token, get_audio_devices
from overlay_ui2 import FloatingOverlay, show_overlay

# =========================
# Load ENV
# =========================
load_dotenv()
GEMINI_KEY = os.getenv("gemini_llm6")
ASSEMBLY_KEY = os.getenv("assembly_api_key")
OCR_API_KEY = os.getenv("ocr")

# =========================
# Backend config
# =========================
API_BASE = "http://127.0.0.1:8000"
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
def backend_login(username, password):
    try:
        r = requests.post(f"{API_BASE}/auth/login", data={"username": username, "password": password}, timeout=8)
        if r.status_code == 200:
            return r.json().get("access_token")
    except Exception as e:
        print("[LOGIN ERROR]", e)
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

def save_token(token): 
    with open(TOKEN_FILE, "w") as f: json.dump({"access_token": token}, f)

def load_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            return json.load(f).get("access_token")
    return None

# =========================
# OCR / AI pipeline (unchanged)
# =========================
def get_answer_from_screen():
    global overlay_window
    def do_capture():
        screenshot_path = "screenshot.png"
        try:
            with mss.mss() as sct:
                sct.shot(mon=-1, output=screenshot_path)
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
    if not OCR_API_KEY:
        show_overlay('answer', "Error: OCR key missing")
        return
    try:
        show_overlay('question', "OCR processing...")
        payload = {'isOverlayRequired': False, 'apikey': OCR_API_KEY, 'language': 'eng'}
        with open(image_path, 'rb') as f:
            r = requests.post("https://api.ocr.space/parse/image", files={'filename': f}, data=payload, timeout=15)
        result = r.json()
        extracted = result['ParsedResults'][0]['ParsedText'].strip()
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
        if os.path.exists(image_path): os.remove(image_path)

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
    if stop_event.is_set(): return
    if is_final:
        latest_transcript = text
    else:
        latest_transcript = text
    show_overlay('question', latest_transcript)

# =========================
# GUI Windows
# =========================
class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login - AI Interview Assistant")
        self.setGeometry(600, 300, 400, 200)

        layout = QFormLayout()
        self.user = QLineEdit()
        self.pw = QLineEdit(); self.pw.setEchoMode(QLineEdit.Password)
        self.btn = QPushButton("Login")
        self.btn.clicked.connect(self.do_login)

        layout.addRow("Username:", self.user)
        layout.addRow("Password:", self.pw)
        layout.addRow(self.btn)
        self.setLayout(layout)

        # Modern stylesheet
        self.setStyleSheet("""
            QWidget { background: #1e1e2f; color: white; font-size: 14px; }
            QLineEdit { padding: 8px; border: 1px solid #444; border-radius: 6px; }
            QPushButton { background: #4e73df; color: white; padding: 8px; border-radius: 6px; }
            QPushButton:hover { background: #3751c5; }
        """)

    def do_login(self):
        token = backend_login(self.user.text(), self.pw.text())
        if token:
            QApplication.instance()._backend_token = token
            save_token(token)
            self.close()
            self.launcher = LauncherWindow()
            self.launcher.show()
        else:
            QMessageBox.warning(self, "Error", "Login failed")

class LauncherWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Setup Assistant")
        self.setGeometry(500, 250, 450, 350)

        lay = QVBoxLayout()

        self.balance_label = QLabel("Credits: ...")
        lay.addWidget(self.balance_label, alignment=Qt.AlignCenter)

        self.refresh_btn = QPushButton("Refresh Balance")
        self.refresh_btn.clicked.connect(self.refresh_balance)
        lay.addWidget(self.refresh_btn)

        self.logout_btn = QPushButton("Logout")
        self.logout_btn.clicked.connect(self.logout)
        lay.addWidget(self.logout_btn)

        # Resume + device
        self.resume_btn = QPushButton("Select Resume")
        self.resume_btn.clicked.connect(self.load_resume)
        self.resume_lbl = QLabel("No resume selected")
        lay.addWidget(self.resume_btn)
        lay.addWidget(self.resume_lbl)

        self.device_combo = QComboBox()
        for d in get_audio_devices():
            self.device_combo.addItem(f"{d['name']} (idx {d['index']})", d['index'])
        lay.addWidget(QLabel("Select Audio Device:"))
        lay.addWidget(self.device_combo)

        self.start_btn = QPushButton("Start Interview Assistant")
        self.start_btn.clicked.connect(self.start_assistant)
        lay.addWidget(self.start_btn)

        self.setLayout(lay)

        # Styling
        self.setStyleSheet("""
            QWidget { background: #f5f7fb; color: #2e2e3f; font-size: 14px; }
            QLabel { font-size: 14px; margin: 4px; }
            QPushButton { background: #28a745; color: white; padding: 10px; border-radius: 8px; }
            QPushButton:hover { background: #218838; }
            QComboBox { padding: 6px; border-radius: 6px; border: 1px solid #aaa; }
        """)

        self.resume_summary = None
        self.refresh_balance()

    def refresh_balance(self):
        token = QApplication.instance()._backend_token
        if token:
            credits = backend_get_credits(token)
            self.balance_label.setText(f"Credits: {credits}")
        else:
            self.balance_label.setText("Credits: N/A")

    def logout(self):
        if os.path.exists(TOKEN_FILE): os.remove(TOKEN_FILE)
        QMessageBox.information(self, "Logged out", "You will need to login next time.")
        QApplication.instance().quit()

    def load_resume(self):
        path, _ = QFileDialog.getOpenFileName(self,"Select Resume","","PDF Files (*.pdf)")
        if path:
            self.resume_lbl.setText(os.path.basename(path))
            self.resume_summary = get_resume_summary(path)
    def start_assistant(self):
        if not (self.resume_summary and GEMINI_KEY and ASSEMBLY_KEY and OCR_API_KEY):
            QMessageBox.warning(self, "Error", "Missing resume or API keys in .env")
            return
        try:
            configure_google_ai(GEMINI_KEY)
            global chat, transcription_thread, overlay_window
            chat = build_chat(self.resume_summary)
            device_index = self.device_combo.currentData()
            token = QApplication.instance()._backend_token
            set_backend_token(token)
            transcription_thread = start_transcription_thread(
                ASSEMBLY_KEY, handle_transcription, stop_event, device_index
            )

            if transcription_thread:
                # Define callback when overlay closes
                def on_overlay_closed():
                    self.show()   # bring back launcher instead of quitting
                    global overlay_window
                    overlay_window = None

                overlay_window = FloatingOverlay(
                    process_callback=get_ai_answer,
                    stop_callback=on_overlay_closed,
                    capture_callback=get_answer_from_screen
                )
                overlay_window.show()
                self.hide()   # hide launcher instead of closing it
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    

# =========================
# Application class
# =========================
class MainApplication(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self._backend_token = None

        token = load_token()
        if token:
            try:
                r = requests.get(f"{API_BASE}/auth/me", headers={"Authorization": f"Bearer {token}"}, timeout=6)
                if r.status_code == 200:
                    print("[AUTO LOGIN] Using saved token")
                    self._backend_token = token
                    self.launcher = LauncherWindow()
                    self.launcher.show()
                    return
            except:
                pass
            print("[AUTO LOGIN FAILED] Token expired")

        self.login = LoginWindow()
        self.login.show()

def listen_for_escape_key():
    import keyboard
    keyboard.wait("esc")
    if QApplication.instance(): QApplication.instance().quit()

if __name__=="__main__":
    esc_thread=threading.Thread(target=listen_for_escape_key,daemon=True)
    esc_thread.start()
    app=MainApplication(sys.argv)
    sys.exit(app.exec_())
