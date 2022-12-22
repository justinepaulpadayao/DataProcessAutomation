import logging
import os
from datetime import datetime


def configure_logging():
    # Create a logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # Create a file handler
    log_dir = 'log_files'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Generate the log file name using the current timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    log_file = f'main_{timestamp}.log'
    log_path = os.path.join(log_dir, log_file)
    file_handler = logging.FileHandler(log_path)

    # Set the log level and format for the file handler
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Add the file handler to the logger
    logger.addHandler(file_handler)

    # Add a console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Try logging a message to test if the logging is configured correctly
    try:
        logger.info('Logging test message')
    except Exception as e:
        logger.exception('Error while logging test message: %s', e)


