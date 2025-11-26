"""Logging configuration for the application"""
import logging
import sys
from pathlib import Path
from datetime import datetime

def setup_logger():
    """Setup logger to output to both console and file"""
    # Create log directory
    log_dir = Path("./log")
    log_dir.mkdir(exist_ok=True)
    
    # Create log file with timestamp
    log_file = log_dir / f"app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)

# Initialize logger
logger = setup_logger()