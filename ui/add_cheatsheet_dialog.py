"""Dialog for adding new cheatsheet via LLM"""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                                QLineEdit, QPushButton, QTextEdit, QProgressBar,
                                QMessageBox)
from PySide6.QtCore import Qt, Signal, QThread
from core.settings_manager import SettingsManager
from script.llm_generator import LLMGenerator
from pathlib import Path


class GeneratorThread(QThread):
    """Thread for running LLM generation"""
    
    finished = Signal(bool, str, str)  # success, content, error
    
    def __init__(self, generator, command_name):
        super().__init__()
        self.generator = generator
        self.command_name = command_name
    
    def run(self):
        """Run the generation"""
        success, content, error = self.generator.generate_cheatsheet(self.command_name)
        self.finished.emit(success, content, error)


class AddCheatsheetDialog(QDialog):
    """Dialog for adding new cheatsheet"""
    
    cheatsheet_added = Signal(str)  # filepath
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = SettingsManager()
        self.generator_thread = None
        self.generated_content = ""
        self.setup_ui()
        self.apply_theme()
    
    def setup_ui(self):
        """Setup UI elements"""
        self.setWindowTitle("Add Cheatsheet")
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowStaysOnTopHint)
        self.setModal(True)
        self.setFixedSize(600, 500)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("Generate New Cheatsheet")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)
        
        # Command input
        input_label = QLabel("Command/Tool Name:")
        input_label.setObjectName("fieldLabel")
        layout.addWidget(input_label)
        
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("e.g., kubectl, terraform, ffmpeg...")
        self.command_input.setObjectName("commandInput")
        self.command_input.returnPressed.connect(self.generate_cheatsheet)
        layout.addWidget(self.command_input)
        
        # Preview area
        preview_label = QLabel("Preview:")
        preview_label.setObjectName("fieldLabel")
        layout.addWidget(preview_label)
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setPlaceholderText("Generated YAML will appear here...")
        self.preview_text.setObjectName("previewText")
        layout.addWidget(self.preview_text, 1)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("progressBar")
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setWordWrap(True)
        self.status_label.hide()
        layout.addWidget(self.status_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("secondaryButton")
        self.cancel_btn.setFixedHeight(40)
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        self.generate_btn = QPushButton("Generate")
        self.generate_btn.setObjectName("primaryButton")
        self.generate_btn.setFixedHeight(40)
        self.generate_btn.clicked.connect(self.generate_cheatsheet)
        button_layout.addWidget(self.generate_btn)
        
        self.save_btn = QPushButton("Save")
        self.save_btn.setObjectName("primaryButton")
        self.save_btn.setFixedHeight(40)
        self.save_btn.clicked.connect(self.save_and_process)
        self.save_btn.hide()
        button_layout.addWidget(self.save_btn)
        
        layout.addLayout(button_layout)
        
        # Focus on input
        self.command_input.setFocus()
    
    def generate_cheatsheet(self):
        """Generate cheatsheet using LLM"""
        command_name = self.command_input.text().strip()
        
        if not command_name:
            self.show_status("Please enter a command/tool name", error=True)
            return
        
        # Check API key
        api_key = self.settings.get_llm_api_key()
        if not api_key:
            reply = QMessageBox.question(
                self,
                "API Key Not Set",
                "LLM API key is not configured. Would you like to open settings?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.open_settings()
            return
        
        # Disable inputs
        self.command_input.setEnabled(False)
        self.generate_btn.setEnabled(False)
        self.save_btn.hide()
        
        # Show progress
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.progress_bar.show()
        self.show_status("Generating cheatsheet...", error=False)
        
        # Create generator
        generator = LLMGenerator(
            api_url=self.settings.get_llm_api_url(),
            api_key=api_key,
            model=self.settings.get_llm_model()
        )
        
        # Run generation in thread
        self.generator_thread = GeneratorThread(generator, command_name)
        self.generator_thread.finished.connect(self.on_generation_finished)
        self.generator_thread.start()
    
    def on_generation_finished(self, success, content, error):
        """Handle generation completion"""
        # Re-enable inputs
        self.command_input.setEnabled(True)
        self.generate_btn.setEnabled(True)
        self.progress_bar.hide()
        
        if success:
            self.generated_content = content
            self.preview_text.setPlainText(content)
            self.show_status("✓ Generated successfully! Review and click Save.", error=False)
            self.save_btn.show()
            self.generate_btn.hide()
        else:
            self.show_status(f"✗ Error: {error}", error=True)
            self.preview_text.clear()
            self.generated_content = ""
    
    def save_and_process(self):
        """Save YAML and process it"""
        if not self.generated_content:
            return
        
        command_name = self.command_input.text().strip()
        
        # Create generator to save file
        generator = LLMGenerator(
            api_url=self.settings.get_llm_api_url(),
            api_key=self.settings.get_llm_api_key(),
            model=self.settings.get_llm_model()
        )
        
        success, filepath, error = generator.save_to_file(self.generated_content, command_name)
        
        if not success:
            QMessageBox.warning(self, "Save Error", error)
            return
        
        # Show progress for SVG generation
        self.save_btn.setEnabled(False)
        self.progress_bar.setRange(0, 0)
        self.progress_bar.show()
        self.show_status("Generating SVG...", error=False)
        
        # Process with main.py
        try:
            from main import scan_and_generate
            scan_and_generate(to_png=False)
            
            self.show_status("✓ Cheatsheet created successfully!", error=False)
            self.progress_bar.hide()
            
            # Emit signal with SVG path
            svg_path = Path("./src/svg") / f"{filepath.stem}.svg"
            self.cheatsheet_added.emit(str(svg_path))
            
            # Close dialog after brief delay
            from PySide6.QtCore import QTimer
            QTimer.singleShot(1000, self.accept)
            
        except Exception as e:
            self.progress_bar.hide()
            self.show_status(f"✗ Error generating SVG: {str(e)}", error=True)
            self.save_btn.setEnabled(True)
    
    def open_settings(self):
        """Open settings dialog"""
        from ui.settings_dialog import SettingsDialog
        dialog = SettingsDialog(self)
        dialog.exec()
    
    def show_status(self, message, error=False):
        """Show status message"""
        self.status_label.setText(message)
        self.status_label.setProperty("error", error)
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)
        self.status_label.show()
    
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
                }
                QLabel#fieldLabel {
                    color: #ffffff;
                    font-size: 14px;
                    font-weight: 500;
                    font-family: -apple-system, 'SF Pro Text', 'Segoe UI', sans-serif;
                }
                QLabel#statusLabel {
                    color: #34c759;
                    font-size: 13px;
                    font-family: -apple-system, 'SF Pro Text', 'Segoe UI', sans-serif;
                }
                QLabel#statusLabel[error="true"] {
                    color: #ff453a;
                }
                QLineEdit#commandInput {
                    padding: 10px 12px;
                    border: 1px solid rgba(58, 58, 60, 0.8);
                    border-radius: 8px;
                    background-color: rgba(44, 44, 46, 0.6);
                    color: #ffffff;
                    font-size: 15px;
                    font-family: -apple-system, 'SF Pro Text', 'Segoe UI', sans-serif;
                }
                QLineEdit#commandInput:focus {
                    border: 1px solid #007aff;
                    background-color: rgba(58, 58, 60, 0.7);
                }
                QTextEdit#previewText {
                    border: 1px solid rgba(58, 58, 60, 0.8);
                    border-radius: 8px;
                    background-color: rgba(44, 44, 46, 0.6);
                    color: #ffffff;
                    font-size: 13px;
                    font-family: 'Consolas', 'Monaco', monospace;
                    padding: 10px;
                }
                QProgressBar#progressBar {
                    border: none;
                    border-radius: 2px;
                    background-color: rgba(58, 58, 60, 0.6);
                }
                QProgressBar#progressBar::chunk {
                    background-color: #007aff;
                    border-radius: 2px;
                }
                QPushButton#primaryButton {
                    padding: 11px 24px;
                    border: none;
                    border-radius: 10px;
                    background-color: #007aff;
                    color: white;
                    font-size: 15px;
                    font-weight: 500;
                    font-family: -apple-system, 'SF Pro Text', 'Segoe UI', sans-serif;
                    min-width: 100px;
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
                }
                QLabel#fieldLabel {
                    color: #000000;
                    font-size: 14px;
                    font-weight: 500;
                    font-family: -apple-system, 'SF Pro Text', 'Segoe UI', sans-serif;
                }
                QLabel#statusLabel {
                    color: #34c759;
                    font-size: 13px;
                    font-family: -apple-system, 'SF Pro Text', 'Segoe UI', sans-serif;
                }
                QLabel#statusLabel[error="true"] {
                    color: #ff3b30;
                }
                QLineEdit#commandInput {
                    padding: 10px 12px;
                    border: 1px solid rgba(209, 209, 214, 0.8);
                    border-radius: 8px;
                    background-color: rgba(242, 242, 247, 0.6);
                    color: #000000;
                    font-size: 15px;
                    font-family: -apple-system, 'SF Pro Text', 'Segoe UI', sans-serif;
                }
                QLineEdit#commandInput:focus {
                    border: 1px solid #007aff;
                    background-color: rgba(229, 229, 234, 0.7);
                }
                QTextEdit#previewText {
                    border: 1px solid rgba(209, 209, 214, 0.8);
                    border-radius: 8px;
                    background-color: rgba(242, 242, 247, 0.6);
                    color: #000000;
                    font-size: 13px;
                    font-family: 'Consolas', 'Monaco', monospace;
                    padding: 10px;
                }
                QProgressBar#progressBar {
                    border: none;
                    border-radius: 2px;
                    background-color: rgba(229, 229, 234, 0.6);
                }
                QProgressBar#progressBar::chunk {
                    background-color: #007aff;
                    border-radius: 2px;
                }
                QPushButton#primaryButton {
                    padding: 11px 24px;
                    border: none;
                    border-radius: 10px;
                    background-color: #007aff;
                    color: white;
                    font-size: 15px;
                    font-weight: 500;
                    font-family: -apple-system, 'SF Pro Text', 'Segoe UI', sans-serif;
                    min-width: 100px;
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