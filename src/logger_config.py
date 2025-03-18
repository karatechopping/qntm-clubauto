# logger_config.py
import logging
import os
from datetime import datetime

def setup_logging():
    if not os.path.exists('logs'):
        os.makedirs('logs')

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = f'logs/process_{timestamp}.log'

    # File handler - gets everything
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))

    # Console handler - only warnings and errors
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)  # Only show warnings and errors
    console_handler.setFormatter(logging.Formatter('%(message)s'))

    # Root logger setup
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return log_file
