# overlay_ui2.py

import sys
import ctypes
from queue import Queue
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QSizePolicy, QFrame, QPushButton
)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtGui import QFont

# Constant to exclude the window from screen capture
WDA_EXCLUDEFROMCAPTURE = 0x11
user32 = ctypes.windll.user32
message_queue = Queue()

class FloatingOverlay(QWidget):
    def __init__(self, process_callback=None, stop_callback=None, capture_callback=None):
        super().__init__()
        self.process_callback = process_callback
        self.stop_callback = stop_callback
        self.capture_callback = capture_callback
        self._setup_window()
        self.init_ui()
        self._setup_animations()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_queue)
        self.timer.start(100)

    def _setup_window(self):
        screen_geometry = QApplication.primaryScreen().geometry()
        self.initial_height = 240
        self.setGeometry(0, 50, screen_geometry.width(), self.initial_height)
        self.setMinimumHeight(self.initial_height)
        self.setWindowTitle("Private Overlay")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)

    def init_ui(self):
        self.container = QWidget(self)
        self.container.setStyleSheet("background-color: rgba(20, 30, 55, 230); border-radius: 12px;")

        main_layout = QHBoxLayout(self.container)
        main_layout.setContentsMargins(20, 15, 15, 15)
        main_layout.setSpacing(15)

        qa_layout = QVBoxLayout()
        qa_layout.setSpacing(10)
        self.question_label = QLabel("Listening...")
        self.question_label.setWordWrap(True)
        self.answer_label = QLabel("...")
        self.answer_label.setWordWrap(True)
        self.question_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.answer_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        label_style = "background-color: transparent; color: #EAEAEA; font-family: Segoe UI;"
        self.question_label.setStyleSheet(f"{label_style} font-size: 10pt;")
        self.answer_label.setStyleSheet(f"{label_style} font-size: 11pt; font-weight: 600;")
        
        qa_layout.addLayout(self._create_labeled_layout("Q:", self.question_label))
        qa_layout.addLayout(self._create_labeled_layout("A:", self.answer_label))

        control_layout = QVBoxLayout()
        control_layout.setSpacing(10)
        
        # === FIX STARTS HERE ===
        # Use stretchable spacers to center the widgets vertically.
        # This is more robust for size calculations than setAlignment.
        control_layout.addStretch()

        self.status_icon_label = QLabel("🎙️")
        self.status_icon_label.setFont(QFont("Segoe UI Emoji", 32))
        self.status_icon_label.setAlignment(Qt.AlignCenter)
        
        self.process_button = QPushButton("Get Answer")
        self.process_button.setCursor(Qt.PointingHandCursor)
        self.process_button.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2; color: white; border: none;
                border-radius: 5px; padding: 10px 15px;
                font-family: 'Segoe UI'; font-size: 10pt; font-weight: bold;
            }
            QPushButton:hover { background-color: #5B9EE5; }
            QPushButton:pressed { background-color: #3A8ADB; }
        """)
        self.process_button.clicked.connect(self.on_process_click)

        self.capture_button = QPushButton("Capture Screen")
        self.capture_button.setCursor(Qt.PointingHandCursor)
        self.capture_button.setStyleSheet("""
            QPushButton {
                background-color: #3B9D7E; color: white; border: none;
                border-radius: 5px; padding: 10px 15px;
                font-family: 'Segoe UI'; font-size: 10pt; font-weight: bold;
            }
            QPushButton:hover { background-color: #4CB591; }
            QPushButton:pressed { background-color: #2A8C6B; }
        """)
        self.capture_button.clicked.connect(self.on_capture_click)

        self.stop_button = QPushButton("Stop")
        self.stop_button.setCursor(Qt.PointingHandCursor)
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #D83C3E; color: white; border: none;
                border-radius: 5px; padding: 8px 15px;
                font-family: 'Segoe UI'; font-size: 10pt; font-weight: bold;
            }
            QPushButton:hover { background-color: #E54B4D; }
            QPushButton:pressed { background-color: #C42A2C; }
        """)
        self.stop_button.clicked.connect(self.on_stop_click)
        
        control_layout.addWidget(self.status_icon_label)
        control_layout.addWidget(self.process_button)
        control_layout.addWidget(self.capture_button)
        control_layout.addWidget(self.stop_button)
        
        # Add another spacer at the bottom
        control_layout.addStretch()
        # === FIX ENDS HERE ===

        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setStyleSheet("color: rgba(60, 120, 220, 0.3);")

        main_layout.addLayout(qa_layout, stretch=8)
        main_layout.addWidget(separator)
        main_layout.addLayout(control_layout, stretch=1)

        top_level_layout = QVBoxLayout(self)
        top_level_layout.setContentsMargins(0, 0, 0, 0)
        top_level_layout.addWidget(self.container)
        self.setLayout(top_level_layout)

    def on_capture_click(self):
        if self.capture_callback:
            self.status_icon_label.setText("📸")
            self.answer_label.setText("...")
            self.capture_callback()

    def on_process_click(self):
        if self.process_callback:
            self.status_icon_label.setText("🤔")
            self.answer_label.setText("...")
            self.process_callback()

    def on_stop_click(self):
        if self.stop_callback:
            self.stop_callback()

    def _create_labeled_layout(self, prefix_text, label_widget):
        layout = QHBoxLayout()
        prefix_label = QLabel(prefix_text)
        prefix_label.setStyleSheet("background: transparent; color: #6A85B3; font-family: 'Segoe UI'; font-size: 12pt; font-weight: 700;")
        prefix_label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        layout.addWidget(prefix_label, alignment=Qt.AlignTop)
        layout.addWidget(label_widget)
        return layout

    def _setup_animations(self):
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(300)
        self.fade_animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.resize_animation = QPropertyAnimation(self, b"geometry")
        self.resize_animation.setDuration(250)
        self.resize_animation.setEasingCurve(QEasingCurve.InOutCubic)

    def showEvent(self, event):
        super().showEvent(event)
        try:
            hwnd = self.winId().__int__()
            user32.SetWindowDisplayAffinity(hwnd, WDA_EXCLUDEFROMCAPTURE)
        except AttributeError:
            pass # Fails gracefully on non-Windows OS
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.start()

    def check_queue(self):
        if not message_queue.empty():
            message_type, text = message_queue.get()
            if message_type == 'question':
                self.question_label.setText(text)
                is_final_question = text.startswith("Q:")
                
                if not is_final_question:
                    self.status_icon_label.setText("🎙️")
                else:
                    self.status_icon_label.setText("❓")
                    self.resize_to_content()
                    
            elif message_type == 'answer':
                self.answer_label.setText(text)
                if text != "...":
                    self.status_icon_label.setText("💡")
                self.resize_to_content()

    def resize_to_content(self):
        self.layout().invalidate()
        self.layout().activate()
        target_height = max(self.initial_height, self.sizeHint().height())
        current_geo = self.geometry()
        self.resize_animation.setStartValue(current_geo)
        self.resize_animation.setEndValue(QRect(current_geo.x(), current_geo.y(), current_geo.width(), target_height))
        self.resize_animation.start()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self.drag_start_position)
            event.accept()

    def closeEvent(self, event):
        print("Overlay closed, quitting application.")
        if self.stop_callback:
            self.stop_callback()
        else:
            QApplication.instance().quit()
        event.accept()


def show_overlay(message_type, text):
    message_queue.put((message_type, text))


if __name__ == '__main__':
    import sys
    import random
    
    app = QApplication(sys.argv)

    # Instantiate the overlay without any real callbacks for UI testing
    overlay = FloatingOverlay()
    overlay.show()

    # --- Dummy function to test UI text and resize updates ---
    def test_ui_updates():
        questions = [
            "Tell me about your experience with machine learning pipelines.",
            "What are your salary expectations?",
            "Q: This is a much longer finalized question to test how the window handles word wrapping and resizing."
        ]
        answers = [
            "Thinking...",
            "Based on my skills and experience, I'm expecting a competitive salary for this role. I'm happy to discuss the details further.",
            "This is a very long sample answer to demonstrate how the UI accommodates a large amount of text. The window should expand vertically, and the text should wrap correctly without being cut off. The animation should also be smooth."
        ]
        
        # Update the UI with random sample data
        show_overlay('question', random.choice(questions))
        # Show an answer after a short delay
        QTimer.singleShot(1500, lambda: show_overlay('answer', random.choice(answers)))

    # Use a QTimer to call the test function every 5 seconds
    update_timer = QTimer()
    update_timer.timeout.connect(test_ui_updates)
    update_timer.start(5000) # 5 seconds

    # Trigger the first update immediately
    test_ui_updates()
    
    sys.exit(app.exec_())