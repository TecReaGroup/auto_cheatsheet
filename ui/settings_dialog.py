"""Settings dialog for LLM API configuration"""
import sys
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                                QLineEdit, QPushButton, QFormLayout, QWidget)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPalette, QColor
from core.settings_manager import SettingsManager
from ui.icon_manager import IconManager

# Windows dark title bar support
if sys.platform == 'win32':
    try:
        import ctypes
        from ctypes import windll, c_int, byref
        DWMWA_USE_IMMERSIVE_DARK_MODE = 20
        DWMWA_CAPTION_COLOR = 35
    except ImportError:
        DWMWA_USE_IMMERSIVE_DARK_MODE = None
        DWMWA_CAPTION_COLOR = None


class SettingsDialog(QDialog):
    """Dialog for configuring LLM API settings"""
    
    settings_saved = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = SettingsManager()
        self._dark_titlebar_applied = False
        self.setup_ui()
        self.load_settings()
        self.apply_theme()
    
    def setup_ui(self):
        """Setup UI elements"""
        self.setWindowTitle("Settings")
        self.setWindowIcon(IconManager.get_settings_icon())
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowStaysOnTopHint)
        self.setModal(True)
        self.setFixedWidth(500)
        
        # Force dark palette
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.ColorRole.Window, QColor(28, 28, 30))
        dark_palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        self.setPalette(dark_palette)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("LLM API Settings")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)
        
        # Form layout for settings
        form_widget = QWidget()
        form_widget.setObjectName("formWidget")
        form_layout = QFormLayout(form_widget)
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(0, 0, 0, 0)
        
        # API URL
        self.api_url_input = QLineEdit()
        self.api_url_input.setPlaceholderText("https://api.openai.com/v1")
        self.api_url_input.setObjectName("settingsInput")
        form_layout.addRow("API URL:", self.api_url_input)
        
        # API Key
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("sk-...")
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setObjectName("settingsInput")
        form_layout.addRow("API Key:", self.api_key_input)
        
        # Model
        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("gpt-4")
        self.model_input.setObjectName("settingsInput")
        form_layout.addRow("Model:", self.model_input)
        
        layout.addWidget(form_widget)
        
        # Info text
        info = QLabel("Configure your OpenAI-compatible API settings.\nThe API key will be stored securely.")
        info.setObjectName("infoText")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondaryButton")
        cancel_btn.setFixedHeight(40)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save")
        save_btn.setObjectName("primaryButton")
        save_btn.setFixedHeight(40)
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
    
    def load_settings(self):
        """Load current settings"""
        self.api_url_input.setText(self.settings.get_llm_api_url())
        self.api_key_input.setText(self.settings.get_llm_api_key())
        self.model_input.setText(self.settings.get_llm_model())
    
    def save_settings(self):
        """Save settings and close"""
        api_url = self.api_url_input.text().strip()
        api_key = self.api_key_input.text().strip()
        model = self.model_input.text().strip()
        
        # Use defaults if empty
        if not api_url:
            api_url = "https://api.openai.com/v1"
        if not model:
            model = "gpt-4"
        
        self.settings.save_llm_api_url(api_url)
        self.settings.save_llm_api_key(api_key)
        self.settings.save_llm_model(model)
        
        self.settings_saved.emit()
        self.accept()
    
    def showEvent(self, event):
        """Override show event to apply dark titlebar before window appears"""
        super().showEvent(event)
        if not self._dark_titlebar_applied:
            self._dark_titlebar_applied = True
            self.apply_windows_dark_titlebar()
    
    def apply_windows_dark_titlebar(self):
        """Apply dark title bar on Windows"""
        if sys.platform == 'win32' and DWMWA_USE_IMMERSIVE_DARK_MODE is not None:
            try:
                hwnd = int(self.winId())
                value = c_int(1)
                windll.dwmapi.DwmSetWindowAttribute(
                    hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE,
                    byref(value), ctypes.sizeof(value)
                )
                color = c_int(0x1e1c1c)
                windll.dwmapi.DwmSetWindowAttribute(
                    hwnd, DWMWA_CAPTION_COLOR,
                    byref(color), ctypes.sizeof(color)
                )
            except Exception:
                pass
    
    def apply_theme(self):
        """Apply theme styling"""
        theme = self.settings.get_theme()
        
        if theme == "dark":
            self.setStyleSheet("""
                QDialog {
                    background-color: rgba(28, 28, 30, 0.98);
                    border-radius: 12px;
                }
                QLabel#dialogTitle {
                    color: #ffffff;
                    font-size: 20px;
                    font-weight: 600;
                    font-family: -apple-system, 'SF Pro Display', 'Segoe UI', sans-serif;
                    padding-bottom: 10px;
                }
                QLabel#infoText {
                    color: #8e8e93;
                    font-size: 13px;
                    font-family: -apple-system, 'SF Pro Text', 'Segoe UI', sans-serif;
                    line-height: 1.4;
                }
                QLabel {
                    color: #ffffff;
                    font-size: 14px;
                    font-family: -apple-system, 'SF Pro Text', 'Segoe UI', sans-serif;
                }
                QLineEdit#settingsInput {
                    padding: 10px 12px;
                    border: 1px solid rgba(58, 58, 60, 0.8);
                    border-radius: 8px;
                    background-color: rgba(44, 44, 46, 0.6);
                    color: #ffffff;
                    font-size: 14px;
                    font-family: -apple-system, 'SF Pro Text', 'Segoe UI', sans-serif;
                    min-width: 300px;
                }
                QLineEdit#settingsInput:focus {
                    border: 1px solid #007aff;
                    background-color: rgba(58, 58, 60, 0.7);
                }
                QPushButton#primaryButton {
                    padding: 11px 24px;
                    border: none;
                    border-radius: 10px;
                    background-color: #007aff;
                    color: white;
                    font-size: 15px;
                    font-weight: 500;
                    font-family: -apple-system, 'SF Pro Text', 'Segoe UI', sans-serif;
                    min-width: 100px;
                }
                QPushButton#primaryButton:hover {
                    background-color: #0a84ff;
                }
                QPushButton#primaryButton:pressed {
                    background-color: #0051d5;
                }
                QPushButton#secondaryButton {
                    padding: 11px 24px;
                    border: none;
                    border-radius: 10px;
                    background-color: rgba(58, 58, 60, 0.6);
                    color: #ffffff;
                    font-size: 15px;
                    font-weight: 500;
                    font-family: -apple-system, 'SF Pro Text', 'Segoe UI', sans-serif;
                    min-width: 100px;
                }
                QPushButton#secondaryButton:hover {
                    background-color: rgba(68, 68, 70, 0.7);
                }
                QPushButton#secondaryButton:pressed {
                    background-color: rgba(48, 48, 50, 0.8);
                }
            """)
        else:
            self.setStyleSheet("""
                QDialog {
                    background-color: rgba(255, 255, 255, 0.98);
                    border-radius: 12px;
                }
                QLabel#dialogTitle {
                    color: #000000;
                    font-size: 20px;
                    font-weight: 600;
                    font-family: -apple-system, 'SF Pro Display', 'Segoe UI', sans-serif;
                    padding-bottom: 10px;
                }
                QLabel#infoText {
                    color: #8e8e93;
                    font-size: 13px;
                    font-family: -apple-system, 'SF Pro Text', 'Segoe UI', sans-serif;
                    line-height: 1.4;
                }
                QLabel {
                    color: #000000;
                    font-size: 14px;
                    font-family: -apple-system, 'SF Pro Text', 'Segoe UI', sans-serif;
                }
                QLineEdit#settingsInput {
                    padding: 10px 12px;
                    border: 1px solid rgba(209, 209, 214, 0.8);
                    border-radius: 8px;
                    background-color: rgba(242, 242, 247, 0.6);
                    color: #000000;
                    font-size: 14px;
                    font-family: -apple-system, 'SF Pro Text', 'Segoe UI', sans-serif;
                    min-width: 300px;
                }
                QLineEdit#settingsInput:focus {
                    border: 1px solid #007aff;
                    background-color: rgba(229, 229, 234, 0.7);
                }
                QPushButton#primaryButton {
                    padding: 11px 24px;
                    border: none;
                    border-radius: 10px;
                    background-color: #007aff;
                    color: white;
                    font-size: 15px;
                    font-weight: 500;
                    font-family: -apple-system, 'SF Pro Text', 'Segoe UI', sans-serif;
                    min-width: 100px;
                }
                QPushButton#primaryButton:hover {
                    background-color: #0a84ff;
                }
                QPushButton#primaryButton:pressed {
                    background-color: #0051d5;
                }
                QPushButton#secondaryButton {
                    padding: 11px 24px;
                    border: none;
                    border-radius: 10px;
                    background-color: rgba(229, 229, 234, 0.6);
                    color: #000000;
                    font-size: 15px;
                    font-weight: 500;
                    font-family: -apple-system, 'SF Pro Text', 'Segoe UI', sans-serif;
                    min-width: 100px;
                }
                QPushButton#secondaryButton:hover {
                    background-color: rgba(209, 209, 214, 0.7);
                }
                QPushButton#secondaryButton:pressed {
                    background-color: rgba(199, 199, 204, 0.8);
                }
            """)