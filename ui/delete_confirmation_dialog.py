"""Custom delete confirmation dialog matching settings style"""
import sys
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt
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


class DeleteConfirmationDialog(QDialog):
    """Custom styled delete confirmation dialog"""
    
    def __init__(self, cheatsheet_name, parent=None):
        super().__init__(parent)
        self.settings = SettingsManager()
        self._dark_titlebar_applied = False
        self.setup_ui(cheatsheet_name)
        self.apply_theme()
    
    def setup_ui(self, cheatsheet_name):
        """Setup UI elements"""
        self.setWindowTitle("Delete Cheatsheet")
        self.setWindowIcon(IconManager.get_window_icon())
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowStaysOnTopHint)
        self.setModal(True)
        self.setFixedWidth(400)
        
        # Force dark palette
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.ColorRole.Window, QColor(28, 28, 30))
        dark_palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        self.setPalette(dark_palette)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("Delete Cheatsheet")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)
        
        # Message
        message = QLabel(f"Are you sure you want to delete '{cheatsheet_name}'?\nThis will delete both the YAML and SVG files.\n")
        message.setObjectName("messageText")
        message.setWordWrap(True)
        layout.addWidget(message)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondaryButton")
        cancel_btn.setFixedHeight(40)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        delete_btn = QPushButton("Delete")
        delete_btn.setObjectName("deleteButton")
        delete_btn.setFixedHeight(40)
        delete_btn.clicked.connect(self.accept)
        button_layout.addWidget(delete_btn)
        
        layout.addLayout(button_layout)
    
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
                QLabel#messageText {
                    color: #ffffff;
                    font-size: 14px;
                    font-family: -apple-system, 'SF Pro Text', 'Segoe UI', sans-serif;
                    line-height: 1.5;
                }
                QPushButton#deleteButton {
                    padding: 11px 24px;
                    border: none;
                    border-radius: 10px;
                    background-color: #ff3b30;
                    color: white;
                    font-size: 15px;
                    font-weight: 500;
                    font-family: -apple-system, 'SF Pro Text', 'Segoe UI', sans-serif;
                    min-width: 100px;
                }
                QPushButton#deleteButton:hover {
                    background-color: #ff453a;
                }
                QPushButton#deleteButton:pressed {
                    background-color: #d70015;
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
                QLabel#messageText {
                    color: #000000;
                    font-size: 14px;
                    font-family: -apple-system, 'SF Pro Text', 'Segoe UI', sans-serif;
                    line-height: 1.5;
                }
                QPushButton#deleteButton {
                    padding: 11px 24px;
                    border: none;
                    border-radius: 10px;
                    background-color: #ff3b30;
                    color: white;
                    font-size: 15px;
                    font-weight: 500;
                    font-family: -apple-system, 'SF Pro Text', 'Segoe UI', sans-serif;
                    min-width: 100px;
                }
                QPushButton#deleteButton:hover {
                    background-color: #ff453a;
                }
                QPushButton#deleteButton:pressed {
                    background-color: #d70015;
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