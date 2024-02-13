'''
Mesh generation from PointClouds.
For Enya, John and Willy.
(C) 2022 - 2024, Reynel Rodriguez
All rights reserved.
'''

import open3d as o3d

o3d.utility.set_verbosity_level(o3d.utility.VerbosityLevel.Debug)
o3d.utility.set_verbosity_level(o3d.utility.VerbosityLevel.Debug)

import pymeshlab
from datetime import date, datetime
from PIL import Image
import os, platform, shutil, zipfile, logging, sys, glob, utm, time
from tkinter import Tk
from tkinter import filedialog, messagebox

Image.MAX_IMAGE_PIXELS = None

level = logging.INFO
format = '%(message)s'
handlers = [logging.StreamHandler()]
logging.basicConfig(level=level, format='%(asctime)s \033[1;34;40m%(levelname)-8s \033[1;37;40m%(message)s',
                    datefmt='%H:%M:%S', handlers=handlers)

o3d.utility.set_verbosity_level(o3d.utility.VerbosityLevel.Error)

mesh_depth = 12

class meshing():

    def __init__(self, _mm_project, logger):
        self.mm_project = _mm_project
        self.logger = logger
    def load_e57(self, e57path):

        mesh_depth= 11
        ms = pymeshlab.MeshSet()
        ms.load_new_mesh(e57path)
        fullpath = e57path.replace("e57", "ply")

        ms.save_current_mesh(fullpath,
                             save_vertex_color=True,
                             save_vertex_coord=True,
                             save_vertex_normal=True,
                             save_face_color=True,
                             save_wedge_texcoord=True,
                             save_wedge_normal=True)

        return fullpath, mesh_depth

    def attempt_nksr(self, filename, fullpath, mesh_output_folder):

        shutil.copy(fullpath, '\\\wsl.localhost\\Ubuntu-22.04\\home\\mapmaker\\fsrpc_mapmaker\\pointclouds\\'+filename)
        cmd = 'wsl --user mapmaker --cd /home/mapmaker/fsrpc_mapmaker'
        os.system(cmd)
        return

    def get_PointCloud(self, fullpath, gpu):

        self.logger.info("Method Called: get_PointCloud")

        global path, filename, mesh_output_folder, simplified_output_folder, with_texture_output_folder, obj_file, separator, c, log_name, lat, lon, utm_easting, utm_northing, zone, log_name, log_folder, pc_folder, post_dest_folder, model_dest_folder, face_number, designator, folder_type, folder_suffix

        root = Tk()
        root.iconbitmap(default='gui_images/ARTAK_103_drk.ico')
        root.after(1, lambda: root.focus_force())
        root.withdraw()

        with open('ARTAK_MM/LOGS/pc_type.log', 'r') as pc_type:
            pc = pc_type.read()

        if 'hr' in pc:
            face_number = 3500000
            designator = 'hr_'
            folder_type = 'HighRes'
            folder_suffix = '_hr'
            texture_size = 20480

        else:
            face_number = 100000
            designator = 'lr_'
            folder_type = 'LowRes'
            folder_suffix = '_lr'
            texture_size = 8192

        today = date.today()
        now = datetime.now()
        self.mm_project.set_time_processing_start(time.time())
        d = today.strftime("%d%m%Y")
        ct = now.strftime("%H%M%S")

        if platform.system == 'Windows':
            separator = '\\'
        else:
            separator = '/'

        # Define o3d data object to handle PointCloud
        ply_point_cloud = o3d.data.PLYPointCloud()

        lat = "0"
        lon = "0"

        # We will encode the lat and lon into utm compliant coordinates for the xyz file and retrieve the utm zone for the prj file

        utm_easting, utm_northing, zone, zone_letter = utm.from_latlon(float(lat), float(lon))
        utm_easting = "%.2f" % utm_easting
        utm_northing = "%.2f" % utm_northing

        # Separate source path from filename
        path, filename = os.path.split(fullpath)
        path = path.replace("<_io.TextIOWrapper name='", '')
        filename = filename.replace("' mode='r' encoding='cp1252'>", '')

        fullpath = path + separator + filename

        if 'None' in fullpath:
            quit()

        with open("ARTAK_MM/LOGS/status.log", "w") as status:
            pass

        if '.e57' in fullpath:

            self.logger.info("Converting to PLY")
            fullpath, mesh_depth = self.load_e57(fullpath)

        path, filename = os.path.split(fullpath)

        logfilename = filename.replace('.ply', '').replace('.pts', '').replace('.obj', '').replace('.e57', '')
        pc_folder = logfilename
        log_name = filename.replace('.ply', '').replace('.pts', '').replace('.obj', '').replace('.e57', '') + "_" + str(
            d) + "_" + str(ct) + ".log"

        # Derive destination folders from source path
        post_dest_folder = "ARTAK_MM/POST/Lidar" + separator + pc_folder + separator + "Data"
        model_dest_folder = "ARTAK_MM/POST/Lidar" + separator + pc_folder + separator + "Data/Model"
        mesh_output_folder = "ARTAK_MM/DATA/PointClouds/"+folder_type + separator + pc_folder + separator + "mesh"+folder_suffix
        simplified_output_folder = "ARTAK_MM/DATA/PointClouds/"+folder_type + separator + pc_folder + separator + "simplified"+folder_suffix
        with_texture_output_folder = "ARTAK_MM/DATA/PointClouds/"+folder_type + separator + pc_folder + separator + "final"+folder_suffix
        log_folder = "ARTAK_MM/LOGS/"

        # Create directories within the source folder if they dont exist
        if not os.path.exists(mesh_output_folder):
            os.makedirs(mesh_output_folder)
        if not os.path.exists(simplified_output_folder):
            os.makedirs(simplified_output_folder, mode=777)
        if not os.path.exists(with_texture_output_folder):
            os.makedirs(with_texture_output_folder, mode=777)
        if not os.path.exists(post_dest_folder):
            os.makedirs(post_dest_folder, mode=777)
        if not os.path.exists(model_dest_folder):
            os.makedirs(model_dest_folder, mode=777)

        try:

            with open(log_folder + "gpu_status.txt") as msg:

                stat = msg.readline()
                stat = stat.strip()

            os.remove(log_folder + "/gpu_status.txt")

        except FileNotFoundError:

            stat = ""

        if gpu == 'y':

            self.logger.info("Attempting GPU accelerated Reconstruction")
            self.logger.info("Loading PointCloud")

            self.attempt_nksr(filename, fullpath, mesh_output_folder)

            cmd = 'taskkill /im wsl.exe /F'
            os.system(cmd)

            if 'gpu_success' in stat:

                try:

                    # Remove the status flag for MM_GUI progressbar
                    shutil.rmtree("ARTAK_MM/DATA/PointClouds/" + folder_type + separator + pc_folder)

                except FileNotFoundError:
                    pass

                with open(log_folder + "/status.log", "w") as status:
                    status.write("done")
                time.sleep(2)
                os.remove(log_folder + "/status.log")

                messagebox.showinfo('ARTAK 3D Map Maker', 'Reconstruction Complete.')
                message = 'Reconstruction Complete.'
                self.logger.info(message)
                model_path = model_dest_folder
                self.logger.info("File to upload: ",self.mm_project.name + model_path + self.mm_project.name + ".zip")
                self.logger.info(message)
                self.write_to_log(path, separator, message)
                self.mm_project.set_completed_file_path(model_path)
                self.mm_project.set_completed_file_path(os.path.join(os.getcwd(), model_path))
                self.mm_project.set_zip_payload_location(os.path.join(os.getcwd(), model_path))
                #self.mm_project.name + model_path + self.mm_project.name + ".zip"
                return

        else:

            if 'gpu_fail' in stat:

                self.logger.info("This PointCloud is not suitable for GPU Reconstruction. Switching to CPU.")

            if "lr_" in designator:
                # Create xyz and prj based on lat and lon provided
                prj_1 = 'PROJCS["WGS 84 / UTM zone '
                prj_2 = '",GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-81],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["Easting",EAST],AXIS["Northing",NORTH],AUTHORITY["EPSG","32617"]]'

                with open(with_texture_output_folder + separator + logfilename + '.xyz', 'w') as xyz:
                    xyz.write(str(utm_easting + " " + str(utm_northing) + " " + "101.000"))

                with open(with_texture_output_folder + separator + logfilename + '.prj', 'w') as prj:
                    prj.write(str(prj_1) + str(zone) + str(prj_2))

            try:

                with open(with_texture_output_folder + separator + logfilename+'/', 'r') as msg:
                    pass

            except FileNotFoundError:
                pass

            #logging.info('Loading PointCloud.\r')
            #self.logger.info("Loading PointCloud")
            message = 'Loading PointCloud. ' + str(fullpath)
            self.write_to_log(path, separator, message)
            self.logger.info("fixn to do o3d.io.read")
            pcd = o3d.io.read_point_cloud(fullpath)
            self.logger.info("done o3dioread")
            message = str(pcd)
            self.write_to_log(path, separator, message)
            self.downsample(pcd, texture_size)

    def downsample(self, pcd, texture_size):
        # We need to downsample the PointCloud to make it less dense and easier to work with
        # logging.info("Downsampling.\r")
        message = str(pcd)
        self.logger.info(message)
        self.logger.info('Downsampling.')
        downpcd = pcd.voxel_down_sample(voxel_size = 0.02)
        # logging.info(str(downpcd)+"\r")
        message = str(downpcd)
        self.logger.info(message)
        self.write_to_log(path, separator, message)
        self.compute_normals_and_generate_mesh(downpcd, mesh_depth, texture_size)

    def compute_normals_and_generate_mesh(self, downpcd, mesh_depth, texture_size):

        # Since some PointClouds don't include normals information (needed for texture and color extraction) we will have to calculate it.
        # logging.info("Computing Normals.\r")
        message = 'Computing Normals.'
        self.logger.info(message)
        self.write_to_log(path, separator, message)
        downpcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))

        # logging.info('Generating Mesh.\r')
        message = 'Generating Mesh.'
        self.logger.info(message)
        self.write_to_log(path, separator, message)

        mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(downpcd, depth=mesh_depth, width=0, scale=1.1,
                                                                         linear_fit=False)[0]
        generated_mesh = mesh_output_folder + separator + filename.replace('ply', 'obj').replace('pts', 'obj')

        # logging.info("Exporting Mesh.\r")
        o3d.io.write_triangle_mesh(generated_mesh,
                                   mesh,
                                   write_ascii=False,
                                   compressed=True,
                                   write_vertex_normals=True,
                                   write_vertex_colors=True,
                                   write_triangle_uvs=True,
                                   print_progress=False)

        message = 'Exporting Mesh'
        self.logger.info(message)
        self.write_to_log(path, separator, message)
        mesh_file_size = int(os.path.getsize(generated_mesh))

        if mesh_file_size > 6000000000:
            mesh_depth = 11
            # logging.info("Mesh is not memory friedly. Retrying with safer parameters.\r")
            message = 'Mesh is not memory friedly. Retrying with safer parameters.'
            self.write_to_log(path, separator, message)
            self.logger.info(message)
            self.compute_normals_and_generate_mesh(downpcd, mesh_depth, texture_size)

        else:
            self.mesh_processing(generated_mesh, texture_size)

    def mesh_processing(self, generated_mesh, texture_size):

        try:
            # We will use Meshlab from now on to to handle the processing.
            ms = pymeshlab.MeshSet()
            # logging.info("Loading and Analyzing Mesh.\r")
            message = 'Analyzing Mesh.'
            self.write_to_log(path, separator, message)
            ms.load_new_mesh(generated_mesh)

            try:
                # In order to get closer to the usable faces as much as possible, we will calculate the unusable face edge legth by dividing the
                # mesh diagonal bounding box mesurement by 200. This is the value that meshlab uses as a default on its filter.
                # Caveat: If the object was edited too much (The total manually removed faces is higher than 25% of the entire bounding box), the bounding box method to determine
                # the face length will bee too much, therefore, we will have to use an arbitrary static value; we have found that 1.6 works well.

                boundingbox = ms.current_mesh().bounding_box()
                diag = boundingbox.diagonal()

                t_hold = diag / 200

                p = pymeshlab.PercentageValue(25)

                # logging.info('Refining.\r')
                message = 'Refining'
                self.write_to_log(path, separator, message)
                # We will select faces that are long based on the bounding box calculation and then remove them
                ms.apply_filter('compute_selection_by_edge_length',
                                threshold=t_hold)
                ms.apply_filter('meshing_remove_selected_faces')
                # The selection process and removal of long faces will create floaters, we will remove isolated faces
                ms.apply_filter('meshing_remove_connected_component_by_diameter',
                                mincomponentdiag=p)
                # if this is a generated file from exyn sensors, then we need to use 'safe' values different from the leica ones.

                if ".ply" in filename:
                    t_hold = 0.1

                elif ".pts" in filename:
                    t_hold = 0.09

                else:
                    t_hold = 0.1

                # Since there will still be some long faces, we will mark them and remove them, this time applying a 0.06 thershold. This is

                ms.apply_filter('compute_selection_by_edge_length',
                                threshold=t_hold)
                ms.apply_filter('meshing_remove_selected_faces')

                # Then we remove any isolated faces (floaters) that might still be laying around
                ms.apply_filter('meshing_remove_connected_component_by_diameter',
                                mincomponentdiag=p)
                # logging.info("Exporting Mesh.")
                message = 'Exporting Mesh.'
                self.write_to_log(path, separator, message)

                newpath = simplified_output_folder + separator + filename.replace('ply', 'obj').replace('pts', 'obj')

                ms.save_current_mesh(newpath,
                                     save_vertex_color=True,
                                     save_vertex_coord=True,
                                     save_vertex_normal=True,
                                     save_face_color=True,
                                     save_wedge_texcoord=True,
                                     save_wedge_normal=True,
                                     save_polygonal=True)

            except pymeshlab.pmeshlab.PyMeshLabException:

                try:

                    ms.load_new_mesh(generated_mesh)
                    # logging.info('Mesh not optimal. Retargeting parameters (1).\r')
                    message = 'Mesh not optimal. Retargeting parameters (1).'
                    self.write_to_log(path, separator, message)

                    boundingbox = ms.current_mesh().bounding_box()
                    diag = boundingbox.diagonal()
                    t_hold = diag / 200

                    p = pymeshlab.PercentageValue(10)

                    # logging.info('Refining.\r')
                    message = 'Refining'
                    self.write_to_log(path, separator, message)

                    # We will select faces that are long based on the bounding box calculation and then remove them
                    ms.apply_filter('compute_selection_by_edge_length',
                                    threshold=t_hold)
                    ms.apply_filter('meshing_remove_selected_faces')

                    # The selection process and removal of long faces will create floaters, we will remove isolated faces
                    ms.apply_filter('meshing_remove_connected_component_by_diameter',
                                    mincomponentdiag=p)

                    if ".ply" in filename:
                        t_hold = 0.3

                    elif ".pts" in filename:
                        t_hold = 0.095

                    else:
                        t_hold = 0.3

                    # Since there will still be some long faces, we will mark them and remove them, this time applying a 0.06 thershold. This is
                    ms.apply_filter('compute_selection_by_edge_length',
                                    threshold=t_hold)
                    ms.apply_filter('meshing_remove_selected_faces')

                    # Then we remove any isolated faces (floaters) that might still be laying around
                    ms.apply_filter('meshing_remove_connected_component_by_diameter',
                                    mincomponentdiag = p)

                    message = 'Exporting Mesh.'
                    self.write_to_log(path, separator, message)
                    newpath = simplified_output_folder + separator + filename.replace('ply', 'obj').replace('pts',
                                                                                                            'obj')

                    ms.save_current_mesh(newpath,
                                         save_vertex_color=True,
                                         save_vertex_coord=True,
                                         save_vertex_normal=True,
                                         save_face_color=True,
                                         save_wedge_texcoord=True,
                                         save_wedge_normal=True,
                                         save_polygonal=True)

                except pymeshlab.pmeshlab.PyMeshLabException:

                    try:

                        ms.load_new_mesh(generated_mesh)
                        # logging.info('Mesh not optimal. Retargeting parameters (2).\r')
                        message = 'Mesh not optimal. Retargeting parameters (2).'
                        self.write_to_log(path, separator, message)
                        boundingbox = ms.current_mesh().bounding_box()
                        diag = boundingbox.diagonal()
                        t_hold = diag / 200
                        p = pymeshlab.PercentageValue(10)
                        # logging.info('Refining.\r')
                        message = 'Refining'
                        self.write_to_log(path, separator, message)
                        # We will select faces that are long based on the bounding box calculation and then remove them
                        ms.apply_filter('compute_selection_by_edge_length',
                                        threshold=t_hold)
                        ms.apply_filter('meshing_remove_selected_faces')

                        # The selection process and removal of long faces will reate floaters, we will remove isolated faces
                        ms.apply_filter('meshing_remove_connected_component_by_diameter',
                                        mincomponentdiag=p)

                        if ".ply" in filename:
                            t_hold = 0.6

                        elif ".pts" in filename:
                            t_hold = 0.099

                        else:
                            t_hold = 0.6

                        # Since there will still be some long faces, we will mark them and remove them, this time applying a 0.06 thershold. This is
                        ms.apply_filter('compute_selection_by_edge_length',
                                        threshold=t_hold)
                        ms.apply_filter('meshing_remove_selected_faces')
                        # Then we remove any isolated faces (floaters) that might still be laying around
                        ms.apply_filter('meshing_remove_connected_component_by_diameter',
                                        mincomponentdiag=p)
                        # logging.info("Exporting Mesh.")
                        message = 'Exporting Mesh.'
                        self.write_to_log(path, separator, message)

                        newpath = simplified_output_folder + separator + filename.replace('ply', 'obj').replace('pts',
                                                                                                                'obj')

                        ms.save_current_mesh(newpath,
                                             save_vertex_color=True,
                                             save_vertex_coord=True,
                                             save_vertex_normal=True,
                                             save_face_color=True,
                                             save_wedge_texcoord=True,
                                             save_wedge_normal=True,
                                             save_polygonal=True)

                    except pymeshlab.pmeshlab.PyMeshLabException:

                        # Cleanup

                        print("Folder: ARTAK_MM/DATA/PointClouds/" + folder_type + separator + pc_folder)

                        try:
                            shutil.rmtree("ARTAK_MM/DATA/PointClouds/" + folder_type + separator + pc_folder)
                            # Remove the status flag for MM_GUI progressbar
                        except FileNotFoundError:
                            pass

                        with open(log_folder + "/status.log", "w") as status:
                            status.write("done")
                        time.sleep(2)
                        os.remove(log_folder + "/status.log")

                        # Announce error and terminate.

                        messagebox.showerror('ARTAK 3D Map Maker', 'Could not compute Mesh from PointCloud. Aborting.')
                        logging.info('Process complete.\r')
                        message = 'Could not compute Mesh from PointCloud. Aborting.'
                        self.write_to_log(path, separator, message)
                        return

            m = ms.current_mesh()
            v_number = m.vertex_number()
            f_number = m.face_number()
            logging.info("Initial VC: "+str(v_number)+". Initial FC: "+str(f_number)+".\r")
            message = 'Initial VC: ' + str(v_number) + '. Initial FC: ' + str(f_number) + "."
            self.write_to_log(path, separator, message)
            # Let's take a look at the mesh file to see how big it is. We are constrained to about 120Mb in this case, therefore we
            # will have to decimate if the file is bigger than that number.

            # if f_number > 6500000:  # Decimate over 6500000 faces (approx.650Mb)
            if f_number > face_number:  # Decimate over 6500000 faces (approx.950Mb)
                self.decimation(ms, newpath, f_number, texture_size)

            else:
                self.add_texture_and_materials(newpath, texture_size)

        except MemoryError:
            logging.info('Error. Not enough Memory to run the process. Quitting.\r')
            message = 'Error. Not enough Memory to run the process. Quitting.'
            self.write_to_log(path, separator, message)
            quit()

    def decimation(self, ms, newpath, f_number, texture_size):
        # The mesh decimation works best if we take a percentage of faces at a time. We will decimate to target amount
        # of (faces / weight) and save the file, then read the file size and if necessary (over the 185Mb threshold), we will repeat
        # the decimation process again until the resulting mesh meets the file size criteria, we will do this n times (passes).
        m = ms.current_mesh()
        c = 1
        # while f_number > 6500000:
        while f_number > face_number:
            m = ms.current_mesh()
            f_number = m.face_number()
            # target_faces = int(f_number / 1.125)
            target_faces = int(f_number / 1.5)
            logging.info("Target: "+str(int(target_faces))+" F. Iter. "+str(c)+".\r")
            message = "Target: " + str(int(target_faces)) + " F. Iter. " + str(c) + "."
            self.write_to_log(path, separator, message)
            ms.apply_filter('meshing_decimation_quadric_edge_collapse',
                            targetfacenum=int(target_faces), targetperc=0,
                            qualitythr=0.3,
                            optimalplacement=True,
                            preservenormal=True,
                            autoclean=True)
            f_number = m.face_number()
            v_number = m.vertex_number()
            ratio = (
                            abs(target_faces / f_number) - 1.1) * 10  # Efficiency ratio. resulting amt faces vs target amt of faces
            logging.info("Achieved: "+str(f_number)+" F. Ratio ==> "+"%.2f" % abs(ratio)+":1.00.\r")
            message = 'Achieved: ' + str(f_number) + ' F. Ratio ==> ' + '%.2f' % abs(ratio) + ':1.00.'
            self.write_to_log(path, separator, message)
            c += 1

        m = ms.current_mesh()
        f_number = m.face_number()
        v_number = m.vertex_number()

        logging.info("End VC: "+str(v_number)+". End FC: "+str(f_number)+".\r")
        message = 'End VC: ' + str(v_number) + '. End FC: ' + str(f_number) + "."
        self.write_to_log(path, separator, message)

        newpath1 = simplified_output_folder + separator + 'decimated_' + filename.replace('ply', 'obj').replace(
            'pts',
            'obj')

        ms.save_current_mesh(newpath1,
                             save_vertex_color=True,
                             save_vertex_coord=True,
                             save_vertex_normal=True,
                             save_face_color=False,
                             save_wedge_texcoord=False,
                             save_wedge_normal=False,
                             save_polygonal=False)

        self.add_texture_and_materials(newpath, newpath1, texture_size)
    def add_texture_and_materials(self, newpath, newpath1, texture_size):

        # This part creates the materials and texture file (.mtl and .png) by getting the texture coordinates from the vertex,
        # tranfering the vertex info to wedges and reating a trivialized texture coordinate from the per wedge info. In the end,
        # we will just extract the texture form the color present at that texture coordinate and thats how we get the texture info into a png

        ms = pymeshlab.MeshSet()

        # logging.info("Loading and Analyzing Mesh.\r")
        message = 'Analyzing Mesh.'
        self.logger.info(message)
        self.write_to_log(path, separator, message)

        # logging.info("Extracting Texture and Materials.\n")
        message = 'Generating Texture and Materials.'
        self.logger.info(message)
        self.write_to_log(path, separator, message)

        ms.load_new_mesh(newpath)
        ms.load_new_mesh(newpath1)

        print("Parametrization with "+str(texture_size))

        ms.apply_filter('compute_texcoord_parametrization_triangle_trivial_per_wedge',
                        sidedim = 0,
                        textdim = texture_size,
                        border = 3,
                        method = 'Basic')

        percentage = pymeshlab.PercentageValue(2)

        newpath_texturized = with_texture_output_folder + separator + filename.replace('ply', 'obj').replace('pts','obj').replace('decimated_', '')

        model_path = model_dest_folder + separator + 'Model.obj'

        #Here we transfer the texture
        ms.apply_filter('transfer_attributes_to_texture_per_vertex',
                         sourcemesh = 0,
                         targetmesh  = 1,
                         attributeenum = 0,
                         upperbound = percentage,
                         textname = 'texture.png',
                         textw = texture_size,
                         texth = texture_size,
                         overwrite = False,
                         pullpush = True)

        ms.save_current_mesh(newpath_texturized,
                             save_vertex_color = False,
                             save_vertex_coord = False,
                             save_vertex_normal = False,
                             save_face_color = True,
                             save_wedge_texcoord = True,
                             save_wedge_normal = True,
                             save_polygonal = False)

        ms.save_current_mesh(model_path,
                             save_vertex_color = False,
                             save_vertex_coord = False,
                             save_vertex_normal = False,
                             save_face_color = True,
                             save_wedge_texcoord = True,
                             save_wedge_normal = True,
                             save_polygonal = False)

        # We need to compress the texture file
        img = Image.open(with_texture_output_folder + separator + 'texture.png')
        img = img.convert("P", palette=Image.WEB, colors = 256)
        img.save(with_texture_output_folder + separator + 'texture.png', optimize=True)

        # Let's compress
        self.compress_into_zip(with_texture_output_folder, newpath)
        files = [f for f in glob.glob(with_texture_output_folder + "/*.zip")]
        for file in files:
            shutil.copy(file, post_dest_folder)

        # Cleanup
        print("Folder: ARTAK_MM/DATA/PointClouds/" + folder_type + separator + pc_folder)
        try:
            shutil.rmtree("ARTAK_MM/DATA/PointClouds/" + folder_type + separator + pc_folder)
            # Remove the status flag for MM_GUI progressbar
        except FileNotFoundError:
            pass

        with open(log_folder + "/status.log", "w") as status:
            status.write("done")
        time.sleep(2)
        os.remove(log_folder + "/status.log")

        messagebox.showinfo('ARTAK 3D Map Maker', 'Reconstruction Complete.')
        # logging.info('Process complete.\r')
        message = 'Reconstruction Complete.'
        model_path = model_dest_folder
        self.logger.info(message)
        self.write_to_log(path, separator, message)
        self.mm_project.set_completed_file_path(model_path)
        self.mm_project.set_completed_file_path(os.path.join(os.getcwd(), model_path))
        self.mm_project.set_zip_payload_location(os.path.join(os.getcwd(), model_path))
        #self.mm_project.name + model_path + self.mm_project.name + ".zip"
        return

    def compress_into_zip(self, with_texture_output_folder, newpath):

        if 'lr_' in designator:
            extensions = ['.obj', '.obj.mtl', '.xyz', '.prj']
        else:
            extensions = ['.obj', '.obj.mtl', '.png']

        compression = zipfile.ZIP_DEFLATED
        zip_file = with_texture_output_folder + separator + filename.replace('.obj', '').replace('.ply',
                                                                                                         '').replace(
            '.pts', '') + '.zip'
        with zipfile.ZipFile(zip_file, mode="w") as zf:
            for ext in extensions:
                try:
                    zf.write(with_texture_output_folder + separator + filename.replace('.obj', '').replace('.ply','').replace('.pts', '') + ext, filename.replace('.obj', '').replace('.ply', '').replace('.pts', '') + ext,
                             compress_type = compression, compresslevel = 9)
                except FileExistsError:
                    pass
                except FileNotFoundError:
                    pass
            zf.write(with_texture_output_folder + separator + 'texture.png', 'texture.png', compress_type = compression, compresslevel = 9)
        message = "Compression complete. Compressed_file: " + str(zip_file)
        self.logger.info(message)

        return

    def write_to_log(self, path, separator, message):

        with open(log_folder + log_name, "a+") as log:
            log.write(message + "\r")
        return
