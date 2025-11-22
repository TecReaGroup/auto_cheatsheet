"""Custom list item widget with inline buttons"""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QMenu
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QPen


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
        icon_label.setPixmap(self.create_file_icon().pixmap(QSize(20, 20)))
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
        self.favorite_btn.setIcon(self.create_favorite_icon())
        self.favorite_btn.setIconSize(QSize(20, 20))
        self.favorite_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.favorite_btn.clicked.connect(lambda: self.favorite_clicked.emit(self.filepath))
        self.favorite_btn.setObjectName("iconButton")
        layout.addWidget(self.favorite_btn, 0, Qt.AlignmentFlag.AlignVCenter)
        
        # Expand menu button
        self.expand_btn = QPushButton()
        self.expand_btn.setFixedSize(32, 32)
        self.expand_btn.setIcon(self.create_expand_icon())
        self.expand_btn.setIconSize(QSize(20, 20))
        self.expand_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.expand_btn.clicked.connect(self.show_context_menu)
        self.expand_btn.setObjectName("iconButton")
        layout.addWidget(self.expand_btn, 0, Qt.AlignmentFlag.AlignVCenter)
    
    def create_file_icon(self):
        """Create file icon"""
        pixmap = QPixmap(20, 20)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        if self.is_favorite:
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
    
    def create_favorite_icon(self):
        """Create favorite star icon"""
        pixmap = QPixmap(20, 20)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        from PySide6.QtGui import QPolygonF
        from PySide6.QtCore import QPointF
        import math
        
        # Create star polygon
        center_x, center_y = 10, 10
        outer_radius = 8
        inner_radius = 3.5
        points = []
        
        for i in range(10):
            angle = math.pi / 2 + (i * math.pi / 5)  # Start from top
            radius = outer_radius if i % 2 == 0 else inner_radius
            x = center_x + radius * math.cos(angle)
            y = center_y - radius * math.sin(angle)
            points.append(QPointF(x, y))
        
        star_polygon = QPolygonF(points)
        
        if self.is_favorite:
            # Filled star
            color = QColor(255, 204, 0)
            painter.setBrush(color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawPolygon(star_polygon)
        else:
            # Outlined star
            color = QColor(200, 200, 200)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(color, 1.5))
            painter.drawPolygon(star_polygon)
        
        painter.end()
        return QIcon(pixmap)
    
    def create_expand_icon(self):
        """Create expand menu icon (three dots)"""
        pixmap = QPixmap(20, 20)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        color = QColor(142, 142, 147)
        painter.setBrush(color)
        painter.setPen(Qt.PenStyle.NoPen)
        
        # Draw three dots with more spacing
        for i in range(3):
            y = 3 + i * 6
            painter.drawEllipse(7, y, 5, 5)
        
        painter.end()
        return QIcon(pixmap)
    
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
        self.favorite_btn.setIcon(self.create_favorite_icon())