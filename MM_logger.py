import logging
import os.path


def initialize_logger(log_filename=None):
    # Create a logger object
    logger = logging.getLogger(__name__)

    # Set the log level
    logger.setLevel(logging.DEBUG)
    log_file_folder = os.getcwd()+"/ARTAK_MM/LOGS/"
    if not os.path.isdir(log_file_folder):
        os.mkdir(log_file_folder)
    log_filename = os.path.join(log_file_folder, str(log_filename) + ".txt")
    # Create a file handler
    handler = logging.FileHandler(log_filename)

    # Set the log message format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # Add the file handler to the logger
    logger.addHandler(handler)

    return logger
