import tkinter as tk
from tkinter import scrolledtext
import subprocess
import threading


def run_executable():
    executable_path = "C:/Program Files/Bentley/ContextCapture/bin/CCEngine.exe"

    def read_output():
        process = subprocess.Popen(executable_path, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                   universal_newlines=True)
        while True:
            output = process.stdout.readline()
            if not output:
                break
            output_text.insert(tk.END, output)
        process.wait()

    # Create a separate thread to read the output
    output_thread = threading.Thread(target=read_output)
    output_thread.start()