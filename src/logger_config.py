# logger_config.py
import logging
import os
from datetime import datetime
import pytz  # Make sure this is installed

def setup_logging():
    try:
        if not os.path.exists('logs'):
            os.makedirs('logs')

        # Use try/except for timezone conversion
        try:
            central_tz = pytz.timezone('America/Chicago')
            timestamp = datetime.now(central_tz).strftime('%Y%m%d_%H%M%S')
        except (ImportError, AttributeError, pytz.exceptions.UnknownTimeZoneError):
            # Fallback to UTC if there's any timezone issue
            print("Warning: Timezone conversion issue. Falling back to default timezone.")
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        log_file = f'logs/process_{timestamp}.log'

        # Create a test file to verify write permissions
        try:
            with open(log_file, 'w') as f:
                f.write('Initializing log file\n')
        except Exception as e:
            print(f"Error creating log file: {e}")
            # Fallback to a more accessible location if needed
            log_file = f'process_{timestamp}.log'
            with open(log_file, 'w') as f:
                f.write('Initializing log file (fallback location)\n')

        # File handler - gets everything
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))

        # Console handler - only warnings and errors
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(logging.Formatter('%(message)s'))

        # Root logger setup - clear any existing handlers first
        logger = logging.getLogger()
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        logger.setLevel(logging.INFO)
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        # Test log messages
        logger.info("Logging initialized successfully")

        print(f"Log file created at: {os.path.abspath(log_file)}")
        return log_file

    except Exception as e:
        print(f"Error setting up logging: {e}")
        # Set up basic console logging as a fallback
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
        return None
