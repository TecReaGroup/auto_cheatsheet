"""Floating orb widget - Main entry point"""
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QPoint, Signal, QPropertyAnimation, QEasingCurve, Property, QRect
from PySide6.QtGui import QPainter, QColor
from ui.selection_menu import SelectionMenu
from ui.icon_manager import IconManager
from core.settings_manager import SettingsManager


class FloatingOrb(QWidget):
    """Draggable floating orb widget"""
    
    svg_selected = Signal(str)
    menu_created = Signal()  # Emitted when selection menu is created
    
    def __init__(self):
        super().__init__()
        self.settings = SettingsManager()
        self.drag_position = QPoint()
        self.press_position = QPoint()
        self.is_dragging = False
        self.selection_menu = None
        self._hover = False
        self._scale = 1.0
        self._menu_drag_in_progress = False
        
        self.setup_ui()
        self.load_position()
    
    def setup_ui(self):
        """Setup UI elements"""
        # Frameless window
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(80, 80)
        
        # Enable mouse tracking for hover effects
        self.setMouseTracking(True)
    
    def load_position(self):
        """Load saved position"""
        x, y = self.settings.get_orb_position()
        self.move(x, y)
    
    def save_position(self):
        """Save current position"""
        pos = self.pos()
        self.settings.save_orb_position(pos.x(), pos.y())
    
    def paintEvent(self, event):
        """Custom paint event for orb - Apple minimalist style"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Calculate scaled size
        size = int(60 * self._scale)
        offset = (80 - size) // 2
        
        # Apple-style subtle shadow
        shadow_offset = 2
        shadow_color = QColor(0, 0, 0, 30)
        painter.setBrush(shadow_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(offset + shadow_offset, offset + shadow_offset, size, size)
        
        # Main orb with flat design
        if self._hover:
            orb_color = QColor(10, 132, 255)  # Apple blue hover
        else:
            orb_color = QColor(0, 122, 255)  # Apple blue
        
        painter.setBrush(orb_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(offset, offset, size, size)
        
        # Draw document icon using QtAwesome
        icon = IconManager.get_orb_document_icon(color=IconManager.WHITE)
        icon_size = int(size // 2.2)
        icon_rect = QRect(
            40 - icon_size // 2,
            40 - icon_size // 2,
            icon_size,
            icon_size
        )
        icon.paint(painter, icon_rect)
    
    def enterEvent(self, event):
        """Mouse enter event"""
        self._hover = True
        self.animate_scale(1.1)
        self.update()
    
    def leaveEvent(self, event):
        """Mouse leave event"""
        self._hover = False
        self.animate_scale(1.0)
        self.update()
    
    def animate_scale(self, target_scale):
        """Animate scale change"""
        animation = QPropertyAnimation(self, b"scale")
        animation.setDuration(150)
        animation.setStartValue(self._scale)
        animation.setEndValue(target_scale)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.start()
        self._animation = animation  # Keep reference
    
    def get_scale(self):
        return self._scale
    
    def set_scale(self, value):
        self._scale = value
        self.update()
    
    scale = Property(float, get_scale, set_scale)
    
    def mousePressEvent(self, event):
        """Handle mouse press"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.press_position = event.globalPosition().toPoint()
            self.drag_position = self.press_position - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging"""
        if event.buttons() == Qt.MouseButton.LeftButton:
            # Start dragging if moved more than 5 pixels
            if not self.is_dragging:
                move_distance = (event.globalPosition().toPoint() - self.press_position).manhattanLength()
                if move_distance > 5:
                    self.is_dragging = True
            
            if self.is_dragging:
                new_pos = event.globalPosition().toPoint() - self.drag_position
                constrained_pos = self.constrain_to_screen(new_pos)
                self.move(constrained_pos)
                # Update menu position if visible
                if self.selection_menu and self.selection_menu.isVisible():
                    self.update_menu_position()
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        if event.button() == Qt.MouseButton.LeftButton:
            if self.is_dragging:
                self.is_dragging = False
                self.snap_to_edge()
                self.save_position()
            else:
                # Click without drag - toggle menu
                self.toggle_selection_menu()
            event.accept()
    
    def constrain_to_screen(self, pos):
        """Constrain orb position to allow maximum half outside screen"""
        from PySide6.QtGui import QGuiApplication
        
        screen = QGuiApplication.primaryScreen().geometry()
        half_width = self.width() // 2
        half_height = self.height() // 2
        
        x = pos.x()
        y = pos.y()
        
        # Constrain horizontal - allow half to go outside
        if x < screen.left() - half_width:
            x = screen.left() - half_width
        elif x + self.width() > screen.right() + half_width:
            x = screen.right() + half_width - self.width()
        
        # Constrain vertical - allow half to go outside
        if y < screen.top() - half_height:
            y = screen.top() - half_height
        elif y + self.height() > screen.bottom() + half_height:
            y = screen.bottom() + half_height - self.height()
        
        return QPoint(x, y)
    
    def snap_to_edge(self):
        """Snap orb to nearest edge if close enough"""
        from PySide6.QtGui import QGuiApplication
        
        screen = QGuiApplication.primaryScreen().geometry()
        pos = self.pos()
        half_width = self.width() // 2
        half_height = self.height() // 2
        snap_threshold = 15  # Pixels from edge to trigger snap
        
        x = pos.x()
        y = pos.y()
        
        # Check distance to each edge
        dist_left = x - screen.left()
        dist_right = screen.right() - (x + self.width())
        dist_top = y - screen.top()
        dist_bottom = screen.bottom() - (y + self.height())
        
        # Find closest edge
        min_dist = min(dist_left, dist_right, dist_top, dist_bottom)
        
        # Snap to edge if within threshold
        if min_dist < snap_threshold:
            target_pos = QPoint(x, y)
            
            if min_dist == dist_left:
                target_pos.setX(screen.left() - half_width)
            elif min_dist == dist_right:
                target_pos.setX(screen.right() - half_width)
            elif min_dist == dist_top:
                target_pos.setY(screen.top() - half_height)
            elif min_dist == dist_bottom:
                target_pos.setY(screen.bottom() - half_height)
            
            self.animate_to_position(target_pos)
    
    def animate_to_position(self, target_pos):
        """Animate orb movement to target position"""
        animation = QPropertyAnimation(self, b"pos")
        animation.setDuration(300)  # 300ms for smooth snap
        animation.setStartValue(self.pos())
        animation.setEndValue(target_pos)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Update menu position during animation
        def update_menu():
            if self.selection_menu and self.selection_menu.isVisible():
                self.update_menu_position()
        
        animation.valueChanged.connect(update_menu)
        animation.start()
        self._position_animation = animation  # Keep reference
    
    def toggle_selection_menu(self):
        """Toggle SVG selection menu visibility"""
        if self.selection_menu and self.selection_menu.isVisible():
            self.selection_menu.close()
        else:
            if not self.selection_menu:
                self.selection_menu = SelectionMenu(self)
                self.selection_menu.svg_selected.connect(self.on_svg_selected)
                self.selection_menu.menu_dragged.connect(self.on_menu_dragged)
                self.menu_created.emit()  # Notify app that menu was created
            
            self.update_menu_position()
            self.selection_menu.show()
    
    def update_menu_position(self):
        """Update menu position relative to orb with screen boundary checks"""
        if not self.selection_menu:
            return
        
        from PySide6.QtGui import QGuiApplication
        
        screen = QGuiApplication.primaryScreen().geometry()
        orb_pos = self.pos()
        menu_width = self.selection_menu.width()
        menu_height = self.selection_menu.height()
        
        # Try to position menu to the right of orb
        menu_x = orb_pos.x() + self.width()
        menu_y = orb_pos.y()
        
        # Check right boundary
        if menu_x + menu_width > screen.right():
            # Position to the left instead
            menu_x = orb_pos.x() - menu_width
        
        # Check left boundary
        if menu_x < screen.left():
            menu_x = screen.left()
        
        # Check bottom boundary
        if menu_y + menu_height > screen.bottom():
            menu_y = screen.bottom() - menu_height - 5
        
        # Check top boundary
        if menu_y < screen.top():
            menu_y = screen.top() + 5
        
        self.selection_menu.move(menu_x, menu_y)
    
    def on_menu_dragged(self, delta):
        """Handle menu drag - move orb synchronously (menu has already checked boundaries)"""
        # Prevent recursive updates
        if self._menu_drag_in_progress:
            return
        
        self._menu_drag_in_progress = True
        
        try:
            # Menu has already calculated the safe delta, just apply it
            new_orb_pos = self.pos() + delta
            self.move(new_orb_pos)
        finally:
            self._menu_drag_in_progress = False
    
    def on_svg_selected(self, svg_path):
        """Handle SVG selection"""
        self.svg_selected.emit(svg_path)
        if self.selection_menu:
            self.selection_menu.close()