"""Logging configuration for Auto Cheatsheet"""
import sys
from pathlib import Path
from datetime import datetime

class TeeOutput:
    """Redirect stdout/stderr to both file and console"""
    def __init__(self, file_path, original_stream):
        self.file = open(file_path, 'a', encoding='utf-8')
        self.original = original_stream
        # When running as compiled exe without console, original_stream can be None
        self.has_console = original_stream is not None
    
    def write(self, message):
        if message:  # Only write non-empty messages
            self.file.write(message)
            self.file.flush()
            # Only write to console if it exists
            if self.has_console:
                try:
                    self.original.write(message)
                    self.original.flush()
                except (AttributeError, OSError):
                    # Console might not be available
                    pass
    
    def flush(self):
        self.file.flush()
        if self.has_console:
            try:
                self.original.flush()
            except (AttributeError, OSError):
                pass
    
    def close(self):
        self.file.close()

def get_app_directory():
    """Get the directory where the exe/script is located"""
    if getattr(sys, 'frozen', False):
        # Running as compiled exe
        return Path(sys.executable).parent
    else:
        # Running as script
        return Path.cwd()

def cleanup_old_logs(log_dir, keep_count=10):
    """Keep only the most recent N log files"""
    try:
        # Get all log files sorted by modification time (newest first)
        log_files = sorted(
            log_dir.glob("app_*.log"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        # Remove old log files (keep only the most recent ones)
        for old_log in log_files[keep_count:]:
            try:
                old_log.unlink()
                print(f"Removed old log: {old_log.name}")
            except Exception as e:
                print(f"Could not remove old log {old_log.name}: {e}")
    except Exception as e:
        print(f"Error cleaning up old logs: {e}")

def setup_logger():
    """Redirect all stdout/stderr to log file"""
    try:
        # Get application directory
        app_dir = get_app_directory()
        
        # Create log directory next to exe
        log_dir = app_dir / "log"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Clean up old log files (keep only 10 most recent)
        cleanup_old_logs(log_dir, keep_count=10)
        
        # Create log file with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = log_dir / f"app_{timestamp}.log"
        
        # Write header
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"{'='*60}\n")
            f.write("Auto Cheatsheet - Log Started\n")
            f.write(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"App Directory: {app_dir}\n")
            f.write(f"Log File: {log_file}\n")
            f.write(f"{'='*60}\n\n")
        
        # Redirect stdout and stderr
        sys.stdout = TeeOutput(log_file, sys.stdout)
        sys.stderr = TeeOutput(log_file, sys.stderr)
        
        print(f"Logger initialized: {log_file}")
        
        return log_file
    except Exception as e:
        # Fallback if logger setup fails
        # Try to write error to a fallback log file
        try:
            app_dir = get_app_directory()
            error_log = app_dir / "log" / "error.log"
            error_log.parent.mkdir(parents=True, exist_ok=True)
            with open(error_log, 'a', encoding='utf-8') as f:
                import traceback
                f.write(f"\n{'='*60}\n")
                f.write(f"Logger Setup Failed: {datetime.now()}\n")
                f.write(f"Error: {e}\n")
                f.write(traceback.format_exc())
                f.write(f"{'='*60}\n\n")
        except Exception:
            pass  # Silently fail if we can't even write error log
        return None

# Don't auto-initialize - let app.py call setup_logger() explicitly
log_file = None