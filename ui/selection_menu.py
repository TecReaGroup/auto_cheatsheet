"""Apple-style selection menu widget for choosing SVG files"""
from pathlib import Path
import subprocess
import sys
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QListWidget, QListWidgetItem,
                                QLineEdit, QPushButton, QHBoxLayout, QLabel, QTabWidget, QApplication, QMessageBox)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QPen
from core.settings_manager import SettingsManager
from ui.list_item_widget import ListItemWidget


class SelectionMenu(QWidget):
    """Apple-style menu for selecting SVG cheatsheet files"""
    
    svg_selected = Signal(str)
    export_requested = Signal(str)  # filepath to export
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = SettingsManager()
        self.svg_dir = Path("./src/svg")
        self.svg_files = []
        
        self.setup_ui()
        self.load_svg_files()
        self.apply_theme()
    
    def setup_ui(self):
        """Setup UI elements"""
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(420, 550)
        
        # Main container
        container = QWidget()
        container.setObjectName("container")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.addWidget(container)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        container_layout.addLayout(layout)
        
        # Title bar with quit button
        title_layout = QHBoxLayout()
        title_layout.setSpacing(0)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("Cheatsheets")
        title.setObjectName("title")
        title_layout.addWidget(title)
        
        title_layout.addStretch()
        
        quit_button = QPushButton()
        quit_button.setObjectName("quitButton")
        quit_button.setFixedSize(32, 32)
        quit_button.setIcon(self.create_close_icon())
        quit_button.setIconSize(QSize(14, 14))
        quit_button.clicked.connect(self.quit_app)
        quit_button.setToolTip("Quit Application")
        title_layout.addWidget(quit_button, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        
        layout.addLayout(title_layout)
        
        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search...")
        self.search_input.setObjectName("search")
        self.search_input.textChanged.connect(self.filter_list)
        layout.addWidget(self.search_input)
        
        # Tabs for different categories
        self.tabs = QTabWidget()
        self.tabs.setObjectName("tabs")
        
        # All files tab
        self.all_list = QListWidget()
        self.all_list.setSpacing(2)
        self.tabs.addTab(self.all_list, "All")
        
        # Recent files tab
        self.recent_list = QListWidget()
        self.recent_list.setSpacing(2)
        self.tabs.addTab(self.recent_list, "Recent")
        
        # Favorites tab
        self.favorites_list = QListWidget()
        self.favorites_list.setSpacing(2)
        self.tabs.addTab(self.favorites_list, "Favorites")
        
        layout.addWidget(self.tabs)
    
    def load_svg_files(self):
        """Load SVG files from directory"""
        self.svg_files.clear()
        
        if not self.svg_dir.exists():
            self.svg_dir.mkdir(parents=True, exist_ok=True)
            return
        
        for svg_file in sorted(self.svg_dir.glob("*.svg")):
            self.svg_files.append(svg_file)
        
        self.populate_lists()
    
    def populate_lists(self):
        """Populate all list widgets with custom widgets"""
        self.all_list.clear()
        
        for svg_file in self.svg_files:
            display_name = self.format_display_name(svg_file.stem)
            filepath = str(svg_file)
            is_favorite = self.settings.is_favorite(filepath)
            
            # Create custom widget
            widget = ListItemWidget(filepath, display_name, is_favorite)
            widget.open_clicked.connect(self.select_svg)
            widget.favorite_clicked.connect(self.toggle_favorite_by_path)
            widget.export_clicked.connect(self.export_requested.emit)
            widget.edit_clicked.connect(self.edit_yaml)
            
            # Add to list
            item = QListWidgetItem(self.all_list)
            item.setSizeHint(QSize(widget.sizeHint().width(), 48))
            self.all_list.addItem(item)
            self.all_list.setItemWidget(item, widget)
        
        self.populate_recent()
        self.populate_favorites()
    
    def populate_recent(self):
        """Populate recent files list with custom widgets"""
        self.recent_list.clear()
        recent_files = self.settings.get_recent_files()
        
        for filepath in recent_files:
            path = Path(filepath)
            if path.exists():
                display_name = self.format_display_name(path.stem)
                is_favorite = self.settings.is_favorite(filepath)
                
                widget = ListItemWidget(filepath, display_name, is_favorite)
                widget.open_clicked.connect(self.select_svg)
                widget.favorite_clicked.connect(self.toggle_favorite_by_path)
                widget.export_clicked.connect(self.export_requested.emit)
                widget.edit_clicked.connect(self.edit_yaml)
                
                item = QListWidgetItem(self.recent_list)
                item.setSizeHint(QSize(widget.sizeHint().width(), 48))
                self.recent_list.addItem(item)
                self.recent_list.setItemWidget(item, widget)
    
    def populate_favorites(self):
        """Populate favorites list with custom widgets"""
        self.favorites_list.clear()
        favorites = self.settings.get_favorites()
        
        for filepath in favorites:
            path = Path(filepath)
            if path.exists():
                display_name = self.format_display_name(path.stem)
                
                widget = ListItemWidget(filepath, display_name, True)
                widget.open_clicked.connect(self.select_svg)
                widget.favorite_clicked.connect(self.toggle_favorite_by_path)
                widget.export_clicked.connect(self.export_requested.emit)
                widget.edit_clicked.connect(self.edit_yaml)
                
                item = QListWidgetItem(self.favorites_list)
                item.setSizeHint(QSize(widget.sizeHint().width(), 48))
                self.favorites_list.addItem(item)
                self.favorites_list.setItemWidget(item, widget)
    
    def create_svg_icon(self, is_favorite=False):
        """Create an icon for SVG items"""
        pixmap = QPixmap(20, 20)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        if is_favorite:
            color = QColor(255, 204, 0)  # Gold
        else:
            color = QColor(0, 122, 255)  # Apple blue
        
        painter.setBrush(color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(3, 2, 14, 16, 2, 2)
        
        painter.setPen(QColor(255, 255, 255))
        for i in range(2):
            y = 7 + i * 5
            painter.drawLine(6, y, 14, y)
        
        painter.end()
        return QIcon(pixmap)
    
    def create_close_icon(self):
        """Create a close (X) icon"""
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        pen = QPen(QColor(142, 142, 147), 1.5)  # #8e8e93
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        
        # Draw X
        painter.drawLine(4, 4, 12, 12)
        painter.drawLine(12, 4, 4, 12)
        
        painter.end()
        return QIcon(pixmap)
    
    def format_display_name(self, filename):
        """Format filename for display"""
        name = filename.replace("_cheatsheet", "").replace("_", " ")
        return name.title()
    
    def filter_list(self, text):
        """Filter the all files list based on search text"""
        text = text.lower()
        for i in range(self.all_list.count()):
            item = self.all_list.item(i)
            item.setHidden(text not in item.text().lower())
    
    def toggle_favorite_by_path(self, filepath):
        """Toggle favorite status by filepath"""
        if self.settings.is_favorite(filepath):
            self.settings.remove_favorite(filepath)
        else:
            self.settings.add_favorite(filepath)
        
        # Refresh all lists to update UI
        self.populate_lists()
    
    def edit_yaml(self, filepath):
        """Open corresponding YAML file in default editor"""
        svg_path = Path(filepath)
        # Assuming YAML files are in src/doc with same stem
        yaml_path = Path("./src/doc") / f"{svg_path.stem}.yaml"
        
        if not yaml_path.exists():
            QMessageBox.warning(self, "File Not Found",
                              f"YAML file not found:\n{yaml_path}")
            return
        
        try:
            if sys.platform == "win32":
                subprocess.Popen(["notepad.exe", str(yaml_path)])
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(yaml_path)])
            else:
                subprocess.Popen(["xdg-open", str(yaml_path)])
        except Exception as e:
            QMessageBox.critical(self, "Error",
                               f"Failed to open YAML file:\n{str(e)}")
    
    def select_svg(self, filepath):
        """Emit selected SVG and add to recent"""
        self.settings.add_recent_file(filepath)
        self.svg_selected.emit(filepath)
    
    def quit_app(self):
        """Quit the entire application"""
        QApplication.quit()
    
    def apply_theme(self):
        """Apply Apple-style minimalist theme"""
        theme = self.settings.get_theme()
        
        if theme == "dark":
            self.setStyleSheet("""
                #container {
                    background-color: rgba(28, 28, 30, 0.95);
                    border-radius: 16px;
                }
                #title {
                    color: #ffffff;
                    font-size: 22px;
                    font-weight: 600;
                    font-family: -apple-system, 'SF Pro Display', 'Segoe UI', sans-serif;
                    padding: 4px 0px;
                }
                QPushButton#quitButton {
                    background-color: transparent;
                    border: none;
                    border-radius: 6px;
                    padding: 0px;
                    margin: 0px;
                }
                QPushButton#quitButton:hover {
                    background-color: rgba(255, 59, 48, 0.15);
                }
                QPushButton#quitButton:pressed {
                    background-color: rgba(255, 59, 48, 0.25);
                }
                QLineEdit#search {
                    padding: 10px 14px;
                    border: none;
                    border-radius: 10px;
                    background-color: rgba(44, 44, 46, 0.8);
                    color: #ffffff;
                    font-size: 15px;
                    font-family: -apple-system, 'SF Pro Text', 'Segoe UI', sans-serif;
                }
                QLineEdit#search:focus {
                    background-color: rgba(58, 58, 60, 0.9);
                }
                QTabWidget#tabs::pane {
                    border: none;
                    background-color: transparent;
                }
                QTabBar::tab {
                    padding: 10px 18px;
                    background-color: transparent;
                    color: #8e8e93;
                    border: none;
                    border-radius: 8px;
                    margin-right: 4px;
                    font-size: 15px;
                    font-family: -apple-system, 'SF Pro Text', 'Segoe UI', sans-serif;
                }
                QTabBar::tab:selected {
                    background-color: rgba(58, 58, 60, 0.6);
                    color: #ffffff;
                }
                QTabBar::tab:hover:!selected {
                    background-color: rgba(44, 44, 46, 0.5);
                    color: #ffffff;
                }
                QListWidget {
                    border: none;
                    background-color: transparent;
                    color: #ffffff;
                    font-size: 15px;
                    font-family: -apple-system, 'SF Pro Text', 'Segoe UI', sans-serif;
                    outline: none;
                }
                QListWidget::item {
                    padding: 0px;
                    border-radius: 8px;
                    margin: 0px;
                    outline: none;
                    background-color: transparent;
                }
                QPushButton#iconButton {
                    background-color: transparent;
                    border: none;
                    border-radius: 6px;
                }
                QPushButton#iconButton:hover {
                    background-color: rgba(58, 58, 60, 0.5);
                }
                QListWidget::item:focus {
                    outline: none;
                }
                QListWidget::item:hover {
                    background-color: rgba(58, 58, 60, 0.5);
                }
                QListWidget::item:selected {
                    background-color: transparent;
                }
                QPushButton#primaryButton {
                    padding: 11px 20px;
                    border: none;
                    border-radius: 10px;
                    background-color: #007aff;
                    color: white;
                    font-size: 15px;
                    font-weight: 500;
                    font-family: -apple-system, 'SF Pro Text', 'Segoe UI', sans-serif;
                }
                QPushButton#primaryButton:hover {
                    background-color: #0a84ff;
                }
                QPushButton#primaryButton:pressed {
                    background-color: #0051d5;
                }
                QPushButton#primaryButton:disabled {
                    background-color: rgba(58, 58, 60, 0.5);
                    color: #636366;
                }
                QPushButton#secondaryButton {
                    padding: 11px;
                    border: none;
                    border-radius: 10px;
                    background-color: rgba(58, 58, 60, 0.6);
                    color: #ffffff;
                    font-size: 18px;
                    font-family: -apple-system, 'SF Pro Text', 'Segoe UI', sans-serif;
                }
                QPushButton#secondaryButton:hover {
                    background-color: rgba(68, 68, 70, 0.7);
                }
                QPushButton#secondaryButton:pressed {
                    background-color: rgba(48, 48, 50, 0.8);
                }
                QPushButton#secondaryButton:disabled {
                    background-color: rgba(58, 58, 60, 0.3);
                    color: #636366;
                }
            """)
        else:
            self.setStyleSheet("""
                #container {
                    background-color: rgba(255, 255, 255, 0.95);
                    border-radius: 16px;
                }
                #title {
                    color: #000000;
                    font-size: 22px;
                    font-weight: 600;
                    font-family: -apple-system, 'SF Pro Display', 'Segoe UI', sans-serif;
                    padding: 4px 0px;
                }
                QPushButton#quitButton {
                    background-color: transparent;
                    border: none;
                    border-radius: 6px;
                    padding: 0px;
                    margin: 0px;
                }
                QPushButton#quitButton:hover {
                    background-color: rgba(255, 59, 48, 0.15);
                }
                QPushButton#quitButton:pressed {
                    background-color: rgba(255, 59, 48, 0.25);
                }
                QLineEdit#search {
                    padding: 10px 14px;
                    border: none;
                    border-radius: 10px;
                    background-color: rgba(242, 242, 247, 0.8);
                    color: #000000;
                    font-size: 15px;
                    font-family: -apple-system, 'SF Pro Text', 'Segoe UI', sans-serif;
                }
                QLineEdit#search:focus {
                    background-color: rgba(229, 229, 234, 0.9);
                }
                QTabWidget#tabs::pane {
                    border: none;
                    background-color: transparent;
                }
                QTabBar::tab {
                    padding: 10px 18px;
                    background-color: transparent;
                    color: #8e8e93;
                    border: none;
                    border-radius: 8px;
                    margin-right: 4px;
                    font-size: 15px;
                    font-family: -apple-system, 'SF Pro Text', 'Segoe UI', sans-serif;
                }
                QTabBar::tab:selected {
                    background-color: rgba(229, 229, 234, 0.6);
                    color: #000000;
                }
                QTabBar::tab:hover:!selected {
                    background-color: rgba(242, 242, 247, 0.5);
                    color: #000000;
                }
                QListWidget {
                    border: none;
                    background-color: transparent;
                    color: #000000;
                    font-size: 15px;
                    font-family: -apple-system, 'SF Pro Text', 'Segoe UI', sans-serif;
                    outline: none;
                }
                QListWidget::item {
                    padding: 0px;
                    border-radius: 8px;
                    margin: 0px;
                    outline: none;
                    background-color: transparent;
                }
                QPushButton#iconButton {
                    background-color: transparent;
                    border: none;
                    border-radius: 6px;
                }
                QPushButton#iconButton:hover {
                    background-color: rgba(229, 229, 234, 0.6);
                }
                QListWidget::item:focus {
                    outline: none;
                }
                QListWidget::item:hover {
                    background-color: rgba(242, 242, 247, 0.7);
                }
                QListWidget::item:selected {
                    background-color: transparent;
                }
                QPushButton#primaryButton {
                    padding: 11px 20px;
                    border: none;
                    border-radius: 10px;
                    background-color: #007aff;
                    color: white;
                    font-size: 15px;
                    font-weight: 500;
                    font-family: -apple-system, 'SF Pro Text', 'Segoe UI', sans-serif;
                }
                QPushButton#primaryButton:hover {
                    background-color: #0a84ff;
                }
                QPushButton#primaryButton:pressed {
                    background-color: #0051d5;
                }
                QPushButton#primaryButton:disabled {
                    background-color: rgba(229, 229, 234, 0.5);
                    color: #8e8e93;
                }
                QPushButton#secondaryButton {
                    padding: 11px;
                    border: none;
                    border-radius: 10px;
                    background-color: rgba(229, 229, 234, 0.6);
                    color: #000000;
                    font-size: 18px;
                    font-family: -apple-system, 'SF Pro Text', 'Segoe UI', sans-serif;
                }
                QPushButton#secondaryButton:hover {
                    background-color: rgba(209, 209, 214, 0.7);
                }
                QPushButton#secondaryButton:pressed {
                    background-color: rgba(199, 199, 204, 0.8);
                }
                QPushButton#secondaryButton:disabled {
                    background-color: rgba(229, 229, 234, 0.3);
                    color: #8e8e93;
                }
            """)