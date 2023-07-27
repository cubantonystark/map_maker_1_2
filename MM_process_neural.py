'''
Neural Rendering and Surface reconstruction . Version 1.1.
For Enya, John and Willy.
(C) 2022 - 2023, Reynel Rodriguez
All rights reserved.
'''

import os, sys, browsers, glob, subprocess, time, win32ui, glob, psutil, shutil, zipfile, pathlib
from datetime import date, datetime
from tkinter import Tk
from tkinter import filedialog, messagebox

global post_dest_folder, model_dest_folder, mission

class neural_rendering_and_recon():

    def copy_obj_and_compress_into_zip(self, tgt_dir, post_dest_folder, model_dest_folder, mission):

        # Lets move the ortho data files into the folder for compression

        shutil.copy(os.getcwd() + "/configs/metadata.prj", str(tgt_dir)+"/mesh")
        shutil.copy(os.getcwd() + "/configs/metadata.xyz", str(tgt_dir)+"/mesh")

        files = [f for f in glob.glob(str(tgt_dir) + "/mesh/*.*")]

        for file in files:
            if "poisson_mesh.ply" in file:
                pass
            else:
                shutil.copy(file, model_dest_folder+"/")

        os.rename(model_dest_folder+"/mesh.obj", model_dest_folder+"/Model.obj")

        compression = zipfile.ZIP_DEFLATED

        files = [f for f in glob.glob(model_dest_folder + "/*.*")]
        zip_file = str(post_dest_folder)+"/"+str(mission)+'.zip'

        with zipfile.ZipFile(zip_file, mode = "w") as zf:

            for file in files:

                file_to_compress = file.split("/")
                file_to_compress = file_to_compress[-1].split("\\")
                zf.write(file, file_to_compress[-1],compress_type = compression, compresslevel = 9)

        #upload(zip_file, url="https://esp.eastus2.cloudapp.azure.com/")

        return

    def recon(self, tgt_dir, post_dest_folder, model_dest_folder, mission):

        base_dir = os.getcwd()
        tgt_dir = str(tgt_dir)+"/nerfacto"
        tgt_dir = max(pathlib.Path(tgt_dir).glob('*/'), key=os.path.getmtime)
        cmd = "python " + str(base_dir) + "/" + "nerfstudio/nerfstudio/scripts/exporter.py poisson --load-config "+str(tgt_dir)+"/config.yml --output-dir "+str(tgt_dir)+"/mesh"
        os.system(cmd)

        if os.path.exists(base_dir + "/ARTAK_MM/LOGS/status_nr.log"):
            os.remove(base_dir + "/ARTAK_MM/LOGS/status_nr.log")

        self.copy_obj_and_compress_into_zip(tgt_dir, post_dest_folder, model_dest_folder, mission)

        messagebox.showinfo('ARTAK 3D Map Maker', 'Reconstruction complete!\n. Mesh is located in '+str(model_dest_folder))
        sys.exit()

    def WindowExists(self, classname):
        try:
            win32ui.FindWindow(classname, None)
        except win32ui.error:
            return False
        else:
            return True

    def create_t_folder(self, src_dir):

        # we will get the images folder and create a processing folder right above it, then return the
        # image path and the created folder as variables for the data processing part

        src_dir = src_dir.split("/")
        src_dir.pop(len(src_dir)-1)
        tgt_dir = "/".join(src_dir)
        tgt_dir = tgt_dir+"/MM_neural"

        if not os.path.exists(tgt_dir):
            os.mkdir(tgt_dir)

        return tgt_dir

    def write_status(self, stats):

        # This file is the beacon for the progress bar in the GUI
        base_dir = os.getcwd()
        with open(base_dir + "/ARTAK_MM/LOGS/status_nr.log", "w") as status:
            status.write(str(stats))

        return

    def get_target_folder(self):

        # We need a root canvas to be able to display some stuff, this canvas will be hidden though.
        root = Tk()
        root.iconbitmap(default='gui_images/ARTAK_103_drk.ico')
        root.withdraw()

        # Get the source folder
        src_dir = filedialog.askdirectory()
        if len(src_dir) == 0:
            sys.exit()

        today = date.today()
        now = datetime.now()

        mission = "nerf_"+str(today.strftime("%Y-%m-%d"))

        current_time = now.strftime("%H-%M-%S")

        mission = mission+"_"+str(current_time)

        # Derive destination folders for posting from the source folder

        post_dest_folder = "ARTAK_MM/POST/Neural/"+str(mission)+"/Data"

        model_dest_folder = "ARTAK_MM/POST/Neural/"+str(mission)+"/Data/Model"

        if not os.path.exists(post_dest_folder):
            os.makedirs(post_dest_folder)

        if not os.path.exists(model_dest_folder):
            os.makedirs(model_dest_folder)

        # Get the source data folder contents
        base_dir = os.getcwd()
        files = []
        to_process = ""
        files = [f for f in glob.glob(src_dir + "/*.*")]

        try:

            if files[0].endswith(".jpg") or files[0].endswith('.JPG'):
                to_process = "img"
                tgt_dir = self.create_t_folder(src_dir)
                self.process_data(to_process, base_dir, src_dir, tgt_dir, post_dest_folder, model_dest_folder, mission)

            elif files[0].endswith(".png") or files[0].endswith('.PNG'):
                to_process = "img"
                tgt_dir = self.create_t_folder(src_dir)
                self.process_data(to_process, base_dir, src_dir, tgt_dir, post_dest_folder, model_dest_folder, mission)

            elif files[0].endswith(".mp4") or files[0].endswith('.MP4'):
                to_process = "vid"
                tgt_dir = self.create_t_folder(src_dir)
                src_dir = files[0]
                self.process_data(to_process, base_dir, src_dir, tgt_dir, post_dest_folder, model_dest_folder, mission)

            elif "transforms.json" in files[0]:
                tgt_dir = src_dir
                self.train(tgt_dir, base_dir, post_dest_folder, model_dest_folder, mission)

            elif files[0].endswith(".yml") or files[0].endswith('.YML'):
                tgt_dir = files[0]
                self.render(tgt_dir, base_dir, post_dest_folder, model_dest_folder, mission)

            else:
                raise IndexError

        except IndexError:
            messagebox.showerror('ARTAK 3D Map Maker', 'No suitable datasets found.')
            sys.exit()

    def check_for_transforms(self, tgt_dir):

        try:
            with open(tgt_dir+"/transforms.json", "r") as check:
                pass

        except FileNotFoundError:
            self.write_status(stats=0)
            messagebox.showerror('ARTAK 3D Map Maker', 'Dataset could not be successfully processed.')
            sys.exit()

    def process_data(self, to_process, base_dir, src_dir, tgt_dir):
        self.write_status(stats = 1)

        if to_process == "img":
            cmd = "python " + str(base_dir) + "/" + "nerfstudio/nerfstudio/scripts/process_data.py images --data " + str(src_dir) + " --output-dir " + str(tgt_dir)
            stats = 1
            self.write_status(stats)
            os.system(cmd)
            self.check_for_transforms(tgt_dir)
            self.train(tgt_dir, src_dir, post_dest_folder, model_dest_folder, mission)

        if to_process == "vid":
            cmd = "python " + str(base_dir) + "/" + "nerfstudio/nerfstudio/scripts/process_data.py video --data " + str(src_dir) + " --output-dir " + str(tgt_dir)
            stats = 1
            self.write_status(stats)
            os.system(cmd)
            self.check_for_transforms(tgt_dir)
            self.train(tgt_dir, base_dir, post_dest_folder, model_dest_folder, mission)

    def train(self, tgt_dir, base_dir, post_dest_folder, model_dest_folder, mission):

        base_dir = os.getcwd()

        arg1 = str(base_dir)+"/nerfstudio/nerfstudio/scripts/train.py"
        arg2 = "nerfacto"
        arg3 = "--pipeline.model.predict-normals"
        arg4 = "True"
        arg5 = "--data"
        arg6 = str(tgt_dir)
        arg7 = "--experiment-name"
        arg8 = str(mission)
        arg9 = "--output-dir"
        arg10 = str(base_dir)+"/ARTAK_MM/POST/Neural"
        arg11 = "--viewer.quit-on-train-completion"
        arg12 = "True"
        arg13 = "--vis"
        arg14 = "viewer_beta"
        arg15 = "--viewer.websocket-host"
        arg16 = "localhost"
        arg17 = "--max-num-iterations"
        arg18 = "1000"

        a = subprocess.Popen(["python", arg1, arg2, arg3, arg4, arg5, arg6, arg7,arg8, arg9, arg10, arg11, arg12, arg13, arg14, arg15, arg16, arg17, arg18])

        self.write_status(stats = 1)
        time.sleep(5)

        browsers.launch("chrome", url="http://localhost:7007")

        while a.poll() is None:
            self.write_status(stats = 1)
            time.sleep(3)

        a.kill()

        tgt_dir = max(pathlib.Path(arg10).glob('*/'), key=os.path.getmtime)

        self.recon(tgt_dir, post_dest_folder, model_dest_folder, mission)

    def render(self, tgt_dir, base_dir):


        arg1 = str(base_dir)+"/nerfstudio/nerfstudio/scripts/viewer/run_viewer.py"
        arg2 = "--load_config"
        arg3 = str(tgt_dir)
        arg4 = "--vis"
        arg5 = "viewer_beta"
        arg6 = "--viewer.websocket-host"
        arg7 = "localhost"

        b = subprocess.Popen(["python", arg1, arg2, arg3, arg4, arg5, arg6, arg7])

        time.sleep(5)

        vis_url = "http://localhost:7007"
        mycmd = r'start chrome /new-tab {}'.format(vis_url)
        c = subprocess.Popen(mycmd, shell=True)

        def if_process_is_running_by_exename(exename='chrome.exe'):
            for proc in psutil.process_iter(['pid', 'name']):
                # This will check if there exists any process running with executable name
                if proc.info['name'] == exename:
                    running = "yes"
                    return running

            running = "no"
            return running

        time.sleep(5)

        while True:
            running = if_process_is_running_by_exename()
            if running == "yes":
                time.sleep(5)
            else:
                break

        b.kill()
        c.kill()

        sys.exit()

if __name__ == '__main__':
    neural_rendering_and_recon().get_target_folder()
