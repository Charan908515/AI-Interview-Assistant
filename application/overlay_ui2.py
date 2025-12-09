# overlay_ui2.py

import sys
import ctypes
from queue import Queue
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QSizePolicy, QFrame, QPushButton, QScrollArea, QTextEdit
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
        self.initial_height = 280
        self.max_height = 600
        self.setGeometry(0, 50, screen_geometry.width(), self.initial_height)
        self.setMinimumHeight(self.initial_height)
        self.setMaximumHeight(self.max_height)
        self.setWindowTitle("AI Interview Assistant")
        # Qt.Tool flag ensures window doesn't appear in taskbar
        # Qt.FramelessWindowHint removes window frame
        # Qt.WindowStaysOnTopHint keeps window on top
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        # Ensure window is not shown in taskbar
        self.setAttribute(Qt.WA_ShowWithoutActivating)

    def init_ui(self):
        self.container = QWidget(self)
        self.container.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(45, 55, 72, 240), stop:1 rgba(26, 32, 44, 240));
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        """)

        main_layout = QHBoxLayout(self.container)
        main_layout.setContentsMargins(25, 20, 20, 20)
        main_layout.setSpacing(20)

        qa_layout = QVBoxLayout()
        qa_layout.setSpacing(15)
        
        # Question section with auto-expanding scroll area
        question_section = QVBoxLayout()
        question_header = QHBoxLayout()
        
        q_prefix = QLabel("Q:")
        q_prefix.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #667eea, stop:1 #764ba2);
            color: white;
            font-family: 'Segoe UI';
            font-size: 13pt;
            font-weight: 700;
            border-radius: 8px;
            padding: 8px 12px;
            margin-right: 10px;
        """)
        q_prefix.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        
        # Create a container widget for the question
        self.question_container = QWidget()
        self.question_container.setStyleSheet("background: transparent;")
        # Allow the question container to expand horizontally
        self.question_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        question_inner_layout = QVBoxLayout(self.question_container)
        question_inner_layout.setContentsMargins(0, 0, 0, 0)
        question_inner_layout.setSpacing(0)
        
        self.question_label = QLabel("Listening...")
        self.question_label.setWordWrap(True)
        self.question_label.setStyleSheet("""
            background-color: transparent; 
            color: #F7FAFC; 
            font-family: 'Segoe UI';
            font-size: 12pt; 
            line-height: 1.4;
            padding: 10px;
            margin: 0;
        """)
        question_inner_layout.addWidget(self.question_label)
        
        # Add stretch to push content to top
        question_inner_layout.addStretch()
        
        self.question_scroll = QScrollArea()
        self.question_scroll.setWidgetResizable(True)
        self.question_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.question_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.question_scroll.setWidget(self.question_container)
        self.question_scroll.setMinimumHeight(60)  # Minimum height for question area
        self.question_scroll.setMaximumHeight(200)  # Maximum height before scrolling
        self.question_scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: rgba(255, 255, 255, 0.1);
                width: 6px;
                border-radius: 3px;
                margin: 2px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.3);
                border-radius: 3px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(255, 255, 255, 0.5);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        question_header.addWidget(q_prefix)
        # Give the scroll area stretch so it takes remaining horizontal space
        question_header.addWidget(self.question_scroll, 1)
        question_section.addLayout(question_header)
        
        # Answer section with auto-expanding scroll area
        answer_section = QVBoxLayout()
        answer_header = QHBoxLayout()
        
        a_prefix = QLabel("A:")
        a_prefix.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #667eea, stop:1 #764ba2);
            color: white;
            font-family: 'Segoe UI';
            font-size: 13pt;
            font-weight: 700;
            border-radius: 8px;
            padding: 8px 12px;
            margin-right: 10px;
        """)
        a_prefix.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        
        # Create a container widget for the answer
        self.answer_container = QWidget()
        self.answer_container.setStyleSheet("""
            background: transparent;
            border: none;
        """)
        # Make container expand to fill available space
        self.answer_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        # Main layout for the answer container
        answer_inner_layout = QHBoxLayout(self.answer_container)  
        answer_inner_layout.setContentsMargins(0, 0, 0, 0)
        answer_inner_layout.setSpacing(0)
        
        # Create a container widget for the label to ensure proper sizing
        self.answer_label_container = QWidget()
        self.answer_label_container.setStyleSheet("""
            background: transparent;
            border: none;
        """)
        # Make label container expand to fill available space
        self.answer_label_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        # Layout for the label container
        self.answer_label_layout = QVBoxLayout(self.answer_label_container)
        self.answer_label_layout.setContentsMargins(10, 10, 10, 10)  
        self.answer_label_layout.setSpacing(0)

        # The actual label that will contain the answer text
        self.answer_label = QLabel("")
        self.answer_label.setWordWrap(True)
        self.answer_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.answer_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.answer_label.setStyleSheet("""
            background-color: transparent; 
            color: #F7FAFC; 
            font-family: 'Segoe UI';
            font-size: 13pt; 
            font-weight: 600; 
            line-height: 1.5;
            padding: 0;
            margin: 0;
            width: 100%;
        """)
        self.answer_label_layout.addWidget(self.answer_label)
        self.answer_label_layout.addStretch()

        # Add the label to its container
        self.answer_label_layout.addWidget(self.answer_label)
        self.answer_label_layout.addStretch()
        
        # Add the label container to the answer container with stretch
        answer_inner_layout.addWidget(self.answer_label_container, 1)
        
        # Create the scroll area for the answer
        self.answer_scroll = QScrollArea()
        self.answer_scroll.setWidgetResizable(True)
        self.answer_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.answer_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.answer_scroll.setWidget(self.answer_container)
        self.answer_scroll.setMinimumHeight(60)  # Minimum height for answer area
        self.answer_scroll.setMaximumHeight(400)  # Maximum height before scrolling
        # Make scroll area expand to fill available space
        self.answer_scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Ensure the scroll area updates its size when content changes
        self.answer_scroll.setSizeAdjustPolicy(QScrollArea.AdjustToContents)
        
        # Ensure the scroll area updates its size when content changes
        self.answer_scroll.setSizeAdjustPolicy(QScrollArea.AdjustToContents)
        
        # Function to ensure scroll reaches the end
        def ensure_scroll_to_end():
            scroll_bar = self.answer_scroll.verticalScrollBar()
            scroll_bar.setValue(scroll_bar.maximum())
        
        # Connect signals
        self.answer_scroll.verticalScrollBar().rangeChanged.connect(ensure_scroll_to_end)
        
        # Install event filter to handle viewport resize
        self.answer_scroll.viewport().installEventFilter(self)
            
        # Connect the scrollbar's range changed signal to ensure we scroll to bottom
        
        self.answer_scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: rgba(255, 255, 255, 0.1);
                width: 6px;
                border-radius: 3px;
                margin: 2px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.3);
                border-radius: 3px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(255, 255, 255, 0.5);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        answer_header.addWidget(a_prefix)
        # Give the answer scroll area stretch so it takes remaining horizontal space
        answer_header.addWidget(self.answer_scroll, 1)
        answer_section.addLayout(answer_header)
        
        qa_layout.addLayout(question_section)
        qa_layout.addLayout(answer_section)

        control_layout = QVBoxLayout()
        control_layout.setSpacing(10)
        
        # === FIX STARTS HERE ===
        # Use stretchable spacers to center the widgets vertically.
        # This is more robust for size calculations than setAlignment.
        control_layout.addStretch()

        self.status_icon_label = QLabel("🎙️")
        self.status_icon_label.setFont(QFont("Segoe UI Emoji", 32))
        self.status_icon_label.setAlignment(Qt.AlignCenter)
        
        self.process_button = QPushButton("🤖 Get Answer")
        self.process_button.setCursor(Qt.PointingHandCursor)
        self.process_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white; border: none;
                border-radius: 10px; padding: 12px 18px;
                font-family: 'Segoe UI'; font-size: 11pt; font-weight: bold;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            QPushButton:hover { 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #7c8ce8, stop:1 #8a5fb0);
                transform: translateY(-1px);
            }
            QPushButton:pressed { 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5a6fd8, stop:1 #6b4394);
            }
        """)
        self.process_button_default_text = self.process_button.text()
        self.process_button.clicked.connect(self.on_process_click)

        self.capture_button = QPushButton("📸 Capture Screen")
        self.capture_button.setCursor(Qt.PointingHandCursor)
        self.capture_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #56ab2f, stop:1 #a8e6cf);
                color: white; border: none;
                border-radius: 10px; padding: 12px 18px;
                font-family: 'Segoe UI'; font-size: 11pt; font-weight: bold;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            QPushButton:hover { 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #6bc23f, stop:1 #b8f0d7);
                transform: translateY(-1px);
            }
            QPushButton:pressed { 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4b9a27, stop:1 #98dcc7);
            }
        """)
        self.capture_button.clicked.connect(self.on_capture_click)

        self.stop_button = QPushButton("⏹️ Stop")
        self.stop_button.setCursor(Qt.PointingHandCursor)
        self.stop_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff6b6b, stop:1 #ee5a52);
                color: white; border: none;
                border-radius: 10px; padding: 12px 18px;
                font-family: 'Segoe UI'; font-size: 11pt; font-weight: bold;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            QPushButton:hover { 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff5252, stop:1 #e53935);
                transform: translateY(-1px);
            }
            QPushButton:pressed { 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e53935, stop:1 #d32f2f);
            }
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
        separator.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 0.2), stop:1 rgba(255, 255, 255, 0.1));
                border: none;
                width: 2px;
                margin: 10px 5px;
            }
        """)

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
            self.answer_label.setText("Capturing screen...")
            self.capture_button.setEnabled(False)
            self.capture_button.setText("⏳ Capturing...")
            QApplication.processEvents()  # Update UI immediately
            try:
                self.capture_callback()
            except Exception as e:
                self.answer_label.setText(f"❌ Capture failed: {str(e)}")
                self.status_icon_label.setText("❌")
            finally:
                self.capture_button.setEnabled(True)
                self.capture_button.setText("📸 Capture Screen")

    def on_process_click(self):
        if self.process_callback:
            self.status_icon_label.setText("🤔")
            self.answer_label.setText("...")
            # Disable button and change text to indicate processing
            self.process_button.setEnabled(False)
            self.process_button.setText("🤔 Thinking...")
            self.process_button.setCursor(Qt.ForbiddenCursor)
            # Force UI to update before calling the callback
            QApplication.processEvents()
            # Call the callback (should be threaded to avoid blocking)
            self.process_callback()

    def on_stop_click(self):
        if self.stop_callback:
            self.stop_callback()

    def _create_labeled_layout(self, prefix_text, label_widget):
        layout = QHBoxLayout()
        prefix_label = QLabel(prefix_text)
        prefix_label.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #667eea, stop:1 #764ba2);
            color: white;
            font-family: 'Segoe UI';
            font-size: 13pt;
            font-weight: 700;
            border-radius: 8px;
            padding: 8px 12px;
            margin-right: 10px;
        """)
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
    def eventFilter(self, obj, event):
        """Handle viewport resize events to update label width"""
        if obj == self.answer_scroll.viewport():
            if event.type() == event.Resize:
                if self.answer_label:
                    self.answer_label.setFixedWidth(self.answer_scroll.viewport().width())
        return super().eventFilter(obj, event)

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
                # Clean up text by removing excessive whitespace and gaps
                cleaned_text = self.clean_text(text)
                self.question_label.setText(cleaned_text)
                if cleaned_text.startswith("Q:"):
                    self.status_icon_label.setText("❓")
                else:
                    self.status_icon_label.setText("🎙️")
            elif message_type == 'answer':
                # Clean up answer text and handle Q: A: format
                cleaned_text = self.clean_text(text)
                answer_text = cleaned_text
                if cleaned_text.startswith("Q:") and "\n\nA:" in cleaned_text:
                    # Split Q: and A: parts
                    parts = cleaned_text.split("\n\nA:", 1)
                    if len(parts) == 2:
                        question_part = parts[0].replace("Q:", "").strip()
                        answer_part = parts[1].strip()
                        self.question_label.setText(question_part)
                        self.answer_label.setText(answer_part)
                        answer_text = answer_part
                    else:
                        self.answer_label.setText(cleaned_text)
                else:
                    self.answer_label.setText(cleaned_text)
                self.answer_label.setFixedWidth(self.answer_scroll.viewport().width())
                # Check if we're still processing (answer is "...") or if we have a real answer
                if answer_text.strip() == "...":
                    # Still processing - keep button disabled
                    self.status_icon_label.setText("🤔")
                    self.process_button.setEnabled(False)
                    self.process_button.setText("🤔 Thinking...")
                    self.process_button.setCursor(Qt.ForbiddenCursor)
                else:
                    # Answer received - re-enable button and restore original text
                    self.status_icon_label.setText("💡")
                    self.process_button.setEnabled(True)
                    self.process_button.setText(self.process_button_default_text)
                    self.process_button.setCursor(Qt.PointingHandCursor)

            self.resize_to_content()

    def clean_text(self, text):
        """Clean text by removing excessive whitespace and formatting issues"""
        if not text:
            return text
            
        # Remove excessive newlines and spaces
        import re
        # Replace multiple spaces with single space
        text = re.sub(r' +', ' ', text)
        # Replace multiple newlines with double newline
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text

    def resize_to_content(self):
        # Update both question and answer labels' size hints
        self.question_label.adjustSize()
        self.answer_label.adjustSize()
        
        # Calculate required heights
        question_height = self.question_label.sizeHint().height() + 40  # Add some padding
        answer_height = self.answer_label.sizeHint().height() + 40  # Add some padding
        
        # Clamp heights between min and max values
        question_height = max(60, min(question_height, 200))  # Question area: 60-200px
        answer_height = max(60, min(answer_height, 300))      # Answer area: 60-300px
        
        # Set the scroll area heights
        self.question_scroll.setFixedHeight(question_height)
        self.answer_scroll.setFixedHeight(answer_height)
        
        # Update the main window size
        self.layout().invalidate()
        self.layout().activate()
        
        # Calculate total height needed
        suggested_height = self.sizeHint().height()
        target_height = max(self.initial_height, min(suggested_height, self.max_height))
        
        # Apply the new size with animation
        if self.height() != target_height:
            self.animation = QPropertyAnimation(self, b"geometry")
            self.animation.setDuration(200)
            self.animation.setStartValue(self.geometry())
            self.animation.setEndValue(QRect(self.x(), self.y(), self.width(), target_height))
            self.animation.setEasingCurve(QEasingCurve.OutCubic)
            self.animation.start()

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