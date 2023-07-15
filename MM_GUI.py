import win32gui, win32con
'''
This snippet hides the console in non compiled scripts. Done for aesthetics
'''

this_program = win32gui.GetForegroundWindow()
win32gui.ShowWindow(this_program , win32con.SW_HIDE)

import random, psutil
from datetime import datetime
import customtkinter
import os
from PIL import Image
import os

'''
We will create the work folders on first run. This code serves as a check in case the one of the working folders gets
accidentaly deleted.
'''
dirs1 = ['ARTAK_MM/DATA/Raw_Images/UNZIPPED', 'ARTAK_MM/DATA/Raw_Images/ZIP/Completed', 'ARTAK_MM/DATA/Raw_Images/ZIP/New', 'ARTAK_MM/DATA/Raw_Images/ZIP/Unzipping_in_progress', 
         'ARTAK_MM/LOGS', 'ARTAK_MM/POST/Photogrammetry', 'ARTAK_MM/DATA/PointClouds']

#cleanup any straggler status file in case of disgraceful exit of either recon script

if os.path.exists("ARTAK_MM/LOGS/status.log"):
    
    os.remove("ARTAK_MM/LOGS/status.log")
    
for dir in dirs1:
    
    if not os.path.exists(dir):
    
        os.makedirs(dir)
    
    else:
        
        continue  
    
import subprocess
import sys
import time
import threading
import win32file
import MM_image_grouper
import MM_objects
import MM_processing_photogrammetry
import MM_logger
import logging
from tkinter import filedialog
import subprocess
from MM_objects import MapmakerProject
import customtkinter
import tkinter as tk
import jobqueue_monitor_sample
from tkhtmlview import HTMLLabel
from pathlib import Path

customtkinter.set_appearance_mode("Dark")  # Modes: system (default), light, dark
customtkinter.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

sd_drive = ""
# Open RESTful API that RX images from the Ground Control Stations
# subprocess.Popen(["python", "C:/Users/micha/Documents/Coding/Photogrammetry/samples/MM_webserver.py"])

# Open loop to check for zip files placed into a specific folder, usually placed there by the Restful API above
subprocess.Popen(["python", "MM_loop_check_files.py"])

r = random.Random()
session_id = r.randint(1, 10000000)
session_logger = MM_logger.initialize_logger("SessionLog" + str(session_id))
print = session_logger.info

class SdCardInsertionEvent(tk.Event):
    def __init__(self, drive_letter):
        super().__init__()
        self.drive_letter = drive_letter


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
                    print("time =" + str(_time))
        print("file = " + file)
        label = customtkinter.CTkLabel(self, text=_time, image=image, compound="left", padx=5, anchor="w")
        button = customtkinter.CTkButton(self, text="Open", width=100, height=24)
        print ("button command = " + str(button_command))
        print (file)
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
        
        self.session_logger = session_logger
        self.iconbitmap(default = 'gui_images/ARTAK_103.ico')
        self.title("ARTAK Map Maker, by Eolian")
        self.geometry("1080x720")

        # set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # load images with light and dark mode image
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "gui_images")
        self.logo_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "logo_light_scheme.png")),
                                                 dark_image=Image.open(os.path.join(image_path, "logo_dark_scheme.png")),
                                                 size=(100, 33))
        self.large_test_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "large_test_image.png")),
                                                       size=(500, 150))
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

        self.navigation_frame_label = customtkinter.CTkLabel(self.navigation_frame, text="  3D Map Maker",
                                                             image=self.logo_image,
                                                             compound="left",
                                                             font=customtkinter.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

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
        # self.home_frame_large_image_label.grid(row=0, column=0, padx=20, pady=10)
        # add settings for auto process sd card
        self.auto_process_sd = customtkinter.CTkLabel(self.fourth_frame, text="Auto Process SD Card Content?")
        self.auto_process_sd.grid(row=6, column=0, padx=20, pady=10)

        self.auto_process_sd_frame = customtkinter.CTkFrame(self)
        self.auto_process_sd_var = customtkinter.BooleanVar()
        self.auto_process_sd_var.set(value=False)

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
        self.radio_var1_pc = customtkinter.StringVar()
        self.radio_var1_pc.set("leg")
        
        self.obj_radio_button = customtkinter.CTkRadioButton(self.fourth_frame, text="New (Cesium)", variable=self.radio_var1_pc,
                                                             value="ces")
        self.obj_radio_button.grid(row=7, column=1, padx=20, pady=10)

        self.tiles_radio_button2 = customtkinter.CTkRadioButton(self.fourth_frame, text="Legacy (Hololens)", variable=self.radio_var1_pc,
                                                                value="leg")
        self.tiles_radio_button2.grid(row=7, column=2, padx=20, pady=10)  
        
        ###
        
        self.home_frame_server = customtkinter.CTkLabel(self.fourth_frame, text="Select ARTAK Server:")
        self.home_frame_server.grid(row=0, column=0, padx=20, pady=10)

        self.server_button_frame = customtkinter.CTkFrame(self)
        self.server_var = customtkinter.StringVar()
        self.server_var.set("https://esp.eastus2.cloudapp.azure.com/")

        self.cloud_radio_button = customtkinter.CTkRadioButton(self.fourth_frame, text="Cloud", variable=self.server_var,
                                                               value="https://esp.eastus2.cloudapp.azure.com/")
        self.cloud_radio_button.grid(row=0, column=1, padx=20, pady=10)

        self.local_radio_button = customtkinter.CTkRadioButton(self.fourth_frame, text="Local", variable=self.server_var,
                                                               value="https://esp.cluster.local")
        self.local_radio_button.grid(row=0, column=2, padx=20, pady=10)

        self.home_frame_button_4 = customtkinter.CTkLabel(self.fourth_frame, text="Select Map Type:")
        self.home_frame_button_4.grid(row=4, column=0, padx=20, pady=10)
        self.button_frame = customtkinter.CTkFrame(self)
        self.radio_var1 = customtkinter.StringVar()
        self.radio_var1.set("OBJ")

        self.obj_radio_button = customtkinter.CTkRadioButton(self.fourth_frame, text="OBJ", variable=self.radio_var1,
                                                             value="OBJ")
        self.obj_radio_button.grid(row=4, column=1, padx=20, pady=10)

        self.tiles_radio_button2 = customtkinter.CTkRadioButton(self.fourth_frame, text="TILES", variable=self.radio_var1,
                                                                value="TILES")
        self.tiles_radio_button2.grid(row=4, column=2, padx=20, pady=10)

        self.radio_label2 = customtkinter.CTkLabel(self.fourth_frame, text="Delete After Transfer?")
        self.radio_label2.grid(row=5, column=0, padx=20, pady=10)

        self.radio_var2 = customtkinter.StringVar()
        self.radio_var2.set("N")

        self.yes_radio_button = customtkinter.CTkRadioButton(self.fourth_frame, text="N", variable=self.radio_var2,
                                                             value="N")
        self.yes_radio_button.grid(row=5, column=1, padx=20, pady=10)

        self.no_radio_button = customtkinter.CTkRadioButton(self.fourth_frame, text="Y", variable=self.radio_var2,
                                                            value="Y")
        self.no_radio_button.grid(row=5, column=2, padx=20, pady=10)

        self.browse_label = customtkinter.CTkLabel(self.home_frame, text="Select Data Source")
        self.browse_label.grid(row=6, column=0, padx=20, pady=10)

        self.browse_button = customtkinter.CTkButton(self.home_frame, text="Browse", command=self.browse_directory)
        self.browse_button.grid(row=6, column=1, padx=20, pady=10)
        
        self.browse_label_pc = customtkinter.CTkLabel(self.home_frame, text="Process PointCloud")
        self.browse_label_pc.grid(row=8, column=0, padx=20, pady=10)

        self.browse_button_pc = customtkinter.CTkButton(self.home_frame, text="Browse", command=self.gen_pc, state = "normal")
        self.browse_button_pc.grid(row=8, column=1, padx=20, pady=10)  
        
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
        self.apperance_mode_label.grid(row=10, column=0, padx=20, pady=20, sticky="s")

        self.appearance_mode_menu = customtkinter.CTkOptionMenu(self.fourth_frame,
                                                                values=["Light", "Dark", "System"],
                                                                command=self.change_appearance_mode_event)
        self.appearance_mode_menu.grid(row=10, column=1, padx=20, pady=20, sticky="nsew", columnspan=2)
        
        # select default frame
        self.select_frame_by_name("home")
        self.list_of_projects = []
        self.scrollable_label_button_frame = ScrollableLabelButtonFrame(master=self, width=300,
                                                                        command=self.label_button_frame_event,
                                                                        corner_radius=0)
        self.scrollable_label_button_frame.grid(row=0, column=2, padx=0, pady=0, sticky="nsew")
        self.list_of_objs = []

        self.list_of_progress_bars = []
        self.local_server_ip = ""
        self.local_server_label = customtkinter.CTkLabel(self.fourth_frame, text="Local Server IP Address")
        self.local_server_ip = customtkinter.CTkEntry(self.fourth_frame, placeholder_text="http://192.168.10.200")
        self.local_server_label.grid(row=8, column=0, padx=20, pady=10, sticky="ew")
        self.local_server_ip.grid(row=8, column=1, padx=20, pady=10, sticky="ew") 
    
    def add_radio_button_set(self, button_label, button_option1, button_option2):
        print ("WIP")
        
    def open_pc_folder(self):
        
        cmd = os.getcwd()+"/ARTAK_MM/DATA/PointClouds"
        os.startfile(cmd)
        
    def gen_pc(self):
        
        global hr_proc, lr_proc
    
        value = self.radio_var1_pc.get()
        
        if 'leg' in value:
        
            subprocess.Popen(["python", "MM_pc2lr.py"])
        
        else:
            
            subprocess.Popen(["python", "MM_pc2hr.py"])  
            
    def display_activity_on_pc_recon(self):
        
        #will check if recon is running. should it be runing, the 'Browse' button is disabled'
        
        self.progressbar_pc = customtkinter.CTkProgressBar(self.home_frame)        
        
        while True:

            if os.path.exists("ARTAK_MM/LOGS/status.log"):
                
                self.browse_button_pc.configure(state = 'disabled')
                
                self.progressbar_pc.grid(row=8, column=2, padx=20, pady=10, sticky="ew")
                self.progressbar_pc.set(0)
                self.progressbar_pc.start()            
                
            else:
                
                self.browse_button_pc.configure(state = 'normal')
                self.progressbar_pc.stop()
                self.progressbar_pc.configure(mode="determinate", progress_color="green")
                self.progressbar_pc.set(1)
            
            time.sleep(3)
                 
    def browse_directory(self):
        path = filedialog.askdirectory()

        if path:
            print(f"Selected Directory: {path}")
            threading.Thread(target=self.print_sd_card_files, kwargs=({'folder_path': path})).start()

    def check_project_status(self):
        status = self.job_queue_monitor()
        self.home_frame_text = status

    def trigger_photogrammetry(self, each_folder, logger, mm_project=MM_objects.MapmakerProject()):
        mm_project.manually_made_name = "ManualNameTest"
        a = MM_processing_photogrammetry.processing_photogrammetry(each_folder, logger=logger, mm_project=mm_project)
        a.do_photogrammetry()
        self.scrollable_label_button_frame.destroy()
        self.scrollable_label_button_frame = ScrollableLabelButtonFrame(master=self, width=300,
                                                                        command=self.label_button_frame_event,
                                                                        corner_radius=0)
        self.scrollable_label_button_frame.grid(row=0, column=2, padx=0, pady=0, sticky="nsew")
        self.on_project_completed(path=each_folder, mm_project=mm_project)

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
        image_path = os.path.join(os.getcwd()+'/ARTAK_MM/DATA/Raw_Images/UNZIPPED/', path)
        images = os.listdir(image_path)
        row = 0
        column = 0
        number_of_columns = 3
        self.third_frame.destroy()
        self.third_frame = customtkinter.CTkScrollableFrame(self, corner_radius=0, fg_color="transparent")

        for each_image in images:
            try:
                image_payload = customtkinter.CTkImage(Image.open(os.path.join(image_path, each_image)), size=(300,255))
                tk_image = customtkinter.CTkLabel(self.third_frame, image=image_payload, text="")
                tk_image.grid(row=row, column=column, padx=10, pady=10)
                column = column + 1
                if column == number_of_columns:
                    row = row + 1
                    column = 0
            except:
                print("Ignoring JSON File")

    def print_sd_card_files(self, folder_path="", drive_letter=""):

        if drive_letter == "":
            path = folder_path
        if folder_path == "":
            path = drive_letter + ":\\"
        try:
            files = get_image_files(path)
          #  threading.Thread(target=app.add_images_to_page, kwargs={"path":path}).start()
            print(f"(Immage Files on {path}:")
            for file in files:
                print(file)
            folder_name_list = MM_image_grouper.group_images(path, logger=self.session_logger)
            print("Folder name list: " + str(folder_name_list))
            map_type = self.radio_var1.get()
            delete_after = self.radio_var2.get()
            artak_server = self.server_var.get()
            print("Processing Triggered. Map type: " + map_type + " " + "Delete After = " + delete_after)
            print(folder_name_list)
            if delete_after == "Y":
                for f in files:
                    os.remove(path + f)
            if map_type == "OBJ":
                for each_folder in folder_name_list:
                    file_count = len(os.listdir(path))
                    logger = MM_logger.initialize_logger("MMProjectLog_" + each_folder)
                    if self.local_server_ip.get() != "":
                        artak_server = self.local_server_ip.get()
                    new_project = MapmakerProject(name=each_folder, time_first_image=each_folder,
                                                  time_mm_start=time.time(),
                                                  image_folder=each_folder, total_images=file_count, logger=logger,
                                                  artak_server=artak_server)

                    self.list_of_projects.append(new_project)
                    print(new_project.as_dict())
                    threading.Thread(target=self.trigger_photogrammetry,
                                     args=(each_folder, logger, new_project)).start()

                    # send the message that a project has been started
                    self.on_project_started(path=path, mm_project=new_project)
                    
            if map_type == "TILES":
                
                for each_folder in folder_name_list:
                    file_count = len(os.listdir(path))
                    logger = MM_logger.initialize_logger(each_folder)
                    new_project = MapmakerProject(name=each_folder, time_first_image=each_folder,
                                                  time_mm_start=time.time(),
                                                  image_folder=each_folder, total_images=file_count, logger=logger,
                                                  artak_server=artak_server)
                    self.list_of_projects.append(new_project)
                    print(new_project.as_dict())
                    threading.Thread(target=self.trigger_photogrammetry,
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
            que_dict = jobqueue_monitor_sample.main()
            self.output_text3.delete("1.0", tk.END)
            for each_job in que_dict:
                self.output_text3.insert(tk.END, str(each_job) + "\n")
            time.sleep(5)

    def mm_project_monitor(self):
        while True:
            self.home_frame_text.delete("1.0", tk.END)
            self.home_frame_text.insert(tk.END, "Jobs from this Session \n")
            count = 1
            time_fields = ["time_mm_start", "time_processing_start", "time_processing_complete", "time_accepted_by_artak"]
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

    def find_preprocessed_folders_with_obj(self):
        
        previous_file_count = 0
        
        while True:
            
            directory = os.getcwd()+"/ARTAK_MM/POST/Photogrammetry"
            #previous_file_count = 0
            self.list_of_objs = []
            if 1 == 1:
                current_file_count = len(os.listdir(directory))
                if current_file_count != previous_file_count:
                    
                    self.scrollable_label_button_frame.destroy()
                    self.scrollable_label_button_frame = ScrollableLabelButtonFrame(master=self, width=300,
                                                                                            command=self.label_button_frame_event,
                                                                                                corner_radius=0)
                    self.scrollable_label_button_frame.grid(row=0, column=2, padx=0, pady=0, sticky="nsew")    
                    
                    for root, dirs, files in os.walk(directory):
                        if "Preprocessed" in dirs:
                            preprocessed_folder = os.path.join(root, "Preprocessed")
                            obj_files = [file for file in os.listdir(preprocessed_folder) if file.endswith(".obj")]
                            if obj_files:
                                print(f"Found Preprocessed folder with OBJ file(s): {preprocessed_folder}")
                                print("OBJ files:")
                                for obj_file in obj_files:
                                    print(os.path.join(preprocessed_folder, obj_file))
                                self.list_of_objs.append(preprocessed_folder)
                    for each_item in self.list_of_objs:  # add items with images
                        self.scrollable_label_button_frame.add_item(file=each_item, button_command=each_item)               
                    previous_file_count = current_file_count
                    
                time.sleep(5)

    def open_obj(self, path):
        path = os.path.join(path+"/", "Model.obj")
        print ("opening obj" + path)
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

    def on_project_started(self, path, mm_project=MapmakerProject()):
        #path = "C:\ARTAK_MM\POST\Photogrammetry/2023-05-18_14-42-52993\Productions\Production_1\Data\Model\Preprocessed"
        self.project2_label = customtkinter.CTkLabel(self.home_frame, text=mm_project.name)

        self.project2_open_images_icon = customtkinter.CTkButton(self.home_frame,
                                                                 text="View Images",
                                                                 command=lambda: threading.Thread(
                                                                     target=self.add_images_to_page,
                                                                     kwargs={"path": mm_project.name}).start())
        self.project2_open_images_icon.grid(row=len(self.list_of_projects)+9, column=2, padx=20, pady=10)
        self.project2_label.grid(row=len(self.list_of_projects)+9, column=0, padx=20, pady=10)
        e1 = customtkinter.CTkEntry(self.home_frame)
        e1.grid(row=len(self.list_of_projects)+9, column=1, padx=20, pady=10, sticky="ew")
        # project3_edit_name = customtkinter.CTkButton(self.home_frame,
        #                                                          text="Edit Name",
        #                                                          command=lambda: threading.Thread(target=self.add_images_to_page, kwargs={"path":path}).start())
        # project3_edit_name.grid(row=len(self.list_of_projects)+9, column=1, padx=20, pady=10)
        # add progress bar
        self.progressbar_1 = customtkinter.CTkProgressBar(self.home_frame)
        self.progressbar_1.grid(row=len(self.list_of_projects)+9, column=4, padx=20, pady=10, sticky="ew")

        self.progressbar_1.configure(mode="determinate")
        self.progressbar_1.set(0)
        self.progressbar_1.start()

        threading.Thread(target=self.update_name_manually_loop, args=(e1, mm_project)).start()

    def update_name_manually_loop(self, input_field, mm_project):
        while True:
            mm_project.manually_made_name = input_field.get()
            time.sleep(5)
    def on_change_name(self):
        print("on name change")
    def on_project_completed(self, path=None, mm_project=MapmakerProject()):
        #path = "C:\ARTAK_MM\POST\Photogrammetry/2023-05-18_14-42-52993\Productions\Production_1\Data\Model\Preprocessed"
        #threading.Thread(target=app.find_preprocessed_folders_with_obj).start()

        project2_open_map_icon = customtkinter.CTkButton(self.home_frame,
                                                                 text="Open Map",
                                                                 command=lambda: threading.Thread(target=self.open_obj, kwargs={"path":path}).start())
        project2_open_map_icon.grid(row=len(self.list_of_projects)+9, column=3, padx=20, pady=10)

        # add progress bar
        progressbar_1 = customtkinter.CTkProgressBar(self.home_frame)
        progressbar_1.grid(row=len(self.list_of_projects)+9, column=4, padx=20, pady=10, sticky="ew")

        progressbar_1.configure(mode="determinate", progress_color="green")
        progressbar_1.set(1)
        progressbar_1.stop()
#        progressbar_1.destroy()

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

    def frame_4_button_event(self):
        self.select_frame_by_name("frame_4")

    def change_appearance_mode_event(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)


class TextRedirector:
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag

    def write(self, str):
        self.widget.insert(tk.END, str, (self.tag,))
        self.widget.see(tk.END)

    def flush(self):
        pass


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
    app = App()
    threading.Thread(target=app.sd_card_monitor).start()
    threading.Thread(target=app.job_queue_monitor).start()
    threading.Thread(target=app.mm_project_monitor).start()
    threading.Thread(target=app.find_preprocessed_folders_with_obj).start()
    threading.Thread(target=app.display_activity_on_pc_recon).start()
    app.run_executable()
    app.mainloop()
