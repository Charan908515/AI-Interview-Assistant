# Missing methods for launcher_ui.py
# Add these methods to your LauncherWindow class

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
