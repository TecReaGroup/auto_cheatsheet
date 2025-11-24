"""PySide6 Cheatsheet Viewer Application - Main Entry Point"""
import sys
from PySide6.QtWidgets import QApplication
from ui.floating_orb import FloatingOrb
from ui.svg_viewer import SVGViewerWindow
from core.settings_manager import SettingsManager
import signal

# Gracefully handle SIGINT (Ctrl+C) to quit the application
def quit_app():
    QApplication.quit()
signal.signal(signal.SIGINT, lambda sig, frame: QApplication.quit())

class CheatsheetApp(QApplication):
    """Main application class"""
    
    def __init__(self, argv):
        super().__init__(argv)
        self.setApplicationName("Cheatsheet Viewer")
        self.setOrganizationName("CheatsheetApp")
        
        # Initialize settings
        self.settings = SettingsManager()
        
        # Initialize windows
        self.orb = FloatingOrb()
        self.viewer = None
        
        # Connect signals
        self.orb.svg_selected.connect(self.open_svg_viewer)
        self.orb.menu_created.connect(self.connect_menu_signals)
        
        # Show floating orb
        self.orb.show()
    
    def connect_menu_signals(self):
        """Connect menu signals when menu is created"""
        if self.orb.selection_menu:
            self.orb.selection_menu.export_requested.connect(self.handle_export_request)
    
    def open_svg_viewer(self, svg_path):
        """Open SVG viewer with selected file"""
        if self.viewer:
            self.viewer.close()
        
        self.viewer = SVGViewerWindow(svg_path, self.settings)
        self.viewer.viewer_closed.connect(self.on_viewer_closed)
        self.viewer.show()
    
    def handle_export_request(self, filepath):
        """Handle export request - export without opening viewer"""
        # Create a hidden viewer just for export
        if not self.viewer:
            self.viewer = SVGViewerWindow(filepath, self.settings)
        
        # Export without showing the viewer
        self.viewer.export_png_by_path(filepath)
        
        # Clean up the hidden viewer
        if not self.viewer.isVisible():
            self.viewer.deleteLater()
            self.viewer = None
    
    def on_viewer_closed(self):
        """Handle viewer close - show selection menu"""
        # Show menu if not already visible
        if not (self.orb.selection_menu and self.orb.selection_menu.isVisible()):
            self.orb.toggle_selection_menu()


def main():
    """Application entry point"""
    app = CheatsheetApp(sys.argv)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()