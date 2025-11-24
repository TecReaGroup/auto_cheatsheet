"""Settings manager for persisting application state"""
from PySide6.QtCore import QSettings


class SettingsManager:
    """Manages application settings and persistence"""
    
    def __init__(self):
        self.settings = QSettings("CheatsheetApp", "CheatsheetViewer")
    
    # Orb position
    def save_orb_position(self, x, y):
        """Save floating orb position"""
        self.settings.setValue("orb/x", x)
        self.settings.setValue("orb/y", y)
    
    def get_orb_position(self):
        """Get saved orb position or default"""
        x = self.settings.value("orb/x", 100, type=int)
        y = self.settings.value("orb/y", 100, type=int)
        return x, y
    
    # Window geometry
    def save_window_geometry(self, geometry):
        """Save window geometry"""
        self.settings.setValue("window/geometry", geometry)
    
    def get_window_geometry(self):
        """Get saved window geometry"""
        return self.settings.value("window/geometry")
    
    # Theme
    def save_theme(self, theme):
        """Save theme preference (light/dark)"""
        self.settings.setValue("appearance/theme", theme)
    
    def get_theme(self):
        """Get theme preference"""
        return self.settings.value("appearance/theme", "dark", type=str)
    
    # Recent files
    def save_recent_files(self, files):
        """Save recent files list"""
        self.settings.setValue("recent/files", files)
    
    def get_recent_files(self):
        """Get recent files list"""
        return self.settings.value("recent/files", [], type=list)
    
    def add_recent_file(self, filepath, max_recent=10):
        """Add file to recent files list"""
        recent = self.get_recent_files()
        
        # Remove if already exists
        if filepath in recent:
            recent.remove(filepath)
        
        # Add to front
        recent.insert(0, filepath)
        
        # Limit size
        recent = recent[:max_recent]
        
        self.save_recent_files(recent)
    
    # Favorites
    def save_favorites(self, favorites):
        """Save favorite files list"""
        self.settings.setValue("favorites/files", favorites)
    
    def get_favorites(self):
        """Get favorite files list"""
        return self.settings.value("favorites/files", [], type=list)
    
    def add_favorite(self, filepath):
        """Add file to favorites"""
        favorites = self.get_favorites()
        if filepath not in favorites:
            favorites.append(filepath)
            self.save_favorites(favorites)
    
    def remove_favorite(self, filepath):
        """Remove file from favorites"""
        favorites = self.get_favorites()
        if filepath in favorites:
            favorites.remove(filepath)
            self.save_favorites(favorites)
    
    def is_favorite(self, filepath):
        """Check if file is in favorites"""
        return filepath in self.get_favorites()
    
    # Zoom level
    def save_zoom_level(self, zoom):
        """Save zoom level"""
        self.settings.setValue("viewer/zoom", zoom)
    
    def get_zoom_level(self):
        """Get saved zoom level"""
        return self.settings.value("viewer/zoom", 1.0, type=float)
    
    # YAML Editor
    def save_yaml_editor(self, editor_path):
        """Save YAML editor path"""
        self.settings.setValue("editor/yaml", editor_path)
    
    def get_yaml_editor(self):
        """Get YAML editor path"""
        return self.settings.value("editor/yaml", "", type=str)