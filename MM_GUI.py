import win32gui, win32con

'''
This snippet hides the console in non compiled scripts. Done for aesthetics
'''
# this_program = win32gui.GetForegroundWindow()
# win32gui.ShowWindow(this_program, win32con.SW_HIDE)

import random
from datetime import datetime
from PIL import Image
import os, shutil
import open3d as o3d

'''
This should take care  of the 'job cannot be accessed by this engine' error
allowing for a clean start.
'''

try:

    user_path = os.path.expanduser('~')
    cc_path = r"Documents/Bentley/ContextCapture Desktop/Jobs"
    user_path = os.path.join(user_path, cc_path)
    shutil.rmtree(user_path)

except FileNotFoundError:
    pass

'''
We will create the work folders on first run. This code serves as a check in case the one of the working folders gets
accidentaly deleted.
'''
dirs1 = ['ARTAK_MM/DATA/Raw_Images/UNZIPPED', 'ARTAK_MM/DATA/Raw_Images/ZIP/Completed',
         'ARTAK_MM/DATA/Raw_Images/ZIP/New', 'ARTAK_MM/DATA/Raw_Images/ZIP/Unzipping_in_progress',
         'ARTAK_MM/LOGS', 'ARTAK_MM/POST/Photogrammetry', 'ARTAK_MM/POST/Neural', 'ARTAK_MM/POST/Lidar',
         'ARTAK_MM/DATA/PointClouds']

# cleanup any straggler status file in case of disgraceful exit of either recon script

if os.path.exists("ARTAK_MM/LOGS/status.log"):
    os.remove("ARTAK_MM/LOGS/status.log")

for dir in dirs1:
    if not os.path.exists(dir):
        os.makedirs(dir)

    else:
        continue

import sys, time, threading, win32file, subprocess, pymeshlab
import MM_image_grouper
import MM_objects
import MM_processing_photogrammetry
import MM_logger
import logging
from tkinter import filedialog
from MM_objects import MapmakerProject, MapmakerSettings
import customtkinter
import tkinter as tk
import jobqueue_monitor_sample
from tkhtmlview import HTMLLabel
from pathlib import Path
import playsound

sys.setrecursionlimit(1999999999)

customtkinter.set_appearance_mode("Dark")  # Modes: system (default), light, dark
customtkinter.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

sd_drive = ""
# Open RESTful API that RX images from the Ground Control Stations
subprocess.Popen(["python", os.getcwd() + "/MM_webserver.py"])

# Open loop to check for zip files placed into a specific folder, usually placed there by the Restful API above
subprocess.Popen(["python", "MM_loop_check_files.py"])



class SdCardInsertionEvent(tk.Event):
    def __init__(self, drive_letter):
        super().__init__()
        self.drive_letter = drive_letter


def play_sound_processing_error():
    playsound.playsound("error.wav")
    print("playing sound: completed ")


def play_sound_processing_complete():
    playsound.playsound("completed.wav")
    print("playing sound: completed ")


def play_sound_processing_started():
    playsound.playsound("apocalypse_mission.wav")
    print("playing sound: started ")


class ScrollableLabelButtonFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, command=None, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.command = command
        self.radiobutton_variable = customtkinter.StringVar()
        self.label_list = []
        self.button_list = []

    def add_item(self, button_command=None, image=None, file=None, _time=None):
        # filename = os.listdir(item)
        #  print ("filename = " + filename)
        path = Path(file)
        if _time is None:
            for each_file in os.listdir(path.parent.absolute()):
                if "zip" in each_file:
                    _time = str(each_file).split(".")[0]
      #  print("file = " + file)
        label = customtkinter.CTkLabel(self, text=_time, image=image, compound="left", padx=5, anchor="w")
        button = customtkinter.CTkButton(self, text="Open", width=100, height=24)
       # print("button command = " + str(button_command))
      #  print(file)
        if button_command is not None:
            button.configure(command=lambda: self.command(button_command))
        label.grid(row=len(self.label_list), column=0, pady=(0, 10), sticky="w")
        button.grid(row=len(self.button_list), column=1, pady=(0, 10), padx=5)
        self.label_list.append(label)
        self.button_list.append(button)

    def remove_item(self, item):
        for label, button in zip(self.label_list, self.button_list):
            if item == label.cget("text"):
                label.destroy()
                button.destroy()
                self.label_list.remove(label)
                self.button_list.remove(button)
                return

    def remove_all(self):
        for label, button in zip(self.label_list, self.button_list):
            label.destroy()
            button.destroy()


class App(customtkinter.CTk):

    def __init__(self):
        super().__init__()
        app_settings = MM_objects.load_settings()

        self.iconbitmap(default='gui_images/EolianIcon.ico')
        self.title("EOLIAN MAP MAKER")
        self.geometry("1400x720")
        self.protocol('WM_DELETE_WINDOW', self.terminate)

        # set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # load images with light and dark mode image
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "gui_images")
        self.logo_image = customtkinter.CTkImage(
            light_image=Image.open(os.path.join(image_path, "MM_logo_light.png")),
            dark_image=Image.open(os.path.join(image_path, "MM_logo_light.png")),
            size=(218, 25.6))
        self.large_test_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "MM_logo_light.png")),
                                                       size=(250, 64))
        self.image_icon_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "image_icon_light.png")),
                                                       size=(20, 20))
        self.home_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "home_dark.png")),
                                                 dark_image=Image.open(os.path.join(image_path, "home_light.png")),
                                                 size=(20, 20))
        self.chat_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "chat_dark.png")),
                                                 dark_image=Image.open(os.path.join(image_path, "chat_light.png")),
                                                 size=(20, 20))
        self.add_user_image = customtkinter.CTkImage(
            light_image=Image.open(os.path.join(image_path, "add_user_dark.png")),
            dark_image=Image.open(os.path.join(image_path, "add_user_light.png")), size=(20, 20))

        # create fourth frame
        self.fourth_frame = customtkinter.CTkScrollableFrame(self, corner_radius=0, fg_color="transparent")

        # create navigation frame
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(5, weight=1)

        self.navigation_frame_label = customtkinter.CTkLabel(self.navigation_frame, text="",
                                                             image=self.logo_image,
                                                             compound="left",
                                                             font=customtkinter.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.home_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10,
                                                   text="Home",
                                                   fg_color="transparent", text_color=("gray10", "gray90"),
                                                   hover_color=("gray70", "gray30"),
                                                   image=self.home_image, anchor="w", command=self.home_button_event)
        self.home_button.grid(row=1, column=0, sticky="ew")

        self.frame_2_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40,
                                                      border_spacing=10, text="System Logs",
                                                      fg_color="transparent", text_color=("gray10", "gray90"),
                                                      hover_color=("gray70", "gray30"),
                                                      image=self.chat_image, anchor="w",
                                                      command=self.frame_2_button_event)
        self.frame_2_button.grid(row=2, column=0, sticky="ew")

        self.frame_3_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40,
                                                      border_spacing=10, text="Images",
                                                      fg_color="transparent", text_color=("gray10", "gray90"),
                                                      hover_color=("gray70", "gray30"),
                                                      image=self.add_user_image, anchor="w",
                                                      command=self.frame_3_button_event)
        self.frame_3_button.grid(row=3, column=0, sticky="ew")
        self.frame_4_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40,
                                                      border_spacing=10, text="System Settings",
                                                      fg_color="transparent", text_color=("gray10", "gray90"),
                                                      hover_color=("gray70", "gray30"),
                                                      image=self.add_user_image, anchor="w",
                                                      command=self.frame_4_button_event)
        self.frame_4_button.grid(row=4, column=0, sticky="ew")

        # create home frame
        self.home_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.home_frame.grid_columnconfigure(0, weight=1)

        self.home_frame_large_image_label = customtkinter.CTkLabel(self.home_frame, text="",
                                                                   image=self.large_test_image)
    #    self.home_frame_large_image_label.grid(row=0, column=0, padx=20, pady=10, sticky="EW")
        # add settings for auto process sd card
        self.auto_process_sd = customtkinter.CTkLabel(self.fourth_frame, text="Auto Process SD Card Content?")
        self.auto_process_sd.grid(row=6, column=0, padx=20, pady=10)

        self.auto_process_sd_frame = customtkinter.CTkFrame(self)
        self.auto_process_sd_var = customtkinter.BooleanVar()
        self.auto_process_sd_var.set(app_settings["auto_process_sd"])

        self.auto_process_button = customtkinter.CTkRadioButton(self.fourth_frame,
                                                                text="Y",
                                                                variable=self.auto_process_sd_var,
                                                                value=True)
        self.auto_process_button.grid(row=6, column=1, padx=20, pady=10)

        self.no_auto_process_button = customtkinter.CTkRadioButton(self.fourth_frame,
                                                                   text="N",
                                                                   variable=self.auto_process_sd_var,
                                                                   value=False)
        self.no_auto_process_button.grid(row=6, column=2, padx=20, pady=10)

        ###Create PC buttons

        self.home_frame_button_4 = customtkinter.CTkLabel(self.fourth_frame, text="Mesh from PointCloud")
        self.home_frame_button_4.grid(row=7, column=0, padx=20, pady=10)
        self.button_frame = customtkinter.CTkFrame(self)
        self.mesh_from_pointcloud_type_var = customtkinter.StringVar()
        self.mesh_from_pointcloud_type_var.set(app_settings['mesh_from_pointcloud_type'])

        self.obj_radio_button = customtkinter.CTkRadioButton(self.fourth_frame, text="New (Cesium)",
                                                             variable=self.mesh_from_pointcloud_type_var,
                                                             value="ces")
        self.obj_radio_button.grid(row=7, column=1, padx=20, pady=10)

        self.tiles_radio_button2 = customtkinter.CTkRadioButton(self.fourth_frame, text="Legacy (Hololens)",
                                                                variable=self.mesh_from_pointcloud_type_var,
                                                                value="leg")
        self.tiles_radio_button2.grid(row=7, column=2, padx=20, pady=10)

        ###

        self.home_frame_server = customtkinter.CTkLabel(self.fourth_frame, text="Select ARTAK Server:")
        self.home_frame_server.grid(row=0, column=0, padx=20, pady=10)

        self.server_button_frame = customtkinter.CTkFrame(self)
        self.server_var = customtkinter.StringVar()
        self.server_var.set(app_settings["artak_server"])

        self.cloud_radio_button = customtkinter.CTkRadioButton(self.fourth_frame, text="Cloud",
                                                               variable=self.server_var,
                                                               value="https://esp.eastus2.cloudapp.azure.com/")
        self.cloud_radio_button.grid(row=0, column=1, padx=20, pady=10)

        self.local_radio_button = customtkinter.CTkRadioButton(self.fourth_frame, text="Local",
                                                               variable=self.server_var,
                                                               value="http://eoliancluster.local/")
        self.local_radio_button.grid(row=0, column=2, padx=20, pady=10)

        self.home_frame_button_4 = customtkinter.CTkLabel(self.fourth_frame, text="Select Map Type:")
        self.home_frame_button_4.grid(row=4, column=0, padx=20, pady=10)
        self.button_frame = customtkinter.CTkFrame(self)

        self.auto_open_var = customtkinter.BooleanVar()

        self.auto_open_var.set(self.string_to_bool(app_settings["auto_open_upon_completion"]))
        self.auto_open_text = customtkinter.CTkLabel(self.fourth_frame, text="Auto-open upon completion?")
        self.auto_open_text.grid(row=11, column=0, padx=20, pady=10)
        self.auto_open_switch = customtkinter.CTkSwitch(self.fourth_frame, text="Yes", variable=self.auto_open_var)
        self.auto_open_switch.grid(row=11, column=1, padx=20, pady=10)





        self.map_type_var = customtkinter.StringVar()
        self.map_type_var.set(app_settings["map_type"])

        self.obj_radio_button = customtkinter.CTkRadioButton(self.fourth_frame, text="OBJ", variable=self.map_type_var,
                                                             value="OBJ")
        self.obj_radio_button.grid(row=4, column=1, padx=20, pady=10)

        self.tiles_radio_button2 = customtkinter.CTkRadioButton(self.fourth_frame, text="TILES",
                                                                variable=self.map_type_var,
                                                                value="TILES")
        self.tiles_radio_button2.grid(row=4, column=2, padx=20, pady=10)

        self.radio_label2 = customtkinter.CTkLabel(self.fourth_frame, text="Delete After Transfer?")
        self.radio_label2.grid(row=5, column=0, padx=20, pady=10)

        self.delete_after_transfer_var = customtkinter.StringVar()
        self.delete_after_transfer_var.set(app_settings["delete_after_transfer"])

        self.yes_radio_button = customtkinter.CTkRadioButton(self.fourth_frame, text="N", variable=self.delete_after_transfer_var,
                                                             value="N")
        self.yes_radio_button.grid(row=5, column=1, padx=20, pady=10)

        self.no_radio_button = customtkinter.CTkRadioButton(self.fourth_frame, text="Y", variable=self.delete_after_transfer_var,
                                                            value="Y")
        self.no_radio_button.grid(row=5, column=2, padx=20, pady=10)

        self.browse_label = customtkinter.CTkLabel(self.home_frame, text="Select Image/Video")
        self.browse_label.grid(row=6, column=0, padx=20, pady=10)

        self.browse_button = customtkinter.CTkButton(self.home_frame, text="Browse", command=self.browse_directory)
        self.browse_button.grid(row=6, column=1, padx=20, pady=10)

        self.browse_label_pc = customtkinter.CTkLabel(self.home_frame, text="Select PointCloud")
        self.browse_label_pc.grid(row=8, column=0, padx=20, pady=10)

        self.browse_button_pc = customtkinter.CTkButton(self.home_frame, text="Browse", command=self.gen_pc,
                                                        state="normal")
        self.browse_button_pc.grid(row=8, column=1, padx=20, pady=10)

        # self.browse_label_nr = customtkinter.CTkLabel(self.home_frame, text="Neural Surface Reconstruction")
        # self.browse_label_nr.grid(row=10, column=0, padx=20, pady=10)
        #
        # self.browse_button_nr = customtkinter.CTkButton(self.home_frame, text="Browse", command=self.process_for_nr,
        #                                                 state="normal")
        # self.browse_button_nr.grid(row=10, column=1, padx=20, pady=10)
        #
        # self.browse_label_med = customtkinter.CTkLabel(self.home_frame, text="Process Med OBJ")
        # self.browse_label_med.grid(row=12, column=0, padx=20, pady=10)
        #
        # self.browse_button_med = customtkinter.CTkButton(self.home_frame, text="Browse", command=self.process_med_obj,
        #                                                  state="normal")
        # self.browse_button_med.grid(row=12, column=1, padx=20, pady=10)

        # create second frame
        self.second_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.second_frame.grid_rowconfigure(0, weight=1)  # configure grid system
        self.second_frame.grid_columnconfigure(0, weight=1)

        self.home_frame_text = customtkinter.CTkTextbox(self.second_frame, height=200)
        self.home_frame_text.grid(row=0, column=0, padx=20, pady=10, sticky="nsew", columnspan=4)

        # self.output_text1 = customtkinter.CTkTextbox(self.second_frame, height=200)
        # #  self.output_text1.grid(row=1, column=1, padx=20, pady=10)
        # sys.stdout = self.TextRedirector(self.output_text1, "stdout")
        # self.output_text1.grid(row=1, column=0, padx=20, pady=10, sticky="nsew", columnspan=4)

        # Redirect stdout to the Text widget

        self.output_text2 = customtkinter.CTkTextbox(self.second_frame, height=200)
        self.output_text2.grid(row=2, column=0, padx=20, pady=10, sticky="nsew", columnspan=4)

        self.output_text3 = customtkinter.CTkTextbox(self.second_frame, height=200)
        self.output_text3.grid(row=3, column=0, padx=20, pady=10, sticky="nsew", columnspan=4)

        # create a bind between the on_sd_card_insertion method and the SdCardInsertion event
        self.bind("<<SdCardInsertion>>", self.on_sd_card_insertion)
        self.bind("<<ProjectStarted>>", self.on_project_started)

        # create third frame
        self.third_frame = customtkinter.CTkScrollableFrame(self, corner_radius=0, fg_color="transparent")
        self.apperance_mode_label = customtkinter.CTkLabel(self.fourth_frame, text="App Screen Mode")
        self.apperance_mode_label.grid(row=15, column=0, padx=20, pady=20, sticky="s")

        self.appearance_mode_menu = customtkinter.CTkOptionMenu(self.fourth_frame,
                                                                values=["Light", "Dark", "System"]
                                                                )
        self.appearance_mode_menu.grid(row=15, column=1, padx=20, pady=20, sticky="nsew", columnspan=2)


        self.quality = customtkinter.StringVar()
        self.quality.set("Speed")
        self.quality_label = customtkinter.CTkLabel(self.fourth_frame, text="Speed vs Quality")
        self.quality_label.grid(row=22, column=0, padx=20, pady=20, sticky="s")
        self.quality_menu = customtkinter.CTkOptionMenu(self.fourth_frame,
                                                                values=["Speed", "Balanced", "Quality"],
                                                                variable=self.quality
                                                        )
        self.quality_menu.grid(row=22, column=1, padx=20, pady=20, sticky="nsew", columnspan=2)

        # select default frame
        self.select_frame_by_name("home")
        self.list_of_projects = []
        self.scrollable_label_button_frame = ScrollableLabelButtonFrame(master=self, width=300,
                                                                        command=self.label_button_frame_event,
                                                                        corner_radius=0)
        self.scrollable_label_button_frame.grid(row=0, column=2, padx=0, pady=0, sticky="nsew")


        self.list_of_objs = []

        self.list_of_progress_bars = []
        self.local_server_ip_var = app_settings["local_server_ip"]
        self.local_server_label = customtkinter.CTkLabel(self.fourth_frame, text="Custom Server Domain Name or IP Address")
        self.local_server_ip_var = customtkinter.CTkEntry(self.fourth_frame, placeholder_text=app_settings["local_server_ip"])
        self.local_server_label.grid(row=12, column=0, padx=20, pady=10, sticky="ew")
        self.local_server_ip_var.grid(row=12, column=1, padx=20, pady=10, sticky="ew")


        self.time_between_images = customtkinter.CTkLabel(self.fourth_frame, text="Max time between image groups")
        self.time_between_images_var = customtkinter.CTkEntry(self.fourth_frame, placeholder_text=app_settings["max_interval_between_images"])
        self.time_between_images_var.setvar(app_settings["max_interval_between_images"])
        self.time_between_images.grid(row=13, column=0, padx=20, pady=10, sticky="ew")
        self.time_between_images_var.grid(row=13, column=1, padx=20, pady=10, sticky="ew")

        self.time_between_frames = customtkinter.CTkLabel(self.fourth_frame, text="Video Frame Extraction Rate (in frames)")
        self.time_between_frames_var = customtkinter.CTkEntry(self.fourth_frame, placeholder_text="20")
        self.time_between_frames_var.setvar("20")
        self.time_between_frames.grid(row=18, column=0, padx=20, pady=10, sticky="ew")
        self.time_between_frames_var.grid(row=18, column=1, padx=20, pady=10, sticky="ew")

        self.partition_key = customtkinter.CTkLabel(self.fourth_frame, text="Map Partition Key")
        self.partition_key_var = customtkinter.CTkEntry(self.fourth_frame, placeholder_text="None")
        self.partition_key_var.setvar("")
        self.partition_key.grid(row=14, column=0, padx=20, pady=10, sticky="ew")
        self.partition_key_var.grid(row=14, column=1, padx=20, pady=10, sticky="ew")

        self.rerun_failed_jobs_var = customtkinter.StringVar()
        self.rerun_failed_jobs = customtkinter.CTkLabel(self.fourth_frame, text="Rerun Failed Jobs")
        self.rerun_failed_jobs.grid(row=10, column=0, padx=20, pady=10, sticky="ew")
        self.rerun_radio_button_y = customtkinter.CTkRadioButton(self.fourth_frame, text="Y",
                                                                 variable=self.rerun_failed_jobs_var,
                                                                 value="Y")
        self.rerun_radio_button_y.grid(row=10, column=1, padx=20, pady=10)

        self.rerun_radio_button_n = customtkinter.CTkRadioButton(self.fourth_frame, text="N",
                                                                 variable=self.rerun_failed_jobs_var,
                                                                 value="N")
        self.rerun_radio_button_n.grid(row=10, column=2, padx=20, pady=10)
        self.rerun_failed_jobs_var.set(app_settings["rerun_failed_jobs"])
        # todo fix delete button which currently doesnt have permission to delete
        self.save_settings_button = customtkinter.CTkButton(self.fourth_frame, text="Save Settings",
                                                          command=self.save_settings, state="normal")
        self.save_settings_button.grid(row=16, column=1, padx=20, pady=10)

        r = random.Random()
        session_id = r.randint(1, 10000000)
        session_logger = MM_logger.initialize_logger("SessionLog_App_" + str(session_id), log_text_widget=self.output_text2)
        print = session_logger.info

        self.session_logger = session_logger
        session_logger.info("App Startup Complete")

    # not working right now because of permissions
    # todo fix permissions

    def save_settings(self):
        settings = MM_objects.MapmakerSettings()
        settings.rerun_failed_jobs = self.rerun_failed_jobs_var.get()
        settings.map_type = self.map_type_var.get()
        settings.artak_server = self.server_var.get()
        settings.local_server_ip = self.local_server_ip_var.get()
        settings.app_screen_mode = self.appearance_mode_menu.get()
        settings.auto_process_sd = self.auto_process_sd_var.get()
        settings.max_interval_between_images = self.time_between_images_var.get()
        settings.mesh_from_pointcloud_type = self.mesh_from_pointcloud_type_var.get()
        settings.delete_after_transfer = self.delete_after_transfer_var.get()
        settings.auto_open_upon_completion = self.bool_to_string(self.auto_open_var.get())
        settings.save()

    def bool_to_string(self, bool):
        if bool:
            return "true"
        else:
            return "false"
    def string_to_bool(self, string):
        if string == "false":
            return False
        if string == "true":
            return True
    def show_training(self):
        time.sleep(2)
        
        return

    def terminate(self):
        # This will create a file in the logs folder that will signal we are cloing shop
        with open(os.getcwd() + "/ARTAK_MM/LOGS/kill.mm", "w") as killer:
            pass
        process = threading.current_thread()
        print("Current thread PID is: " + str(process))
        os.system('taskkill /im iTwinCaptureModelerEngine.exe /F')
        os.remove(os.getcwd() + "/ARTAK_MM/LOGS/kill.mm")
        os.system('killall.bat')
        sys.exit()

    def delete_all_source_data(self):
        directory = os.path.join(os.getcwd(), 'ARTAK_MM/DATA/Raw_Images/UNZIPPED')
        for f in os.listdir(directory):
            os.remove(os.path.join(directory, f))

    def add_radio_button_set(self, button_label, button_option1, button_option2):
        print("WIP")

    def process_for_nr(self):

        subprocess.Popen(["python", "MM_proces s_neural.py"])

    def open_pc_folder(self):

        cmd = os.getcwd() + "/ARTAK_MM/DATA/PointClouds"
        os.startfile(cmd)

    def gen_pc(self):

        global hr_proc, lr_proc

        value = self.mesh_from_pointcloud_type_var.get()

        if 'leg' in value:

            with open('ARTAK_MM/LOGS/pc_type.log', 'w') as pc_type:
                pc_type.write('leg')

        else:
            with open('ARTAK_MM/LOGS/pc_type.log', 'w') as pc_type:
                pc_type.write('hr')

        subprocess.Popen(["python", "MM_pc2mesh.py"])

    def process_med_obj(self):

        global hr_proc, lr_proc

        value = self.mesh_from_pointcloud_type_var.get()

        if 'leg' in value:

            with open('ARTAK_MM/LOGS/pc_type.log', 'w') as pc_type:
                pc_type.write('leg')
        else:
            with open('ARTAK_MM/LOGS/pc_type.log', 'w') as pc_type:
                pc_type.write('hr')

        subprocess.Popen(["python", "MM_process_med_obj.py"])

    def display_activity_on_pc_recon(self):

        # will check if recon is running. should it be running, the 'Browse' button is disabled'

        self.progressbar_pc = customtkinter.CTkProgressBar(self.home_frame)

        while True:

            try:
                with open(os.getcwd() + "/ARTAK_MM/LOGS/kill.mm", "r"):
                    pass
                print("Killing PC recon")
                sys.exit()

            except FileNotFoundError:

                if os.path.exists("ARTAK_MM/LOGS/status.log"):

                    self.browse_button_pc.configure(state='disabled')

                    self.progressbar_pc.grid(row=8, column=2, padx=20, pady=10, sticky="ew")
                    self.progressbar_pc.set(0)
                    self.progressbar_pc.start()

                else:

                    self.browse_button_pc.configure(state='normal')
                    self.progressbar_pc.stop()
                    self.progressbar_pc.configure(mode="determinate", progress_color="green")
                    self.progressbar_pc.set(1)

                    try:
                        with open('ARTAK_MM/LOGS/status.log') as status:
                            status_finished = status.read().rstrip()
                        if 'done' in status_finished:
                            app.find_folders_with_obj_once()
                        else:
                            pass

                    except FileNotFoundError:
                        pass

                time.sleep(2)

    def display_activity_on_nr_recon(self):
        # will check if neural recon is running. should it be running, the 'Browse' button is disabled'

        self.progressbar_nr = customtkinter.CTkProgressBar(self.home_frame)

        while True:

            try:
                with open(os.getcwd() + "/ARTAK_MM/LOGS/kill.mm", "r"):
                    pass
                print("Killing Neural recon")
                sys.exit()

            except FileNotFoundError:

                if os.path.exists("ARTAK_MM/LOGS/status_nr.log"):

                    if os.path.exists("ARTAK_MM/LOGS/t_render.log"):
                        self.browse_button_nr.configure(text="View 3D Scene")
                        self.browse_button_nr.configure(command=self.show_training)
                        self.browse_button_nr.configure(state='normal')

                    else:
                        self.browse_button_nr.configure(text="Browse")
                        self.browse_button_nr.configure(state='disabled')

                    self.progressbar_nr.grid(row=10, column=2, padx=20, pady=10, sticky="ew")
                    self.progressbar_nr.set(0)
                    self.progressbar_nr.start()

                else:

                    self.browse_button_nr.configure(command=self.process_for_nr)
                    self.browse_button_nr.configure(state='normal')
                    self.progressbar_nr.stop()
                    self.progressbar_nr.configure(mode="determinate", progress_color="green")
                    self.progressbar_nr.set(1)

                    try:
                        with open('ARTAK_MM/LOGS/status.log') as status:
                            status_finished = status.read().rstrip()
                        if 'done' in status_finished:
                            app.find_folders_with_obj_once()
                        else:
                            pass

                    except FileNotFoundError:
                        pass

                time.sleep(2)

    def browse_directory(self):
        path = filedialog.askdirectory()

        if path:
            print(f"Selected Directory: {path}")
            threading.Thread(name='t6', target=self.process_files, kwargs=({'folder_path': path})).start()

    def check_project_status(self):
        status = self.job_queue_monitor()
        self.home_frame_text = status

    def trigger_photogrammetry(self, each_folder, logger, mm_project=MM_objects.MapmakerProject()):
        session_project_number = mm_project.session_project_number
        mm_project.local_image_folder = os.getcwd() + "/ARTAK_MM/DATA/Raw_Images/UNZIPPED/" + each_folder
        mm_project.partition_key = self.partition_key_var.get()
        progress_bar = self.on_project_started(path=each_folder, mm_project=mm_project,
                                               session_project_number=session_project_number)
        mm_project.manually_made_name = "ManualNameTest"
        try:
            a = MM_processing_photogrammetry.ProcessingPhotogrammetry(each_folder, logger=logger,
                                                                      mm_project=mm_project)
            status = a.do_photogrammetry()
        except:
            if mm_project.status == "Error":
                print("Error processing 3D Map")
                # play_sound_processing_complete()
        self.on_project_completed(progress_bar=progress_bar, path=each_folder, mm_project=mm_project)

    def label_button_frame_event(self, item):
        print(f"label button frame clicked: {item}")
        self.open_obj(item)

    class TextRedirector:
        def __init__(self, widget, tag="stdout"):
            self.widget = widget
            self.tag = tag

        def write(self, str):
            self.widget.insert(tk.END, str, (self.tag,))
            self.widget.see(tk.END)

        def flush(self):
            pass

    def add_images_to_page(self, path=None):
        self.frame_3_button_event()
        image_path = os.path.join(os.getcwd() + '/ARTAK_MM/DATA/Raw_Images/UNZIPPED/', path)
        images = os.listdir(image_path)
        row = 0
        column = 0
        number_of_columns = 3
        #   self.third_frame.
        # self.third_frame = customtkinter.CTkScrollableFrame(self, corner_radius=0, fg_color="transparent")
        for widget in self.third_frame.winfo_children():
            widget.destroy()
        for each_image in images:
            try:
                image_payload = customtkinter.CTkImage(Image.open(os.path.join(image_path, each_image)),
                                                       size=(300, 255))
                tk_image = customtkinter.CTkLabel(self.third_frame, image=image_payload, text="")
                tk_image.grid(row=row, column=column, padx=10, pady=10)
                column = column + 1
                if column == number_of_columns:
                    row = row + 1
                    column = 0
            except:
                print("Ignoring JSON File")

    def process_files(self, folder_path="", drive_letter=""):

        if drive_letter == "":
            path = folder_path
        if folder_path == "":
            path = drive_letter + ":\\"
        try:
            files = get_image_files(path)
            print(f"(Image Files on {path}:")
            for file in files:
                print(file)
            image_spacing = self.time_between_images_var.get()
            rerun = self.rerun_failed_jobs_var.get()
            if rerun == "Y":
                rerun = True
            if rerun == "N":
                rerun = False
            frame_extraction_rate = self.time_between_frames_var.get()
            if frame_extraction_rate == "":
                frame_extraction_rate = "20"
            folder_name_list = MM_image_grouper.group_images(path, logger=self.session_logger,
                                                             image_spacing=image_spacing, rerun=rerun, frame_spacing=frame_extraction_rate)
            print("Folder name list: " + str(folder_name_list))
            map_type = self.map_type_var.get()
            delete_after = self.delete_after_transfer_var.get()
            artak_server = self.server_var.get()
            print("Processing Triggered. Map type: " + map_type + " " + "Delete After = " + delete_after)
            print(folder_name_list)
            if delete_after == "Y":
                for f in files:
                    os.remove(path + f)
            if map_type == "OBJ":
                projects = []
                for each_folder in folder_name_list:
                    file_count = len(os.listdir(os.getcwd() + "/ARTAK_MM/DATA/Raw_Images/UNZIPPED/" + each_folder))
                    logger = MM_logger.initialize_logger("MMProjectLog_" + each_folder)
                    if self.local_server_ip_var.get() != "":
                        artak_server = self.local_server_ip_var.get()
                        artak_server = self.cleanup_manually_entered_server_address(artak_server)

                    session_project_number = len(self.list_of_projects)
                    new_project = MapmakerProject(name=each_folder, time_first_image=each_folder,
                                                  time_mm_start=time.time(),
                                                  image_folder=each_folder, total_images=file_count, logger=logger,
                                                  artak_server=artak_server,
                                                  session_project_number=session_project_number, map_type="OBJ",
                                                  quality=self.quality.get()
                                                  )
                    self.list_of_projects.append(new_project)
                    projects.append(new_project)
                    print(new_project.as_dict())
                count = 0
                for each_folder in folder_name_list:
                    #threading.Thread(name='t7', target=self.trigger_photogrammetry,
                    #                 args=(each_folder, logger, new_project)).start()
                    self.trigger_photogrammetry(each_folder, logger, projects[count])
                    count = count + 1
                    # send the message that a project has been started

            if map_type == "TILES":

                for each_folder in folder_name_list:
                    file_count = len(os.listdir(path))
                    logger = MM_logger.initialize_logger(each_folder)
                    session_project_number = len(self.list_of_projects)
                    new_project = MapmakerProject(name=each_folder, time_first_image=each_folder,
                                                  time_mm_start=time.time(),
                                                  image_folder=each_folder, total_images=file_count, logger=logger,
                                                  artak_server=artak_server,
                                                  session_project_number=session_project_number, map_type="TILES"
                                                  )
                    self.list_of_projects.append(new_project)
                    print(new_project.as_dict())
                    threading.Thread(name='t8', target=self.trigger_photogrammetry,
                                     args=(each_folder, logger, new_project)).start()

                    # send the message that a project has been started
                    self.on_project_started(path=path, mm_project=new_project)

        except KeyError as e:
            error_message = f"Error accessing files on {path}: {e}"
            self.output_text.insert(tk.END, error_message + "\n")

    def handle_sd_card_insertion(self, drive_letter):
        self.event_generate("<<SdCardInsertion>>", data=drive_letter)

    def handle_project_started(self, project=MM_objects.MapmakerProject()):
        self.event_generate("<<ProjectStarted>>", data=project)

    def job_queue_monitor(self):
        while True:

            try:

                with open(os.getcwd() + "/ARTAK_MM/LOGS/kill.mm", "r"):
                    pass
                print("Killing Job Queue Monitor")
                sys.exit()

            except FileNotFoundError:

                que_dict = jobqueue_monitor_sample.main()
                self.output_text3.delete("1.0", tk.END)
                for each_job in que_dict:
                    self.output_text3.insert(tk.END, str(each_job) + "\n")
                time.sleep(5)

    def mm_project_monitor(self):
        while True:

            try:
                with open(os.getcwd() + "/ARTAK_MM/LOGS/kill.mm", "r"):
                    pass
                print("Killing Project Monitor")
                sys.exit()

            except FileNotFoundError:

                self.home_frame_text.delete("1.0", tk.END)
                self.home_frame_text.insert(tk.END, "Jobs from this Session \n")
                count = 1
                time_fields = ["time_mm_start", "time_processing_start", "time_processing_complete",
                               "time_accepted_by_artak"]
                for each_project in self.list_of_projects:
                    self.home_frame_text.insert(tk.END, "\nJob " + str(count) + "\n")
                    for each_key in each_project.as_dict().keys():
                        if each_key in time_fields:
                            timestamp = each_project.as_dict()[each_key]
                            try:
                                converted_time = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d_%H-%M-%S")
                                line = str(each_key) + " = " + str(converted_time) + "\n"
                            except TypeError:
                                line = ""
                        else:
                            line = str(each_key) + " = " + str(each_project.as_dict()[each_key]) + "\n"
                        self.home_frame_text.insert(tk.END, line)
                    count += 1
                time.sleep(5)

    def find_folders_with_obj(self):

        current_file_count = 0
        previous_file_count = 0

        while True:
            current_file_count = 0
            directory = ["ARTAK_MM/POST/Photogrammetry", "ARTAK_MM/POST/Lidar", "ARTAK_MM/POST/Neural"]
            for dirs in directory:
                current_file_count += len(os.listdir(os.path.join(os.getcwd(), dirs)))
            if current_file_count != previous_file_count:
                directory = os.getcwd() + "/ARTAK_MM/POST"
                self.list_of_objs = []
                for root, dirs, files in os.walk(directory):
                    if "Model" in dirs:
                        output_model_folder = os.path.join(root, "Model")
                        obj_files = [file for file in os.listdir(output_model_folder) if file.endswith(".obj")]
                        if obj_files:
                            #print(f"Found Preprocessed folder with OBJ file(s): {output_model_folder}")
                            self.list_of_objs.append(output_model_folder)
                            self.scrollable_label_button_frame.update()
                self.scrollable_label_button_frame = ScrollableLabelButtonFrame(master=self, width=300,
                                                                                command=self.label_button_frame_event,
                                                                                corner_radius=0)
                self.scrollable_label_button_frame.grid(row=0, column=2, padx=0, pady=0, sticky="nsew")
                for each_item in self.list_of_objs:  # add items with images
                    self.scrollable_label_button_frame.add_item(file=each_item, button_command=each_item)
            else:
                pass
            previous_file_count = current_file_count
            time.sleep(5)

    def find_folders_with_obj_once(self):

        self.list_of_objs = []

        if not os.path.exists("ARTAK_MM/LOGS/status.log") and not os.path.exists("ARTAK_MM/LOGS/status_nr.log"):
            pass

        else:
            previous_file_count = 0
            current_file_count = 0
            directory = ["ARTAK_MM/POST/Photogrammetry", "ARTAK_MM/POST/Lidar", "ARTAK_MM/POST/Neural"]
            for dirs in directory:
                current_file_count += len(os.listdir(os.path.join(os.getcwd(), dirs)))
        return

    def cleanup_manually_entered_server_address(self, address):
        if address[-1] != "/":
            address = address + "/"
        if "http://" not in address and "https://" not in address:
            address = "http://" + address
        return address

    def open_obj(self, path):
        path = os.path.join(path + "/", "Model.obj")
        print("opening obj" + path)
        subprocess.Popen(['start', ' ', path], shell=True)

    def open_obj_new(self, path):
        print("opening obj " + path)
        subprocess.Popen(['start', ' ', path], shell=True)

    def on_sd_card_insertion(self, event):
        global sd_drive
        # create a button to process the drive's images

        self.process_sd_button = customtkinter.CTkButton(self.home_frame,
                                                         text=f"Process SD in {sd_drive}",
                                                         command=lambda: self.process_sd_card(sd_drive,
                                                                                              self.process_sd_button))
        if self.auto_process_sd_var.get():
            self.process_sd_card(sd_drive, self.process_sd_button)

        self.process_sd_button.grid(row=7, column=1, padx=20, pady=10)

    def on_project_started(self, path, session_project_number, mm_project=MapmakerProject()):
        mm_project.status = "Processing"
        project2_label = customtkinter.CTkLabel(self.home_frame, text=mm_project.name)
        project2_open_images_icon = customtkinter.CTkButton(self.home_frame,
                                                            text="View Images",
                                                            command=lambda: threading.Thread(
                                                                target=self.add_images_to_page,
                                                                kwargs={"path": mm_project.name}).start())
        project2_open_images_icon.grid(row=session_project_number + 11, column=2, padx=20, pady=10)
        project2_label.grid(row=session_project_number + 11, column=0, padx=20, pady=10)
        e1 = customtkinter.CTkEntry(self.home_frame)
        e1.grid(row=session_project_number + 11, column=1, padx=20, pady=10, sticky="ew")
        progressbar_1 = customtkinter.CTkProgressBar(self.home_frame)
        progressbar_1.grid(row=session_project_number + 11, column=4, padx=20, pady=10, sticky="ew")

        progressbar_1.configure(mode="determinate")
        progressbar_1.set(0)
        progressbar_1.start()

        threading.Thread(name='t9', target=self.update_name_manually_loop, args=(e1, mm_project)).start()
        return progressbar_1

    def update_name_manually_loop(self, input_field, mm_project):
        while True:

            try:
                with open(os.getcwd() + "/ARTAK_MM/LOGS/kill.mm", "r"):
                    pass
                print("Killing Manual Updater")
                sys.exit()

            except FileNotFoundError:

                mm_project.manually_made_name = input_field.get()
                time.sleep(5)

    def on_change_name(self):
        print("on name change")

    def on_project_completed(self, progress_bar, path=None, mm_project=MapmakerProject()):
        # play_sound_processing_complete()
        path = mm_project.completed_file_path
        session_project_number = mm_project.session_project_number
        if mm_project.status == "Error":
            progress_bar.configure(mode="determinate", progress_color="red")
            progress_bar.set(1)
            progress_bar.stop()
        else:
            project2_open_map_icon = customtkinter.CTkButton(self.home_frame,
                                                             text="Open Map",
                                                             command=lambda: threading.Thread(name='t10',
                                                                                              target=self.open_obj_new,
                                                                                              kwargs={
                                                                                                  "path": path}).start())
            project2_open_map_icon.grid(row=session_project_number + 11, column=3, padx=20, pady=10)
            progress_bar.configure(mode="determinate", progress_color="green")
            progress_bar.set(1)
            progress_bar.stop()
        mm_project.total_processing_time = mm_project.time_processing_complete - mm_project.time_processing_start
        if self.auto_open_var:
            self.open_obj_new(path)


    def process_sd_card(self, drive_letter, button):
        threading.Thread(name='t11', target=self.process_files, kwargs=({'drive_letter': drive_letter})).start()
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
                    threading.Thread(name='t12', target=self.handle_sd_card_insertion, args=(sd_drive,)).start()

                except:
                    print("Calling Bullshit on drive " + drive_letter)

    def select_frame_by_name(self, name):
        # set button color forv selected button
        self.home_button.configure(fg_color=("gray75", "gray25") if name == "home" else "transparent")
        self.frame_2_button.configure(fg_color=("gray75", "gray25") if name == "frame_2" else "transparent")
        self.frame_3_button.configure(fg_color=("gray75", "gray25") if name == "frame_3" else "transparent")
        self.frame_4_button.configure(fg_color=("gray75", "gray25") if name == "frame_4" else "transparent")

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
        if name == "frame_4":
            self.fourth_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.fourth_frame.grid_forget()

    def read_logs_to_textframe(self):
        log_path = 'C:/Users/micha/Apps/MapMaker6/map_maker_1_2/ARTAK_MM/LOGS/SessionLog_App_9593566.txt'

    def run_executable(self):
        executable_path = "C:/Program Files/Bentley/iTwin Capture Modeler/bin/iTwinCaptureModelerEngine.exe"
        def read_output():
            process = subprocess.Popen(executable_path, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                       universal_newlines=True)
            while True:

                try:
                    with open(os.getcwd() + "/ARTAK_MM/LOGS/kill.mm", "r"):
                        pass
                    print("Killing Output reader")
                    sys.exit()

                except FileNotFoundError:

                    output = process.stdout.readline()
                    if not output:
                        break
                    self.output_text2.insert(tk.END, output)
                    self.output_text2.see(tk.END)
                    if output == "Error: Product is not permitted to run.":
                        self.open_licensing_tool()
            process.wait()

        # Create a separate thread to read the output
        output_thread = threading.Thread(name='t13', target=read_output)
        output_thread.start()

    def open_licensing_tool(self):
        executable = "C:/ProgramData/Microsoft/Windows/Start Menu/Programs/CONNECTION Client/CONNECTION Client/CONNECTION Client.lnk"
        subprocess.Popen(executable)

    def home_button_event(self):
        self.select_frame_by_name("home")

    def frame_2_button_event(self):
        self.select_frame_by_name("frame_2")

    def frame_3_button_event(self):
        self.select_frame_by_name("frame_3")

    def frame_4_button_event(self):
        self.select_frame_by_name("frame_4")

    def change_appearance_mode_event(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)


class StatusObject:

    def __init__(self, label, image_icon, name_entry_field, progress_bar):
        self.label = label
        self.image_icon = image_icon
        self.name_entry_field = name_entry_field
        self.progress_bar = progress_bar


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


if __name__ == "__main__":

    if os.path.exists("ARTAK_MM/LOGS/pc_type.log"):
        os.remove("ARTAK_MM/LOGS/pc_type.log")

    if os.path.exists("ARTAK_MM/LOGS/status_nr.log"):
        os.remove("ARTAK_MM/LOGS/status_nr.log")

    if os.path.exists("ARTAK_MM/LOGS/t_render.log"):
        os.remove("ARTAK_MM/LOGS/t_render.log")

    app = App()
    # threading.Thread(target=app.sd_card_monitor).start()
    threading.Thread(target=app.job_queue_monitor, name='t1').start()
    threading.Thread(target=app.mm_project_monitor, name='t2').start()
    threading.Thread(target=app.find_folders_with_obj, name='t3').start()
    threading.Thread(target=app.display_activity_on_pc_recon, name='t4').start()
    threading.Thread(target=app.display_activity_on_nr_recon, name='t5').start()
    app.run_executable()
    app.mainloop()
