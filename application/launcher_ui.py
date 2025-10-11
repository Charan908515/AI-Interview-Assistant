# launcher_ui.py
import os, json, requests
from dotenv import load_dotenv
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel,
    QComboBox, QApplication, QMessageBox, QLineEdit, QHBoxLayout,
    QFrame, QSizePolicy, QProgressBar
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QIcon, QPixmap, QPainter, QBrush, QLinearGradient
from PyQt5.QtWidgets import QGraphicsDropShadowEffect

# Internal imports
from resume_parser import get_resume_summary
from ai_engine import configure_google_ai, build_chat
from speech_api1 import get_audio_devices

# Load environment keys
load_dotenv()
GEMINI_KEY = os.getenv("gemini_llm2")
ASSEMBLY_KEY = os.getenv("assembly_api_key")
OCR_API_KEY = os.getenv("ocr")

API_BASE = "https://se-project-backend-ddr9.onrender.com"
TOKEN_FILE = "token.json"


def save_token_local(token: str):
    try:
        with open(TOKEN_FILE, "w") as f:
            json.dump({"access_token": token}, f)
    except Exception:
        pass


class LauncherWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Interview Assistant")
        self.setGeometry(80, 40, 820, 900)
        self.setFixedSize(820, 900)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Runtime
        self.resume_path = None
        self.resume_summary = None
        self.login_error_label = None
        self.login_spinner = None
        self.resume_spinner = None

        self.init_ui()
        self.setup_animations()
        self.setup_input_cursors()

    def init_ui(self):
        # Outer container
        self.container = QFrame(self)
        self.container.setGeometry(20, 20, 780, 860)
        self.container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                  stop:0 rgba(99,102,241,0.95), stop:1 rgba(236,72,153,0.95));
                border-radius: 22px;
            }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 10)
        self.container.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        # --- Top bar with close button ---
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0, 0, 0, 0)

        title = QLabel("AI Interview Assistant")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: white;")
        top_bar.addWidget(title)
        top_bar.addStretch()

        close_btn = QPushButton("✕")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setFixedSize(34, 34)
        close_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.1);
                color: white;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(255,100,100,0.4);
            }
        """)
        close_btn.clicked.connect(self.close)
        top_bar.addWidget(close_btn)

        layout.addLayout(top_bar)

        # --- Login Section ---
        self.login_frame = QFrame()
        self.login_frame.setStyleSheet("background: transparent;")
        login_layout = QVBoxLayout(self.login_frame)
        login_layout.setContentsMargins(60, 40, 60, 40)
        login_layout.setSpacing(14)

        logo_label = QLabel("🤖")
        logo_label.setFont(QFont("Segoe UI Emoji", 64))
        logo_label.setAlignment(Qt.AlignCenter)
        login_layout.addWidget(logo_label)

        hint = QLabel("Sign in to your account")
        hint.setFont(QFont("Segoe UI", 14, QFont.Bold))
        hint.setAlignment(Qt.AlignCenter)
        hint.setStyleSheet("color: white;")
        login_layout.addWidget(hint)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username or email")
        self.username_input.setFixedHeight(50)
        self.username_input.setCursor(Qt.IBeamCursor)
        self.username_input.setStyleSheet(self._input_style())
        # Ensure cursor is visible
        self.username_input.setAttribute(Qt.WA_MacShowFocusRect, False)
        self.username_input.setFocusPolicy(Qt.StrongFocus)
        login_layout.addWidget(self.username_input)

        # Password input container
        password_container = QHBoxLayout()
        password_container.setSpacing(0)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(50)
        self.password_input.setCursor(Qt.IBeamCursor)
        self.password_input.setStyleSheet(self._input_style_with_embedded_button())
        # Ensure cursor is visible
        self.password_input.setAttribute(Qt.WA_MacShowFocusRect, False)
        self.password_input.setFocusPolicy(Qt.StrongFocus)
        
        # Password visibility toggle button
        self.password_toggle_btn = QPushButton("🙈")  # Monkey covering eyes (hidden)
        self.password_toggle_btn.setFixedSize(40, 40)
        self.password_toggle_btn.setCursor(Qt.PointingHandCursor)
        self.password_toggle_btn.setStyleSheet(self._embedded_button_style())
        self.password_toggle_btn.clicked.connect(self.toggle_password_visibility)
        self.password_visible = False
        
        password_container.addWidget(self.password_input)
        password_container.addWidget(self.password_toggle_btn)
        login_layout.addLayout(password_container)

        # Login error label
        self.login_error_label = QLabel()
        self.login_error_label.setStyleSheet("""
            QLabel {
                color: #ff6b6b;
                background: rgba(255, 107, 107, 0.1);
                border: 1px solid rgba(255, 107, 107, 0.3);
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 12px;
                font-weight: bold;
            }
        """)
        self.login_error_label.setAlignment(Qt.AlignCenter)
        self.login_error_label.hide()
        login_layout.addWidget(self.login_error_label)

        # Login button with spinner container
        login_container = QHBoxLayout()
        login_btn = QPushButton("🔐 Login")
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.setFixedHeight(46)
        login_btn.setStyleSheet(self._primary_button_style())
        login_btn.clicked.connect(self.try_login)
        self.login_btn = login_btn
        
        # Login spinner
        self.login_spinner = QProgressBar()
        self.login_spinner.setRange(0, 0)  # Indeterminate progress
        self.login_spinner.setFixedHeight(46)
        self.login_spinner.setStyleSheet("""
            QProgressBar {
                background: rgba(255,255,255,0.1);
                border: none;
                border-radius: 14px;
                text-align: center;
                color: white;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #42e695, stop:1 #3bb2b8);
                border-radius: 14px;
            }
        """)
        self.login_spinner.hide()
        
        login_container.addWidget(login_btn)
        login_container.addWidget(self.login_spinner)
        login_layout.addLayout(login_container)

        layout.addWidget(self.login_frame)
        layout.addStretch()

        # --- Dashboard Section ---
        self.dashboard_frame = self.build_dashboard_frame()
        layout.addWidget(self.dashboard_frame)
        self.dashboard_frame.hide()

    def build_dashboard_frame(self):
        frame = QFrame()
        frame.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(40, 20, 40, 20)
        layout.setSpacing(16)

        # Welcome + Credits row
        top_row = QHBoxLayout()
        self.welcome_label = QLabel("Welcome")
        self.welcome_label.setFont(QFont("Segoe UI", 13, QFont.Bold))
        self.welcome_label.setStyleSheet("color: white;")
        top_row.addWidget(self.welcome_label)

        top_row.addStretch()

        self.credits_label = QLabel("Credits: —")
        self.credits_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.credits_label.setStyleSheet("color: #ffe082;")
        top_row.addWidget(self.credits_label)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.setFixedHeight(32)
        refresh_btn.setStyleSheet(self._secondary_button_style())
        refresh_btn.clicked.connect(self.load_credits)
        top_row.addWidget(refresh_btn)

        logout_btn = QPushButton("Logout")
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.setStyleSheet(self._secondary_button_style())
        logout_btn.clicked.connect(self.logout_from_dashboard)
        top_row.addWidget(logout_btn)

        layout.addLayout(top_row)

        # Resume upload
        resume_card = self._make_card()
        r_layout = QHBoxLayout(resume_card)
        r_label = QLabel("📄 Resume:")
        r_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        r_label.setStyleSheet("color: white;")
        r_layout.addWidget(r_label)
        
        self.resume_status = QLabel("No resume selected")
        self.resume_status.setStyleSheet("color: rgba(255,255,255,0.8); font-style: italic;")
        r_layout.addWidget(self.resume_status)
        
        # Resume spinner
        self.resume_spinner = QProgressBar()
        self.resume_spinner.setRange(0, 0)
        self.resume_spinner.setFixedSize(24, 24)
        self.resume_spinner.setStyleSheet("""
            QProgressBar {
                background: transparent;
                border: 2px solid rgba(255,255,255,0.3);
                border-radius: 12px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #42e695, stop:1 #3bb2b8);
                border-radius: 10px;
            }
        """)
        self.resume_spinner.hide()
        r_layout.addWidget(self.resume_spinner)
        
        resume_btn = QPushButton("Select PDF")
        resume_btn.setCursor(Qt.PointingHandCursor)
        resume_btn.setStyleSheet(self._secondary_button_style())
        resume_btn.clicked.connect(self.load_resume)
        self.resume_btn = resume_btn
        r_layout.addWidget(resume_btn)
        layout.addWidget(resume_card)

        # Microphone
        mic_card = self._make_card()
        m_layout = QHBoxLayout(mic_card)
        m_label = QLabel("🎤 Microphone:")
        m_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        m_label.setStyleSheet("color: white;")
        m_layout.addWidget(m_label)
        self.device_combo = QComboBox()
        self.device_combo.setStyleSheet("""
            QComboBox {
                background: rgba(255,255,255,0.1);
                color: white;
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 12px;
            }
            QComboBox:hover {
                background: rgba(255,255,255,0.15);
                border: 1px solid rgba(255,255,255,0.3);
            }
            QComboBox::drop-down {
                border: none;
                background: transparent;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border: 2px solid white;
                border-top: none;
                border-right: none;
                width: 6px;
                height: 6px;
                transform: rotate(-45deg);
                margin-right: 8px;
            }
            QComboBox QAbstractItemView {
                background: rgba(40, 44, 52, 0.95);
                color: white;
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 8px;
                selection-background-color: rgba(66, 230, 149, 0.3);
                outline: none;
            }
            QComboBox QAbstractItemView::item {
                padding: 8px 12px;
                border: none;
                color: white;
            }
            QComboBox QAbstractItemView::item:selected {
                background: rgba(66, 230, 149, 0.3);
                color: white;
            }
            QComboBox QAbstractItemView::item:hover {
                background: rgba(255,255,255,0.1);
                color: white;
            }
        """)
        try:
            devices = get_audio_devices()
            if devices:
                for d in devices:
                    self.device_combo.addItem(f"{d['name']} (index {d['index']})", d['index'])
            else:
                self.device_combo.addItem("No input devices found", -1)
        except Exception:
            self.device_combo.addItem("Device listing failed", -1)
        m_layout.addWidget(self.device_combo)
        layout.addWidget(mic_card)

        # Start button
        start_btn = QPushButton("🚀 Start Assistant")
        start_btn.setCursor(Qt.PointingHandCursor)
        start_btn.setFixedHeight(52)
        start_btn.setStyleSheet(self._primary_button_style())
        start_btn.clicked.connect(self.start_assistant)
        layout.addWidget(start_btn, alignment=Qt.AlignRight)

        return frame

    # ---------------- Helpers ----------------
    def _make_card(self):
        f = QFrame()
        f.setStyleSheet("QFrame { background: rgba(255,255,255,0.05); border-radius: 12px; padding: 12px; }")
        return f

    def _input_style(self):
        return """
        QLineEdit {
            background: rgba(40, 44, 52, 0.9);
            border: 1px solid rgba(255,255,255,0.3);
            color: white;
            border-radius: 10px;
            padding: 8px 12px;
            font-size: 13px;
            selection-background-color: rgba(66, 230, 149, 0.4);
            selection-color: white;
        }
        QLineEdit:focus {
            background: rgba(30, 34, 42, 0.95);
            border: 2px solid rgba(66, 230, 149, 0.8);
            outline: none;
        }
        QLineEdit:hover {
            background: rgba(35, 39, 47, 0.92);
            border: 1px solid rgba(255,255,255,0.4);
        }
        """
    
    def _input_style_with_button(self):
        return """
        QLineEdit {
            background: rgba(40, 44, 52, 0.9);
            border: 1px solid rgba(255,255,255,0.3);
            border-top-right-radius: 0px;
            border-bottom-right-radius: 0px;
            border-right: none;
            color: white;
            border-radius: 10px;
            padding: 8px 12px;
            font-size: 13px;
            selection-background-color: rgba(66, 230, 149, 0.4);
            selection-color: white;
        }
        QLineEdit:focus {
            background: rgba(30, 34, 42, 0.95);
            border: 2px solid rgba(66, 230, 149, 0.8);
            border-right: none;
            outline: none;
        }
        QLineEdit:focus {
            background: rgba(30, 34, 42, 0.95);
            border: 2px solid rgba(66, 230, 149, 0.8);
            outline: none;
        }
        QLineEdit:hover {
            background: rgba(35, 39, 47, 0.92);
            border: 1px solid rgba(255,255,255,0.4);
        }
        """
    
    def _password_toggle_style(self):
        return """
        QPushButton {
            background: rgba(40, 44, 52, 0.9);
            border: 1px solid rgba(255,255,255,0.3);
            border-left: none;
            border-top-left-radius: 0px;
            border-bottom-left-radius: 0px;
            border-radius: 10px;
            color: white;
            font-size: 16px;
            font-weight: bold;
        }
        QPushButton:hover {
            background: rgba(35, 39, 47, 0.92);
            border: 1px solid rgba(255,255,255,0.4);
            border-left: none;
        }
        QPushButton:pressed {
            background: rgba(25, 29, 37, 0.95);
        }
        """
    
    def _input_style_with_embedded_button(self):
        return """
        QLineEdit {
            background: rgba(40, 44, 52, 0.9);
            border: 1px solid rgba(255,255,255,0.3);
            color: white;
            border-radius: 10px;
            padding: 8px 50px 8px 12px;
            font-size: 14px;
            selection-background-color: rgba(66, 230, 149, 0.4);
            selection-color: white;
        }
        QLineEdit:focus {
            background: rgba(30, 34, 42, 0.95);
            border: 2px solid rgba(66, 230, 149, 0.8);
            outline: none;
        }
        QLineEdit:hover {
            background: rgba(35, 39, 47, 0.92);
            border: 1px solid rgba(255,255,255,0.4);
        }
        """
    
    def _embedded_button_style(self):
        return """
        QPushButton {
            background: transparent;
            border: none;
            color: white;
            font-size: 16px;
            font-weight: bold;
            border-radius: 6px;
            margin: 5px;
        }
        QPushButton:hover {
            background: rgba(255,255,255,0.1);
        }
        QPushButton:pressed {
            background: rgba(255,255,255,0.2);
        }
        """

    def _primary_button_style(self):
        return """
        QPushButton {
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #42e695, stop:1 #3bb2b8);
            color: #012;
            font-weight: bold;
            border-radius: 14px;
            padding: 10px 20px;
        }
        QPushButton:hover { transform: translateY(-2px); }
        """

    def _secondary_button_style(self):
        return """
        QPushButton {
            background: rgba(255,255,255,0.12);
            color: white;
            border-radius: 8px;
            padding: 6px 10px;
        }
        QPushButton:hover { background: rgba(255,255,255,0.2); }
        """

    def setup_animations(self):
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(400)
        self.fade_anim.setEasingCurve(QEasingCurve.InOutQuad)
    
    def setup_input_cursors(self):
        """Ensure input field cursors are properly configured"""
        # Force cursor visibility and proper behavior
        if hasattr(self, 'username_input'):
            self.username_input.setCursorPosition(0)
            self.username_input.setReadOnly(False)
        if hasattr(self, 'password_input'):
            self.password_input.setCursorPosition(0)
            self.password_input.setReadOnly(False)

    def showEvent(self, e):
        super().showEvent(e)
        self.setWindowOpacity(0)
        self.fade_anim.setStartValue(0)
        self.fade_anim.setEndValue(1)
        self.fade_anim.start()

    # ---------------- Logic ----------------
    def try_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        # Hide previous error
        self.login_error_label.hide()
        
        if not username or not password:
            self.show_login_error("Please enter username and password.")
            return
            
        # Show spinner, hide button
        self.login_btn.hide()
        self.login_spinner.show()
        
        # Use QTimer to allow UI to update before making request
        QTimer.singleShot(100, lambda: self._perform_login(username, password))
    
    def _perform_login(self, username, password):
        try:
            r = requests.post(f"{API_BASE}/auth/login", data={"username": username, "password": password}, timeout=8)
            if r.status_code == 200:
                token = r.json().get("access_token")
                if not token:
                    self.show_login_error("No token returned from server.")
                    return
                app = QApplication.instance()
                app._backend_token = token
                save_token_local(token)
                self.welcome_label.setText(f"Welcome, {username}")
                self.login_frame.hide()
                self.dashboard_frame.show()
                self.load_credits()
            else:
                error_msg = "Invalid username or password."
                try:
                    error_data = r.json()
                    if "detail" in error_data:
                        error_msg = error_data["detail"]
                except:
                    pass
                self.show_login_error(error_msg)
        except requests.exceptions.Timeout:
            self.show_login_error("Connection timeout. Please try again.")
        except requests.exceptions.ConnectionError:
            self.show_login_error("Cannot connect to server. Please check your connection.")
        except Exception as e:
            self.show_login_error(f"Login error: {str(e)}")
        finally:
            # Hide spinner, show button
            self.login_spinner.hide()
            self.login_btn.show()
    
    def show_login_error(self, message):
        self.login_error_label.setText(message)
        self.login_error_label.show()
        # Auto-hide after 5 seconds
        QTimer.singleShot(5000, self.login_error_label.hide)
    
    def toggle_password_visibility(self):
        """Toggle password visibility with monkey emoji animation"""
        if self.password_visible:
            # Hide password
            self.password_input.setEchoMode(QLineEdit.Password)
            self.password_toggle_btn.setText("🙈")  # Monkey covering eyes
            self.password_visible = False
        else:
            # Show password
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.password_toggle_btn.setText("🙉")  # Monkey with open eyes
            self.password_visible = True

    def logout_from_dashboard(self):
        confirm = QMessageBox.question(self, "Logout", "Are you sure you want to logout?",
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirm == QMessageBox.Yes:
            app = QApplication.instance()
            app._backend_token = None
            try:
                if os.path.exists(TOKEN_FILE): os.remove(TOKEN_FILE)
            except Exception: pass
            self.dashboard_frame.hide()
            self.login_frame.show()
            self.username_input.clear()
            self.password_input.clear()
            self.resume_status.setText("No resume selected")
            self.credits_label.setText("Credits: —")

    def load_credits(self):
        app = QApplication.instance()
        token = getattr(app, "_backend_token", None)
        if not token:
            self.credits_label.setText("Credits: —")
            return
        try:
            r = requests.get(f"{API_BASE}/credits/balance", headers={"Authorization": f"Bearer {token}"}, timeout=6)
            if r.status_code == 200:
                c = r.json().get("credits", 0)
                self.credits_label.setText(f"Credits: {c}")
            else:
                self.credits_label.setText("Credits: error")
        except:
            self.credits_label.setText("Credits: error")

    def load_resume(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Resume PDF", "", "PDF Files (*.pdf)")
        if path:
            self.resume_path = path
            filename = os.path.basename(path)
            
            # Show spinner and update status
            self.resume_status.setText(f"Processing {filename}...")
            self.resume_spinner.show()
            self.resume_btn.setEnabled(False)
            
            # Use QTimer to allow UI to update
            QTimer.singleShot(100, lambda: self._process_resume(path, filename))
    
    def _process_resume(self, path, filename):
        try:
            summary = get_resume_summary(path)
            self.resume_summary = summary
            
            # Show success with tick
            self.resume_status.setText(f"✅ {filename}")
            self.resume_status.setStyleSheet("color: #42e695; font-weight: bold;")
        except Exception as e:
            # Show error
            self.resume_status.setText(f"❌ Failed to process {filename}")
            self.resume_status.setStyleSheet("color: #ff6b6b; font-style: italic;")
            QMessageBox.critical(self, "Resume Error", f"Failed to summarize resume: {e}")
        finally:
            # Hide spinner and re-enable button
            self.resume_spinner.hide()
            self.resume_btn.setEnabled(True)

    def start_assistant(self):
        if not self.resume_summary:
            QMessageBox.warning(self, "Missing", "Please upload your resume first.")
            return
        if not all([GEMINI_KEY, ASSEMBLY_KEY, OCR_API_KEY]):
            QMessageBox.critical(self, "Missing Keys", "API keys missing in .env file.")
            return

        app = QApplication.instance()
        token = getattr(app, "_backend_token", None)
        if not token:
            QMessageBox.warning(self, "Login required", "Please login first.")
            return

        try:
            configure_google_ai(GEMINI_KEY)
            chat_instance = build_chat(self.resume_summary)
        except Exception as e:
            QMessageBox.critical(self, "AI Error", f"Gemini setup failed: {e}")
            return

        device_index = self.device_combo.currentData()
        if device_index is None or device_index == -1:
            QMessageBox.warning(self, "Device", "Select a valid microphone.")
            return

        try:
            app.start_main_app(chat_instance, device_index, ASSEMBLY_KEY, OCR_API_KEY)
            self.hide()
        except Exception as e:
            QMessageBox.critical(self, "Start failed", f"Assistant failed to start: {e}")
