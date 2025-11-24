"""Apple-style SVG viewer window"""
from pathlib import Path
import sys
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QScrollArea, QFileDialog,
                                QMessageBox)
from PySide6.QtCore import Qt, QSize, QTimer, Signal
from PySide6.QtGui import QAction, QKeySequence, QPixmap, QPainter, QColor, QPalette
from PySide6.QtSvgWidgets import QSvgWidget
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


class SVGViewerWindow(QMainWindow):
    """Apple-style SVG viewer window"""
    
    viewer_closed = Signal()
    
    def __init__(self, svg_path, settings):
        super().__init__()
        self.svg_path = Path(svg_path)
        self.settings = settings
        
        self.setup_ui()
        self.create_actions()
        self.create_toolbar()
        self.load_svg()
        self.apply_theme()
        self.restore_geometry()
        
        # Apply Windows dark title bar after window is shown
        QTimer.singleShot(100, self.apply_windows_dark_titlebar)
    
    def setup_ui(self):
        """Setup UI elements"""
        self.setWindowTitle(f"{self.svg_path.stem}")
        self.resize(1000, 800)
        self.set_window_icon()
        
        # Force dark title bar by setting dark palette
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.ColorRole.Window, QColor(28, 28, 30))
        dark_palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(28, 28, 30))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(44, 44, 46))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.Button, QColor(44, 44, 46))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
        dark_palette.setColor(QPalette.ColorRole.Link, QColor(0, 122, 255))
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 122, 255))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        self.setPalette(dark_palette)
        
        # Set window background to dark
        self.setStyleSheet("QMainWindow { background-color: #1c1c1e; }")
        
        central_widget = QWidget()
        central_widget.setStyleSheet("background-color: #1c1c1e;")
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(False)
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.svg_widget = QSvgWidget()
        
        self.scroll_area.setWidget(self.svg_widget)
        layout.addWidget(self.scroll_area)
        
        self.statusBar().showMessage(f"{self.svg_path.name}")
    
    def create_actions(self):
        """Create actions"""
        self.export_action = QAction("Export PNG", self)
        self.export_action.setShortcut(QKeySequence("Ctrl+E"))
        self.export_action.triggered.connect(self.export_png)
        
        self.toggle_theme_action = QAction("Toggle Theme", self)
        self.toggle_theme_action.setShortcut(QKeySequence("Ctrl+T"))
        self.toggle_theme_action.triggered.connect(self.toggle_theme)
        
        self.close_action = QAction("Close", self)
        self.close_action.setShortcut(QKeySequence.StandardKey.Close)
        self.close_action.triggered.connect(self.close)
    
    def create_toolbar(self):
        """Create toolbar"""
        # Toolbar removed - export now in context menu
        pass
    
    def set_window_icon(self):
        """Set window icon using QtAwesome"""
        self.setWindowIcon(IconManager.get_window_icon())
    
    def apply_windows_dark_titlebar(self):
        """Apply dark title bar on Windows 10/11"""
        if sys.platform == 'win32' and DWMWA_USE_IMMERSIVE_DARK_MODE is not None:
            try:
                hwnd = int(self.winId())
                print(f"[DEBUG] Window handle: {hwnd}")
                
                # Try Windows 11 method (build 22000+)
                value = c_int(1)  # 1 = dark mode, 0 = light mode
                result = windll.dwmapi.DwmSetWindowAttribute(
                    hwnd,
                    DWMWA_USE_IMMERSIVE_DARK_MODE,
                    byref(value),
                    ctypes.sizeof(value)
                )
                print(f"[DEBUG] DwmSetWindowAttribute result: {result}")
                
                if result == 0:
                    print("[SUCCESS] Dark title bar applied via Windows API")
                else:
                    print(f"[WARNING] DwmSetWindowAttribute failed with code: {result}")
                
                # Also try setting caption color directly (Windows 11)
                color = c_int(0x1e1c1c)  # BGR format: #1c1c1e
                result2 = windll.dwmapi.DwmSetWindowAttribute(
                    hwnd,
                    DWMWA_CAPTION_COLOR,
                    byref(color),
                    ctypes.sizeof(color)
                )
                print(f"[DEBUG] Caption color result: {result2}")
                
            except Exception as e:
                print(f"[ERROR] Failed to apply Windows dark title bar: {e}")
        else:
            print(f"[INFO] Platform: {sys.platform}, API available: {DWMWA_USE_IMMERSIVE_DARK_MODE is not None}")
    
    def load_svg(self):
        """Load SVG file"""
        if self.svg_path.exists():
            self.svg_widget.load(str(self.svg_path))
            self.settings.add_recent_file(str(self.svg_path))
            QTimer.singleShot(100, self.fit_to_window)
        else:
            QMessageBox.warning(self, "Error", f"SVG file not found: {self.svg_path}")
            QTimer.singleShot(100, self.close)
    
    def fit_to_window(self):
        """Fit SVG to window while maintaining aspect ratio"""
        renderer = self.svg_widget.renderer()
        if not renderer or not renderer.isValid():
            return
        
        default_size = renderer.defaultSize()
        viewport_size = self.scroll_area.viewport().size()
        
        # Calculate scale to fit width while maintaining aspect ratio
        scale = viewport_size.width() / default_size.width()
        
        new_size = QSize(
            int(default_size.width() * scale),
            int(default_size.height() * scale)
        )
        
        self.svg_widget.setFixedSize(new_size)
    
    def resizeEvent(self, event):
        """Handle window resize"""
        super().resizeEvent(event)
        self.fit_to_window()
    
    def export_png(self):
        """Export current view as PNG"""
        self.export_png_by_path(str(self.svg_path))
    
    def export_png_by_path(self, svg_path):
        """Export PNG from any SVG path"""
        path = Path(svg_path)
        default_name = path.stem + ".png"
        default_path = str(Path("./src/image") / default_name)
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export as PNG", default_path, "PNG Images (*.png)"
        )
        
        if file_path:
            try:
                # Load the SVG temporarily
                from PySide6.QtSvgWidgets import QSvgWidget
                temp_widget = QSvgWidget()
                temp_widget.load(str(path))
                
                renderer = temp_widget.renderer()
                if renderer and renderer.isValid():
                    default_size = renderer.defaultSize()
                    export_size = QSize(default_size.width() * 2, default_size.height() * 2)
                    
                    pixmap = QPixmap(export_size)
                    pixmap.fill(Qt.GlobalColor.white)
                    
                    painter = QPainter(pixmap)
                    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
                    renderer.render(painter)
                    painter.end()
                    
                    pixmap.save(file_path, "PNG", 100)
                    
                    QMessageBox.information(self, "Success", f"Exported to:\n{file_path}")
                    if hasattr(self, 'statusBar'):
                        self.statusBar().showMessage(f"Exported: {Path(file_path).name}", 3000)
                else:
                    QMessageBox.warning(self, "Error", "Unable to render SVG")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export:\n{str(e)}")
    
    def toggle_theme(self):
        """Toggle between light and dark theme"""
        current_theme = self.settings.get_theme()
        new_theme = "light" if current_theme == "dark" else "dark"
        self.settings.save_theme(new_theme)
        self.apply_theme()
        self.statusBar().showMessage(f"Theme: {new_theme.title()}", 2000)
    
    def apply_theme(self):
        """Apply Apple-style theme"""
        theme = self.settings.get_theme()
        
        if theme == "dark":
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #1c1c1e;
                }
                QToolBar {
                    background-color: rgba(28, 28, 30, 0.95);
                    border: none;
                    padding: 8px;
                    spacing: 8px;
                }
                QScrollArea {
                    background-color: #1c1c1e;
                    border: none;
                }
                QScrollBar:vertical {
                    background: transparent;
                    width: 10px;
                    margin: 0px;
                }
                QScrollBar::handle:vertical {
                    background: rgba(255, 255, 255, 0.2);
                    border-radius: 5px;
                    min-height: 20px;
                }
                QScrollBar::handle:vertical:hover {
                    background: rgba(255, 255, 255, 0.3);
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px;
                }
                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                    background: none;
                }
                QPushButton#toolButton {
                    background-color: rgba(58, 58, 60, 0.6);
                    color: #ffffff;
                    border: none;
                    border-radius: 8px;
                    font-size: 16px;
                    font-weight: 400;
                }
                QPushButton#toolButton:hover {
                    background-color: rgba(68, 68, 70, 0.7);
                }
                QPushButton#primaryButton {
                    background-color: #007aff;
                    color: white;
                    border: none;
                    padding: 6px 16px;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: 500;
                }
                QPushButton#primaryButton:hover {
                    background-color: #0a84ff;
                }
                QStatusBar {
                    background-color: rgba(28, 28, 30, 0.95);
                    color: #8e8e93;
                    border: none;
                    font-size: 12px;
                }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #f2f2f7;
                }
                QToolBar {
                    background-color: rgba(255, 255, 255, 0.95);
                    border: none;
                    padding: 8px;
                    spacing: 8px;
                }
                QScrollArea {
                    background-color: #ffffff;
                    border: none;
                }
                QPushButton#toolButton {
                    background-color: rgba(229, 229, 234, 0.6);
                    color: #000000;
                    border: none;
                    border-radius: 8px;
                    font-size: 16px;
                    font-weight: 400;
                }
                QPushButton#toolButton:hover {
                    background-color: rgba(209, 209, 214, 0.7);
                }
                QPushButton#primaryButton {
                    background-color: #007aff;
                    color: white;
                    border: none;
                    padding: 6px 16px;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: 500;
                }
                QPushButton#primaryButton:hover {
                    background-color: #0a84ff;
                }
                QStatusBar {
                    background-color: rgba(255, 255, 255, 0.95);
                    color: #8e8e93;
                    border: none;
                    font-size: 12px;
                }
            """)
    
    def restore_geometry(self):
        """Restore saved window geometry"""
        geometry = self.settings.get_window_geometry()
        if geometry:
            self.restoreGeometry(geometry)
    
    def closeEvent(self, event):
        """Handle window close - hide and show menu"""
        self.settings.save_window_geometry(self.saveGeometry())
        self.hide()
        self.viewer_closed.emit()
        event.ignore()
    