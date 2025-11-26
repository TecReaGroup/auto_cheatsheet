"""PySide6 Cheatsheet Viewer Application - Main Entry Point"""
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from ui.floating_orb import FloatingOrb
from ui.svg_viewer import SVGViewerWindow
from core.settings_manager import SettingsManager
from core.logger import logger
import signal
import traceback

# Gracefully handle SIGINT (Ctrl+C) to quit the application
signal.signal(signal.SIGINT, signal.SIG_DFL)

class CheatsheetApp(QApplication):
    """Main application class"""
    
    def __init__(self, argv):
        super().__init__(argv)
        self.setApplicationName("Cheatsheet Viewer")
        self.setOrganizationName("CheatsheetApp")
        
        # Initialize settings
        self.settings = SettingsManager()
        
        # Generate SVGs on startup
        self.generate_svgs_on_startup()
        
        # Initialize windows
        self.orb = FloatingOrb()
        self.viewer = None
        
        # Connect signals
        self.orb.svg_selected.connect(self.open_svg_viewer)
        self.orb.menu_created.connect(self.connect_menu_signals)
        
        # Show floating orb
        self.orb.show()
        
        # Setup timer to allow Python signal handlers to run
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: None)
        self.timer.start(100)
    
    def generate_svgs_on_startup(self):
        """Generate SVGs on application startup"""
        try:
            logger.info("Generating SVGs on startup...")
            from main import scan_and_generate
            scan_and_generate(to_png=False)
            logger.info("SVG generation completed")
        except Exception as e:
            logger.error(f"Error generating SVGs on startup: {e}")
            logger.error(traceback.format_exc())
    
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
    try:
        logger.info("="*60)
        logger.info("Starting Cheatsheet Viewer Application")
        logger.info("="*60)
        app = CheatsheetApp(sys.argv)
        logger.info("Application initialized successfully")
        sys.exit(app.exec())
    except Exception as e:
        logger.error("="*60)
        logger.error("FATAL ERROR: Application failed to start")
        logger.error("="*60)
        logger.error(f"Error: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()