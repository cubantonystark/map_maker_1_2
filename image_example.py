import sys

import customtkinter
import os
from PIL import Image
import os
import subprocess
import sys
import time
import threading
import win32file
import MM_image_grouper
import MM_processing_photogrammetry
import logging
from tkinter import filedialog
import subprocess
from MM_objects import MapmakerProject
import customtkinter
import tkinter as tk


customtkinter.set_appearance_mode("Dark")  # Modes: system (default), light, dark
customtkinter.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

sd_drive = ""

# Open RESTful API that RX images from the Ground Control Stations
subprocess.Popen(["python", "C:/Users/micha/Documents/Coding/Photogrammetry/samples/MM_webserver.py"])


class SdCardInsertionEvent(tk.Event):
    def __init__(self, drive_letter):
        super().__init__()
        self.drive_letter = drive_letter


class TextRedirector:
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag

    def write(self, str):
        self.widget.insert(tk.END, str, (self.tag,))
        self.widget.see(tk.END)

    def flush(self):
        pass


def initialize_logger():
    # Create a logger object
    logger = logging.getLogger(__name__)

    # Set the log level
    logger.setLevel(logging.DEBUG)

    # Create a file handler
    handler = logging.FileHandler('C:/Users/micha/Documents/Coding/Photogrammetry/samples/log.txt')

    # Set the log message format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # Add the file handler to the logger
    logger.addHandler(handler)

    return logger


def detect_sd_card():
    drive_list = []
    drives = win32file.GetLogicalDrives()

    for drive in range(1, 26):
        mask = 1 << drive
        if drives & mask:
            drive_letter = chr(ord('A') + drive)
            if drive_letter == "D":
                pass
            else:
                try:
                    drive_type = win32file.GetDriveType(drive_letter + ":\\")
                    if drive_type == win32file.DRIVE_REMOVABLE:
                        drive_list.append(drive_letter)
                except Exception:
                    pass
        # try:
        #     os.listdir(drive_letter + ":\\")
        # except:
        #     print("Calling Bullshit on drive " + drive_letter)
        #     drive_list.pop(drive-1)

    return drive_list


def trigger_photogrammetry(each_folder, logger, mm_project):
    a = MM_processing_photogrammetry.processing_photogrammetry(each_folder, logger=logger, mm_project=mm_project)
    a.do_photogrammetry()

def get_image_files(folder):
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif']  # Add more extensions if needed
    image_files = []

    for root, dirs, files in os.walk(folder):
        for file in files:
            if any(file.lower().endswith(ext) for ext in image_extensions):
                image_files.append(os.path.join(root, file))

    return image_files



def button_click_event():
    dialog = customtkinter.CTkInputDialog(text="Type in a number:", title="Test")
    print("Number:", dialog.get_input())



class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("image_example.py")
        self.geometry("700x450")

        # set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # load images with light and dark mode image
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "gui_images")
        self.logo_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "logo.png")), size=(100, 30))
        self.large_test_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "large_test_image.png")), size=(500, 150))
        self.image_icon_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "image_icon_light.png")), size=(20, 20))
        self.home_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "home_dark.png")),
                                                 dark_image=Image.open(os.path.join(image_path, "home_light.png")), size=(20, 20))
        self.chat_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "chat_dark.png")),
                                                 dark_image=Image.open(os.path.join(image_path, "chat_light.png")), size=(20, 20))
        self.add_user_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "add_user_dark.png")),
                                                     dark_image=Image.open(os.path.join(image_path, "add_user_light.png")), size=(20, 20))

        # create navigation frame
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)

        self.navigation_frame_label = customtkinter.CTkLabel(self.navigation_frame, text="  3D Map Maker", image=self.logo_image,
                                                             compound="left", font=customtkinter.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        self.home_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Home",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   image=self.home_image, anchor="w", command=self.home_button_event)
        self.home_button.grid(row=1, column=0, sticky="ew")

        self.frame_2_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="System Logs",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      image=self.chat_image, anchor="w", command=self.frame_2_button_event)
        self.frame_2_button.grid(row=2, column=0, sticky="ew")

        self.frame_3_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Frame 3",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      image=self.add_user_image, anchor="w", command=self.frame_3_button_event)
        self.frame_3_button.grid(row=3, column=0, sticky="ew")

        self.appearance_mode_menu = customtkinter.CTkOptionMenu(self.navigation_frame, values=["Light", "Dark", "System"],
                                                                command=self.change_appearance_mode_event)
        self.appearance_mode_menu.grid(row=6, column=0, padx=20, pady=20, sticky="s")

        # create home frame
        self.home_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.home_frame.grid_columnconfigure(0, weight=1)

        self.home_frame_large_image_label = customtkinter.CTkLabel(self.home_frame, text="", image=self.large_test_image)
        self.home_frame_large_image_label.grid(row=0, column=0, padx=20, pady=10)


        self.home_frame_button_4 = customtkinter.CTkLabel(self.home_frame, text="Select Map Type:")
        self.home_frame_button_4.grid(row=4, column=0, padx=20, pady=10)
        self.button_frame = customtkinter.CTkFrame(self)
        self.radio_var1 = customtkinter.StringVar()
        self.radio_var1.set("OBJ")

        self.obj_radio_button = customtkinter.CTkRadioButton(self.home_frame, text="OBJ", variable=self.radio_var1, value="OBJ")
        self.obj_radio_button.grid(row=4, column=1, padx=20, pady=10)

        self.tiles_radio_button2 = customtkinter.CTkRadioButton(self.home_frame, text="TILES", variable=self.radio_var1,
                                                          value="TILES")
        self.tiles_radio_button2.grid(row=4, column=2, padx=20, pady=10)

        self.radio_label2 = customtkinter.CTkLabel(self.home_frame, text="Delete After Transfer?")
        self.radio_label2.grid(row=5, column=0, padx=20, pady=10)

        self.radio_var2 = customtkinter.StringVar()
        self.radio_var2.set("N")


        self.yes_radio_button = customtkinter.CTkRadioButton(self.home_frame, text="N", variable=self.radio_var2, value="N")
        self.yes_radio_button.grid(row=5, column=1, padx=20, pady=10)

        self.no_radio_button = customtkinter.CTkRadioButton(self.home_frame, text="Y", variable=self.radio_var2, value="Y")
        self.no_radio_button.grid(row=5, column=2, padx=20, pady=10)

        self.browse_label = customtkinter.CTkLabel(self.home_frame, text="Click the button to select a directory")
        self.browse_label.grid(row=6, column=0, padx=20, pady=10)

        self.browse_button = customtkinter.CTkButton(self.home_frame, text="Browse", command=self.browse_directory)
        self.browse_button.grid(row=6, column=1, padx=20, pady=10)

        # create second frame
        self.second_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.second_frame.grid_rowconfigure(0, weight=1)  # configure grid system
        self.second_frame.grid_columnconfigure(0, weight=1)

        self.output_text1 = customtkinter.CTkTextbox(self.second_frame, height=200)
      #  self.output_text1.grid(row=1, column=1, padx=20, pady=10)
        sys.stdout = self.TextRedirector(self.output_text1, "stdout")
        self.output_text1.grid(row=1, column=0, padx=20, pady=10, sticky="nsew", columnspan=4)

        # Redirect stdout to the Text widget

        self.output_text2 = customtkinter.CTkTextbox(self.second_frame, height=200)
        self.output_text2.grid(row=2, column=0, padx=20, pady=10, sticky="nsew", columnspan=4)

        self.output_text3 = customtkinter.CTkTextbox(self.second_frame, height=200)

        self.output_text3.grid(row=3, column=0, padx=20, pady=10, sticky="nsew", columnspan=4)

        # Create a button to run the executable
        self.runbentley_button = customtkinter.CTkButton(self.second_frame, text="Start Photogrammetry Engine", command=self.run_executable)
        self.runbentley_button.grid(row=0, column=0, padx=20, pady=10, sticky="nsew", columnspan=4)

        self.bind("<<SdCardInsertion>>", self.on_sd_card_insertion)

        # create third frame
        self.third_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")

        # select default frame
        self.select_frame_by_name("home")

    def browse_directory(self):
        path = filedialog.askdirectory()
        if path:
            print(f"Selected Directory: {path}")
            threading.Thread(target=self.print_sd_card_files, kwargs=({'folder_path': path})).start()
    class TextRedirector:
        def __init__(self, widget, tag="stdout"):
            self.widget = widget
            self.tag = tag

        def write(self, str):
            self.widget.insert(tk.END, str, (self.tag,))
            self.widget.see(tk.END)

        def flush(self):
            pass
    def print_sd_card_files(self, folder_path="", drive_letter=""):

        if drive_letter == "":
            path = folder_path
        if folder_path == "":
            path = drive_letter + ":\\"
        try:
            files = get_image_files(path)
            print(f"(Immage Files on {path}:")
            for file in files:
                print(file)
            folder_name_list = MM_image_grouper.group_images(path)
            print("Folder name list: " + str(folder_name_list))
            logger = initialize_logger()
            map_type = self.radio_var1.get()
            delete_after = self.radio_var2.get()
            print("Processing Triggered. Map type: " + map_type + " " + "Delete After = " + delete_after)
            print(folder_name_list)
            if delete_after == "Y":
                for f in files:
                    os.remove(path + f)
            if map_type == "OBJ":
                for each_folder in folder_name_list:
                    # file_count = len(os.listdir(each_folder))
                    new_project = MapmakerProject(name=each_folder, time_first_image=each_folder,
                                                  time_mm_start=time.time(),
                                                  image_folder=path)
                    print(new_project.as_dict())
                    threading.Thread(target=trigger_photogrammetry, args=(each_folder, logger, new_project)).start()
            if map_type == "TILES":
                for each_folder in folder_name_list:
                    new_project = MapmakerProject(name=each_folder, time_first_image=each_folder,
                                                  time_mm_start=time.time(),
                                                  image_folder=path)
                    threading.Thread(target=trigger_photogrammetry, args=(each_folder, logger, new_project)).start()
                    print(new_project.as_dict())

        except KeyError as e:
            error_message = f"Error accessing files on {path}: {e}"
            self.output_text.insert(tk.END, error_message + "\n")
    def handle_sd_card_insertion(self, drive_letter):
        self.event_generate("<<SdCardInsertion>>", data=drive_letter)
    def on_sd_card_insertion(self, event):
        global sd_drive
        self.process_sd_button = customtkinter.CTkButton(self.home_frame, text=f"Process Images on SD Card in {sd_drive}",
                                         command=lambda: self.process_sd_card(sd_drive, self.process_sd_button))
        self.process_sd_button.grid(row=8, column=1, padx=20, pady=10)

    def process_sd_card(self, drive_letter, button):
        threading.Thread(target=self.print_sd_card_files, kwargs=({'drive_letter': drive_letter})).start()
        button.destroy()  # Remove the button from the GUI after it has been clicked

    def sd_card_monitor(self):
        while True:
            drives_before = set(detect_sd_card())
            time.sleep(1)
            drives_after = set(detect_sd_card())
            new_drives = drives_after - drives_before
            for drive_letter in new_drives:
                print("drive detected = " + drive_letter)
                try:
                    os.listdir(drive_letter + ":\\")
                    global sd_drive
                    sd_drive = drive_letter
                    threading.Thread(target=self.handle_sd_card_insertion, args=(sd_drive,)).start()

                except:
                    print("Calling Bullshit on drive " + drive_letter)

    def select_frame_by_name(self, name):
        # set button color forv selected button
        self.home_button.configure(fg_color=("gray75", "gray25") if name == "home" else "transparent")
        self.frame_2_button.configure(fg_color=("gray75", "gray25") if name == "frame_2" else "transparent")
        self.frame_3_button.configure(fg_color=("gray75", "gray25") if name == "frame_3" else "transparent")

        # show selected frame
        if name == "home":
            self.home_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.home_frame.grid_forget()
        if name == "frame_2":
            self.second_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.second_frame.grid_forget()
        if name == "frame_3":
            self.third_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.third_frame.grid_forget()

    def run_executable(self):
        executable_path = "C:/Program Files/Bentley/ContextCapture/bin/CCEngine.exe"

        def read_output():
            process = subprocess.Popen(executable_path, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                       universal_newlines=True)
            while True:
                output = process.stdout.readline()
                if not output:
                    break
                self.output_text2.insert(tk.END, output)
                self.output_text2.see(tk.END)
            process.wait()

        # Create a separate thread to read the output
        output_thread = threading.Thread(target=read_output)
        output_thread.start()

    def home_button_event(self):
        self.select_frame_by_name("home")

    def frame_2_button_event(self):
        self.select_frame_by_name("frame_2")

    def frame_3_button_event(self):
        self.select_frame_by_name("frame_3")

    def change_appearance_mode_event(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)


if __name__ == "__main__":
    app = App()
    threading.Thread(target=app.sd_card_monitor).start()

    app.mainloop()

