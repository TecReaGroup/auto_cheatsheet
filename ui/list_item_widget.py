"""Custom list item widget with inline buttons"""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QMenu
from PySide6.QtCore import Qt, Signal, QSize
from ui.icon_manager import IconManager


class ListItemWidget(QWidget):
    """Custom list item with inline favorite and expand buttons"""
    
    open_clicked = Signal(str)  # filepath
    favorite_clicked = Signal(str)  # filepath
    export_clicked = Signal(str)  # filepath
    edit_clicked = Signal(str)  # filepath
    
    def __init__(self, filepath, display_name, is_favorite=False, parent=None):
        super().__init__(parent)
        self.filepath = filepath
        self.is_favorite = is_favorite
        
        # Set widget styling for equal padding
        self.setStyleSheet("""
            QWidget {
                padding: 0px;
                margin: 0px;
            }
        """)
        
        self.setup_ui(display_name)
    
    def setup_ui(self, display_name):
        """Setup UI elements"""
        # Set fixed height for consistent centering
        self.setFixedHeight(48)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(8)
        
        # File icon - fixed size container
        icon_label = QLabel()
        icon_label.setFixedSize(32, 32)
        file_icon = self.get_file_icon()
        icon_label.setPixmap(file_icon.pixmap(QSize(20, 20)))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label, 0, Qt.AlignmentFlag.AlignVCenter)
        
        # File name label (clickable)
        self.name_label = QLabel(display_name)
        self.name_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 15px;
                font-family: -apple-system, 'SF Pro Text', 'Segoe UI', sans-serif;
                padding: 0px;
                margin: 0px;
            }
        """)
        self.name_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.name_label.mousePressEvent = lambda e: self.open_clicked.emit(self.filepath)
        layout.addWidget(self.name_label, 1, Qt.AlignmentFlag.AlignVCenter)
        
        # Favorite button
        self.favorite_btn = QPushButton()
        self.favorite_btn.setFixedSize(32, 32)
        self.favorite_btn.setIcon(self.get_favorite_icon())
        self.favorite_btn.setIconSize(QSize(18, 18))
        self.favorite_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.favorite_btn.clicked.connect(lambda: self.favorite_clicked.emit(self.filepath))
        self.favorite_btn.setObjectName("iconButton")
        layout.addWidget(self.favorite_btn, 0, Qt.AlignmentFlag.AlignVCenter)
        
        # Expand menu button
        self.expand_btn = QPushButton()
        self.expand_btn.setFixedSize(32, 32)
        self.expand_btn.setIcon(IconManager.get_menu_icon())
        self.expand_btn.setIconSize(QSize(18, 18))
        self.expand_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.expand_btn.clicked.connect(self.show_context_menu)
        self.expand_btn.setObjectName("iconButton")
        layout.addWidget(self.expand_btn, 0, Qt.AlignmentFlag.AlignVCenter)
    
    def get_file_icon(self):
        """Get file icon based on favorite status"""
        if self.is_favorite:
            return IconManager.get_document_icon(color=IconManager.APPLE_GOLD)
        else:
            return IconManager.get_document_icon(color=IconManager.APPLE_BLUE)
    
    def get_favorite_icon(self):
        """Get favorite star icon"""
        return IconManager.get_star_icon(filled=self.is_favorite)
    
    def show_context_menu(self):
        """Show context menu with actions"""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: rgba(28, 28, 30, 0.95);
                border: none;
                border-radius: 8px;
                padding: 4px;
            }
            QMenu::item {
                padding: 8px 20px;
                border-radius: 4px;
                color: #ffffff;
            }
            QMenu::item:selected {
                background-color: #007aff;
            }
        """)
        
        # Export PNG action
        export_action = menu.addAction("Export PNG")
        export_action.triggered.connect(lambda: self.export_clicked.emit(self.filepath))
        
        # Edit YAML action
        edit_action = menu.addAction("Edit YAML")
        edit_action.triggered.connect(lambda: self.edit_clicked.emit(self.filepath))
        
        # Show menu at button position
        menu.exec(self.expand_btn.mapToGlobal(self.expand_btn.rect().bottomLeft()))
    
    def set_favorite(self, is_favorite):
        """Update favorite status"""
        self.is_favorite = is_favorite
        self.favorite_btn.setIcon(self.get_favorite_icon())