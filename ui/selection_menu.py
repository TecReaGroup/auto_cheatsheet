"""Apple-style selection menu widget for choosing SVG files"""
from pathlib import Path
import subprocess
import sys
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QListWidget, QListWidgetItem,
                                QLineEdit, QPushButton, QHBoxLayout, QLabel, QTabWidget, QMessageBox)
from PySide6.QtCore import Qt, Signal, QSize, QPoint
from core.settings_manager import SettingsManager
from ui.list_item_widget import ListItemWidget
from ui.icon_manager import IconManager
from ui.settings_dialog import SettingsDialog
from ui.add_cheatsheet_dialog import AddCheatsheetDialog
from ui.delete_confirmation_dialog import DeleteConfirmationDialog


class SelectionMenu(QWidget):
    """Apple-style menu for selecting SVG cheatsheet files"""
    
    svg_selected = Signal(str)
    export_requested = Signal(str)  # filepath to export
    menu_dragged = Signal(QPoint)  # Emitted when menu is dragged, contains delta movement
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = SettingsManager()
        self.svg_dir = Path("./src/svg")
        self.svg_files = []
        self._lists_populated = False
        
        # Dragging state
        self.drag_position = None
        self.is_dragging = False
        self.drag_start_pos = None
        
        self.setup_ui()
        self.apply_theme()
        self.load_svg_files()
    
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
        
        # Title bar with settings and quit buttons
        title_layout = QHBoxLayout()
        title_layout.setSpacing(8)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("Cheatsheets")
        title.setObjectName("title")
        title_layout.addWidget(title)
        
        title_layout.addStretch()
        
        # Settings button on the right (before close button)
        settings_button = QPushButton()
        settings_button.setObjectName("iconButton")
        settings_button.setFixedSize(32, 32)
        settings_button.setIcon(IconManager.get_settings_icon())
        settings_button.setIconSize(QSize(18, 18))
        settings_button.clicked.connect(self.open_settings)
        settings_button.setToolTip("Settings")
        title_layout.addWidget(settings_button, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        
        # Close button on the far right (hides menu only)
        close_button = QPushButton()
        close_button.setObjectName("quitButton")
        close_button.setFixedSize(32, 32)
        close_button.setIcon(IconManager.get_close_icon())
        close_button.setIconSize(QSize(16, 16))
        close_button.clicked.connect(self.close)
        close_button.setToolTip("Close Menu")
        title_layout.addWidget(close_button, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        
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
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        # All files tab
        self.all_list = QListWidget()
        self.all_list.setSpacing(2)
        self.all_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.all_list.setSelectionMode(QListWidget.SelectionMode.NoSelection)
        self.all_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.tabs.addTab(self.all_list, "All")
        
        # Recent files tab
        self.recent_list = QListWidget()
        self.recent_list.setSpacing(2)
        self.recent_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.recent_list.setSelectionMode(QListWidget.SelectionMode.NoSelection)
        self.recent_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.tabs.addTab(self.recent_list, "Recent")
        
        # Favorites tab
        self.favorites_list = QListWidget()
        self.favorites_list.setSpacing(2)
        self.favorites_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.favorites_list.setSelectionMode(QListWidget.SelectionMode.NoSelection)
        self.favorites_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.tabs.addTab(self.favorites_list, "Favorites")
        
        layout.addWidget(self.tabs)
        
        # Add button below tabs
        add_button = QPushButton("+ Add Cheatsheet")
        add_button.setObjectName("addButton")
        add_button.setFixedHeight(44)
        add_button.clicked.connect(self.open_add_dialog)
        add_button.setToolTip("Generate a new cheatsheet using AI")
        layout.addWidget(add_button)
    
    def load_svg_files(self):
        """Load SVG files from directory"""
        self.svg_files.clear()
        
        if not self.svg_dir.exists():
            self.svg_dir.mkdir(parents=True, exist_ok=True)
            return
        
        for svg_file in sorted(self.svg_dir.glob("*.svg")):
            self.svg_files.append(svg_file)
    
    def populate_lists(self):
        """Populate all list widgets with custom widgets"""
        # Disable updates during batch operation
        self.all_list.setUpdatesEnabled(False)
        self.all_list.clear()
        
        # Use full width for list items to prevent horizontal scrolling
        list_width = self.all_list.viewport().width()
        fixed_size = QSize(list_width, 48)
        
        for svg_file in self.svg_files:
            display_name = self.format_display_name(svg_file.stem)
            filepath = str(svg_file)
            is_favorite = self.settings.is_favorite(filepath)
            
            widget = ListItemWidget(filepath, display_name, is_favorite)
            widget.open_clicked.connect(self.select_svg)
            widget.favorite_clicked.connect(self.toggle_favorite_by_path)
            widget.export_clicked.connect(lambda fp=filepath: self.handle_export(fp))
            widget.edit_clicked.connect(self.edit_yaml)
            widget.delete_clicked.connect(self.delete_cheatsheet)
            
            item = QListWidgetItem(self.all_list)
            item.setSizeHint(fixed_size)
            self.all_list.addItem(item)
            self.all_list.setItemWidget(item, widget)
        
        # Re-enable updates and refresh
        self.all_list.setUpdatesEnabled(True)
        
        self.populate_recent()
        self.populate_favorites()
    
    def populate_recent(self):
        """Populate recent files list with custom widgets"""
        self.recent_list.setUpdatesEnabled(False)
        self.recent_list.clear()
        recent_files = self.settings.get_recent_files()
        
        # Use same width as all_list to ensure consistency
        list_width = self.all_list.viewport().width()
        fixed_size = QSize(list_width, 48)
        
        for filepath in recent_files:
            path = Path(filepath)
            if path.exists():
                display_name = self.format_display_name(path.stem)
                is_favorite = self.settings.is_favorite(filepath)
                
                widget = ListItemWidget(filepath, display_name, is_favorite)
                widget.open_clicked.connect(self.select_svg)
                widget.favorite_clicked.connect(self.toggle_favorite_by_path)
                widget.export_clicked.connect(lambda fp=filepath: self.handle_export(fp))
                widget.edit_clicked.connect(self.edit_yaml)
                widget.delete_clicked.connect(self.delete_cheatsheet)
                
                item = QListWidgetItem(self.recent_list)
                item.setSizeHint(fixed_size)
                self.recent_list.addItem(item)
                self.recent_list.setItemWidget(item, widget)
        
        self.recent_list.setUpdatesEnabled(True)
    
    def populate_favorites(self):
        """Populate favorites list with custom widgets"""
        self.favorites_list.setUpdatesEnabled(False)
        self.favorites_list.clear()
        favorites = self.settings.get_favorites()
        
        # Use same width as all_list to ensure consistency
        list_width = self.all_list.viewport().width()
        fixed_size = QSize(list_width, 48)
        
        for filepath in favorites:
            path = Path(filepath)
            if path.exists():
                display_name = self.format_display_name(path.stem)
                
                widget = ListItemWidget(filepath, display_name, True)
                widget.open_clicked.connect(self.select_svg)
                widget.favorite_clicked.connect(self.toggle_favorite_by_path)
                widget.export_clicked.connect(lambda fp=filepath: self.handle_export(fp))
                widget.edit_clicked.connect(self.edit_yaml)
                widget.delete_clicked.connect(self.delete_cheatsheet)
                
                item = QListWidgetItem(self.favorites_list)
                item.setSizeHint(fixed_size)
                self.favorites_list.addItem(item)
                self.favorites_list.setItemWidget(item, widget)
        
        self.favorites_list.setUpdatesEnabled(True)
    
    def format_display_name(self, filename):
        """Format filename for display"""
        return filename.replace("_cheatsheet", "").replace("_", " ")
    
    def on_tab_changed(self, index):
        """Re-apply search filter when tab changes"""
        self.filter_list(self.search_input.text())
    
    def filter_list(self, text):
        """Filter the currently active tab's list based on search text"""
        text = text.lower()
        
        # Get the currently active list widget
        current_list = self.tabs.currentWidget()
        if not current_list:
            return
        
        for i in range(current_list.count()):
            item = current_list.item(i)
            widget = current_list.itemWidget(item)
            if widget:
                # Get the display name from the widget's label
                display_name = widget.name_label.text().lower()
                item.setHidden(text not in display_name)
    
    def showEvent(self, event):
        """Populate lists asynchronously after menu is shown"""
        super().showEvent(event)
        if not self._lists_populated:
            self._lists_populated = True
            # Populate lists in next event loop iteration to avoid blocking show()
            from PySide6.QtCore import QTimer
            QTimer.singleShot(0, self.populate_lists)
    
    def toggle_favorite_by_path(self, filepath):
        """Toggle favorite status by filepath"""
        if self.settings.is_favorite(filepath):
            self.settings.remove_favorite(filepath)
        else:
            self.settings.add_favorite(filepath)
        
        # Refresh all lists to update UI
        if self._lists_populated:
            # Save current search text before refreshing
            current_search = self.search_input.text()
            self.populate_lists()
            # Re-apply search filter after refreshing lists
            if current_search:
                self.filter_list(current_search)
    
    def handle_export(self, filepath):
        """Handle export request"""
        self.export_requested.emit(filepath)
    
    def edit_yaml(self, filepath):
        """Open corresponding YAML file in configured or system default editor"""
        svg_path = Path(filepath)
        yaml_path = Path("./src/doc") / f"{svg_path.stem}.yaml"
        
        if not yaml_path.exists():
            QMessageBox.warning(self, "File Not Found",
                              f"YAML file not found:\n{yaml_path}")
            return
        
        try:
            # Check for user-configured editor
            custom_editor = self.settings.get_yaml_editor()
            
            if custom_editor:
                # Use custom editor
                subprocess.Popen([custom_editor, str(yaml_path)])
            else:
                # Use system default
                if sys.platform == "win32":
                    import os
                    os.startfile(str(yaml_path))
                elif sys.platform == "darwin":
                    subprocess.Popen(["open", str(yaml_path)])
                else:
                    subprocess.Popen(["xdg-open", str(yaml_path)])
        except Exception as e:
            QMessageBox.critical(self, "Error",
                               f"Failed to open YAML file:\n{str(e)}")
        
        # Regenerate SVG after edit
        self.regenerate_svg_after_delay()
    
    def regenerate_svg_after_delay(self):
        """Regenerate SVGs after a short delay to allow file saves"""
        from PySide6.QtCore import QTimer
        QTimer.singleShot(2000, self.regenerate_svgs)
    
    def regenerate_svgs(self):
        """Regenerate all SVGs using main.py"""
        try:
            from main import scan_and_generate
            scan_and_generate(to_png=False)
            # Refresh lists after regeneration
            self.refresh_lists()
        except Exception as e:
            print(f"Error regenerating SVGs: {e}")
    
    def delete_cheatsheet(self, filepath):
        """Delete cheatsheet YAML and SVG files with confirmation"""
        svg_path = Path(filepath)
        yaml_path = Path("./src/doc") / f"{svg_path.stem}.yaml"
        
        # Show custom confirmation dialog
        dialog = DeleteConfirmationDialog(self.format_display_name(svg_path.stem), self)
        
        if dialog.exec():
            try:
                # Delete YAML file
                if yaml_path.exists():
                    yaml_path.unlink()
                
                # Delete SVG file
                if svg_path.exists():
                    svg_path.unlink()
                
                # Remove from favorites and recent
                self.settings.remove_favorite(filepath)
                recent_files = self.settings.get_recent_files()
                if filepath in recent_files:
                    recent_files.remove(filepath)
                    self.settings.settings.setValue("recent_files", recent_files)
                
                # Refresh lists
                self.refresh_lists()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete files:\n{str(e)}")
    
    def open_settings(self):
        """Open settings dialog"""
        dialog = SettingsDialog(self)
        dialog.exec()
    
    def open_add_dialog(self):
        """Open add cheatsheet dialog"""
        dialog = AddCheatsheetDialog(self)
        dialog.cheatsheet_added.connect(self.on_cheatsheet_added)
        dialog.exec()
    
    def on_cheatsheet_added(self, filepath):
        """Handle new cheatsheet added"""
        self.refresh_lists()
    
    def refresh_lists(self):
        """Refresh all lists to show new/updated cheatsheets"""
        # Reload files
        self.load_svg_files()
        # Repopulate lists
        if self._lists_populated:
            current_search = self.search_input.text()
            self.populate_lists()
            if current_search:
                self.filter_list(current_search)
    
    def select_svg(self, filepath):
        """Emit selected SVG and add to recent"""
        self.settings.add_recent_file(filepath)
        # Refresh recent list to show updated order
        if self._lists_populated:
            self.populate_recent()
        self.svg_selected.emit(filepath)
    
    def mousePressEvent(self, event):
        """Handle mouse press for dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Only allow dragging from title bar area (top ~50px)
            if event.position().y() < 60:
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                self.drag_start_pos = event.globalPosition().toPoint()
                self.is_dragging = False
                event.accept()
                return
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging"""
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position is not None:
            from PySide6.QtGui import QGuiApplication
            
            current_pos = event.globalPosition().toPoint()
            
            # Start dragging if moved more than 5 pixels
            if not self.is_dragging:
                move_distance = (current_pos - self.drag_start_pos).manhattanLength()
                if move_distance > 5:
                    self.is_dragging = True
            
            if self.is_dragging:
                # Calculate desired new position
                desired_pos = current_pos - self.drag_position
                old_pos = self.pos()
                delta = desired_pos - old_pos
                
                # Check if the orb (parent) can move by this delta
                if self.parent():
                    orb_new_pos = self.parent().pos() + delta
                    screen = QGuiApplication.primaryScreen().geometry()
                    half_width = self.parent().width() // 2
                    half_height = self.parent().height() // 2
                    
                    # Calculate constrained orb position
                    orb_x = orb_new_pos.x()
                    orb_y = orb_new_pos.y()
                    
                    if orb_x < screen.left() - half_width:
                        orb_x = screen.left() - half_width
                    elif orb_x + self.parent().width() > screen.right() + half_width:
                        orb_x = screen.right() + half_width - self.parent().width()
                    
                    if orb_y < screen.top() - half_height:
                        orb_y = screen.top() - half_height
                    elif orb_y + self.parent().height() > screen.bottom() + half_height:
                        orb_y = screen.bottom() + half_height - self.parent().height()
                    
                    # Calculate actual delta the orb can move
                    constrained_orb_pos = QPoint(orb_x, orb_y)
                    actual_orb_delta = constrained_orb_pos - self.parent().pos()
                    
                    # Only move menu by the amount orb can actually move
                    constrained_menu_pos = old_pos + actual_orb_delta
                else:
                    # No parent, use simple screen constraint
                    screen = QGuiApplication.primaryScreen().geometry()
                    x = desired_pos.x()
                    y = desired_pos.y()
                    
                    if x < screen.left():
                        x = screen.left()
                    if x + self.width() > screen.right():
                        x = screen.right() - self.width()
                    if y < screen.top():
                        y = screen.top()
                    if y + self.height() > screen.bottom():
                        y = screen.bottom() - self.height()
                    
                    constrained_menu_pos = QPoint(x, y)
                
                # Only move if position actually changed
                if constrained_menu_pos != old_pos:
                    self.move(constrained_menu_pos)
                    
                    # Calculate actual delta and emit signal for orb to follow
                    actual_delta = constrained_menu_pos - old_pos
                    self.menu_dragged.emit(actual_delta)
                
                event.accept()
                return
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = None
            self.is_dragging = False
            self.drag_start_pos = None
            event.accept()
            return
        super().mouseReleaseEvent(event)
    
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
                    padding: 6px;
                }
                QPushButton#iconButton:hover {
                    background-color: rgba(58, 58, 60, 0.5);
                }
                QPushButton#addButton {
                    padding: 12px 20px;
                    border: none;
                    border-radius: 10px;
                    background-color: rgba(52, 199, 89, 0.15);
                    color: #30d158;
                    font-size: 15px;
                    font-weight: 500;
                    font-family: -apple-system, 'SF Pro Text', 'Segoe UI', sans-serif;
                }
                QPushButton#addButton:hover {
                    background-color: rgba(52, 199, 89, 0.25);
                }
                QPushButton#addButton:pressed {
                    background-color: rgba(52, 199, 89, 0.35);
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
                    padding: 6px;
                }
                QPushButton#iconButton:hover {
                    background-color: rgba(229, 229, 234, 0.6);
                }
                QPushButton#addButton {
                    padding: 12px 20px;
                    border: none;
                    border-radius: 10px;
                    background-color: rgba(52, 199, 89, 0.15);
                    color: #34c759;
                    font-size: 15px;
                    font-weight: 500;
                    font-family: -apple-system, 'SF Pro Text', 'Segoe UI', sans-serif;
                }
                QPushButton#addButton:hover {
                    background-color: rgba(52, 199, 89, 0.25);
                }
                QPushButton#addButton:pressed {
                    background-color: rgba(52, 199, 89, 0.35);
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