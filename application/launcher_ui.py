# launcher_ui.py
import sys
import os
import requests
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel,
    QComboBox, QApplication, QMessageBox, QLineEdit, QFormLayout
)
from resume_parser import parse_resume
from ai_engine import configure_google_ai, build_chat
from speech_api1 import get_audio_devices

API_BASE = "http://127.0.0.1:8000"

# -------------------------------
# 🔑 Login Window
# -------------------------------
class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Interview Assistant - Login")
        self.setGeometry(200, 200, 400, 200)

        layout = QFormLayout()

        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        self.login_btn = QPushButton("Login")
        self.login_btn.clicked.connect(self.try_login)

        layout.addRow("Username:", self.username_input)
        layout.addRow("Password:", self.password_input)
        layout.addWidget(self.login_btn)

        self.setLayout(layout)

    def try_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter username and password")
            return
        try:
            r = requests.post(f"{API_BASE}/auth/login", data={"username": username, "password": password}, timeout=8)
            if r.status_code == 200:
                token = r.json().get("access_token")
                QApplication.instance()._backend_token = token
                QMessageBox.information(self, "Success", "Login successful!")
                # go to launcher
                self.close()
                self.launcher = LauncherWindow()
                self.launcher.show()
            else:
                QMessageBox.warning(self, "Login failed", r.text)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

# -------------------------------
# 🚀 Launcher Window
# -------------------------------
class LauncherWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Interview Assistant - Setup")
        self.setGeometry(200, 200, 500, 300)

        layout = QVBoxLayout()

        # resume
        self.resume_btn = QPushButton("Select Resume PDF")
        self.resume_btn.clicked.connect(self.load_resume)
        self.resume_label = QLabel("No resume selected")

        # Gemini key
        self.gemini_key_btn = QPushButton("Enter Gemini API Key")
        self.gemini_key_btn.clicked.connect(self.set_gemini_key)
        self.gemini_key_label = QLabel("No Gemini key")

        # AssemblyAI key
        self.assembly_key_btn = QPushButton("Enter AssemblyAI Key")
        self.assembly_key_btn.clicked.connect(self.set_assembly_key)
        self.assembly_key_label = QLabel("No Assembly key")

        # OCR key
        self.ocr_key_btn = QPushButton("Enter OCR.space Key")
        self.ocr_key_btn.clicked.connect(self.set_ocr_key)
        self.ocr_key_label = QLabel("No OCR key")

        # device selection
        self.device_combo = QComboBox()
        devices = get_audio_devices()
        for d in devices:
            self.device_combo.addItem(f"{d['name']} (index {d['index']})", d['index'])

        # Start button
        self.start_btn = QPushButton("Start Assistant")
        self.start_btn.clicked.connect(self.start_assistant)

        layout.addWidget(self.resume_btn)
        layout.addWidget(self.resume_label)
        layout.addWidget(self.gemini_key_btn)
        layout.addWidget(self.gemini_key_label)
        layout.addWidget(self.assembly_key_btn)
        layout.addWidget(self.assembly_key_label)
        layout.addWidget(self.ocr_key_btn)
        layout.addWidget(self.ocr_key_label)
        layout.addWidget(QLabel("Select Audio Device:"))
        layout.addWidget(self.device_combo)
        layout.addStretch()
        layout.addWidget(self.start_btn)

        self.setLayout(layout)

        # store values
        self.resume_summary = None
        self.gemini_key = None
        self.assembly_key = None
        self.ocr_key = None

    def load_resume(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Resume PDF", "", "PDF Files (*.pdf)")
        if path:
            self.resume_label.setText(os.path.basename(path))
            self.resume_summary = parse_resume(path)

    def set_gemini_key(self):
        key, ok = QInputDialog.getText(self, "Gemini Key", "Enter Gemini API Key:")
        if ok and key:
            self.gemini_key = key
            self.gemini_key_label.setText("Gemini key set")

    def set_assembly_key(self):
        key, ok = QInputDialog.getText(self, "AssemblyAI Key", "Enter AssemblyAI API Key:")
        if ok and key:
            self.assembly_key = key
            self.assembly_key_label.setText("AssemblyAI key set")

    def set_ocr_key(self):
        key, ok = QInputDialog.getText(self, "OCR.space Key", "Enter OCR.space API Key:")
        if ok and key:
            self.ocr_key = key
            self.ocr_key_label.setText("OCR key set")

    def start_assistant(self):
        if not (self.resume_summary and self.gemini_key and self.assembly_key and self.ocr_key):
            QMessageBox.warning(self, "Missing Info", "Please provide all required keys and resume")
            return
        try:
            configure_google_ai(self.gemini_key)
            chat_instance = build_chat(self.resume_summary)
            device_index = self.device_combo.currentData()
            QApplication.instance().start_main_app(chat_instance, device_index, self.assembly_key, self.ocr_key)
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start assistant: {e}")

# -------------------------------
# App entry
# -------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app._backend_token = None  # will be set after login
    login_win = LoginWindow()
    login_win.show()
    sys.exit(app.exec_())
