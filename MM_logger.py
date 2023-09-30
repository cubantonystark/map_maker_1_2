import logging
import os.path
import tkinter as tk

class TkinterLogHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        log_message = self.format(record)
        self.text_widget.insert(tk.END, log_message + '\n')
        self.text_widget.see(tk.END)  # Scroll to the end of the text widget


def initialize_logger(log_filename=None, log_text_widget=None):
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

    if log_text_widget is not None:
        log_handler = TkinterLogHandler(log_text_widget)
        logger.addHandler(log_handler)

    return logger
