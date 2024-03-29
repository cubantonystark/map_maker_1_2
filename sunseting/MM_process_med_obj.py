'''
Mesh generation from PointClouds.
Optimized for Cesium Tiling. Version 1.1.
For Enya, John and Willy.
(C) 2022 - 2023, Reynel Rodriguez
All rights reserved.
'''
import open3d as o3d

o3d.utility.set_verbosity_level(o3d.utility.VerbosityLevel.Error)
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

mesh_depth = 12
class meshing():

    def get_PointCloud(self):

        global swap_axis, path, filename, mesh_output_folder, simplified_output_folder, with_texture_output_folder, obj_file, separator, c, log_name, lat, lon, utm_easting, utm_northing, zone, log_name, log_folder, pc_folder, post_dest_folder, model_dest_folder, face_number, designator, folder_type, folder_suffix

        root = Tk()
        root.iconbitmap(default='gui_images/ARTAK_103_drk.ico')
        root.after(1, lambda: root.focus_force())
        root.withdraw()
        fullpath = filedialog.askopenfile(filetypes=(("PointClouds", "*.ply;*.pts;"), ("All files", "*.*")))
        fullpath = str(fullpath)

        with open('ARTAK_MM/LOGS/pc_type.log', 'r') as pc_type:
            pc = pc_type.read()

        if 'hr' in pc:
            face_number = 9500000
            designator = 'hr_'
            folder_type = 'HighRes'
            folder_suffix = '_hr'
        else:
            face_number = 900000
            designator = 'lr_'
            folder_type = 'LowRes'
            folder_suffix = '_lr'

        file_size_pre_edit = 0
        file_size_post_edit = 0

        today = date.today()
        now = datetime.now()
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

        logfilename = filename.replace('.ply', '').replace('.pts', '').replace('.obj', '')
        pc_folder = logfilename
        log_name = designator + filename.replace('.ply', '').replace('.pts', '').replace('.obj', '') + "_" + str(
            d) + "_" + str(ct) + ".log"

        # Derive destination folders from source path
        post_dest_folder = "ARTAK_MM/POST/Med" + separator + designator + pc_folder + separator + "Data"
        model_dest_folder = "ARTAK_MM/POST/Med" + separator + designator + pc_folder + separator + "Data/Model"
        mesh_output_folder = "ARTAK_MM/DATA/Med/"+folder_type + separator + pc_folder + separator + "mesh"+folder_suffix
        simplified_output_folder = "ARTAK_MM/DATA/Med/"+folder_type + separator + pc_folder + separator + "simplified"+folder_suffix
        with_texture_output_folder = "ARTAK_MM/DATA/Med/"+folder_type + separator + pc_folder + separator + "final"+folder_suffix
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

        if "lr_" in designator:
            # Create xyz and prj based on lat and lon provided
            prj_1 = 'PROJCS["WGS 84 / UTM zone '
            prj_2 = '",GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-81],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["Easting",EAST],AXIS["Northing",NORTH],AUTHORITY["EPSG","32617"]]'

            with open(with_texture_output_folder + separator + logfilename + '.xyz', 'w') as xyz:
                xyz.write(str(utm_easting + " " + str(utm_northing) + " " + "101.000"))

            with open(with_texture_output_folder + separator + logfilename + '.prj', 'w') as prj:
                prj.write(str(prj_1) + str(zone) + str(prj_2))

        if ".obj" in filename:
            shutil.copy(fullpath, simplified_output_folder)
            file_size_pre_edit = int(os.path.getsize(fullpath))  # Here we get the file size in bytes.
            shutil.rmtree(mesh_output_folder)
            generated_mesh = fullpath
            swap_axis = 1
            self.mesh_processing(generated_mesh, swap_axis, file_size_pre_edit, file_size_post_edit)

        else:
            swap_axis = 0

        preview = 0

        with open("ARTAK_MM/LOGS/status.log", "w") as status:
            pass

    def mesh_processing(self, generated_mesh, swap_axis):

        try:
            # We will use Meshlab from now on to to handle the processing.
            ms = pymeshlab.MeshSet()
            # logging.info("Loading and Analyzing Mesh.\r")
            message = 'Loading and Analyzing Mesh.'
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
                file_size = int(os.path.getsize(generated_mesh))
                p = pymeshlab.Percentage(10)

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
                    p = pymeshlab.Percentage(10)

                else:
                    t_hold = 0.06
                    p = pymeshlab.Percentage(25)

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

                    p = pymeshlab.Percentage(10)

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

                        t_hold = 0.9
                        p = pymeshlab.Percentage(10)

                    else:
                        t_hold = 0.075
                        p = pymeshlab.Percentage(10)

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
                    ms.load_new_mesh(generated_mesh)
                    # logging.info('Mesh not optimal. Retargeting parameters (2).\r')
                    message = 'Mesh not optimal. Retargeting parameters (2).'
                    self.write_to_log(path, separator, message)
                    boundingbox = ms.current_mesh().bounding_box()
                    diag = boundingbox.diagonal()
                    t_hold = diag / 200
                    p = pymeshlab.Percentage(10)
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
                        t_hold = 1.6
                        p = pymeshlab.Percentage(10)

                    else:
                        t_hold = 0.08
                        p = pymeshlab.Percentage(10)

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

            m = ms.current_mesh()
            v_number = m.vertex_number()
            f_number = m.face_number()
            # logging.info("Initial VC: "+str(v_number)+". Initial FC: "+str(f_number)+".\r")
            message = 'Initial VC: ' + str(v_number) + '. Initial FC: ' + str(f_number) + "."
            self.write_to_log(path, separator, message)
            # Let's take a look at the mesh file to see how big it is. We are constrained to about 120Mb in this case, therefore we
            # will have to decimate if the file is bigger than that number.
            newpath = simplified_output_folder + separator + filename.replace('ply', 'obj').replace('pts', 'obj')

            #if f_number > 6500000:  # Decimate over 6500000 faces (approx.650Mb)
            if f_number > face_number:  # Decimate over 6500000 faces (approx.950Mb)
                self.decimation(ms, newpath, f_number)

            else:
                self.add_texture_and_materials(newpath, swap_axis)

        except MemoryError:
            # logging.info('Error. Not enough Memory to run the process. Quitting.\r')
            message = 'Error. Not enough Memory to run the process. Quitting.'
            self.write_to_log(path, separator, message)
            quit()

    def decimation(self, ms, newpath, f_number):
        # The mesh decimation works best if we take a percentage of faces at a time. We will decimate to target amount
        # of (faces / weight) and save the file, then read the file size and if necessary (over the 185Mb threshold), we will repeat
        # the decimation process again until the resulting mesh meets the file size criteria, we will do this n times (passes).
        m = ms.current_mesh()
        c = 1
        #while f_number > 6500000:
        while f_number > face_number:
            m = ms.current_mesh()
            f_number = m.face_number()
            target_faces = int(f_number / 1.125)
            # logging.info("Target: "+str(int(target_faces))+" F. Iter. "+str(c)+".\r")
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
            # logging.info("Achieved: "+str(f_number)+" F. Ratio ==> "+"%.2f" % abs(ratio)+":1.00.\r")
            message = 'Achieved: ' + str(f_number) + ' F. Ratio ==> ' + '%.2f' % abs(ratio) + ':1.00.'
            self.write_to_log(path, separator, message)
            c += 1

        m = ms.current_mesh()
        f_number = m.face_number()
        v_number = m.vertex_number()

        # logging.info("End VC: "+str(v_number)+". End FC: "+str(f_number)+".\r")
        message = 'End VC: ' + str(v_number) + '. End FC: ' + str(f_number) + "."
        self.write_to_log(path, separator, message)
        newpath = simplified_output_folder + separator + filename.replace('ply', 'obj').replace('pts', 'obj')
        ms.save_current_mesh(newpath,
                             save_vertex_color=True,
                             save_vertex_coord=True,
                             save_vertex_normal=True,
                             save_face_color=False,
                             save_wedge_texcoord=False,
                             save_wedge_normal=False,
                             save_polygonal=False)
        generated_mesh = newpath
        self.add_texture_and_materials(generated_mesh, swap_axis)
    def add_texture_and_materials(self, newpath, swap_axis):
        # This part creates the materials and texture file (.mtl and .png) by getting the texture coordinates from the vertex,
        # tranfering the vertex info to wedges and reating a trivialized texture coordinate from the per wedge info. In the end,
        # we will just extract the texture form the color present at that texture coordinate and thats how we get the texture info into a png
        ms = pymeshlab.MeshSet()
        # logging.info("Loading and Analyzing Mesh.\r")
        message = 'Loading and Analyzing Mesh.'
        self.write_to_log(path, separator, message)
        ms.load_new_mesh(newpath)
        # logging.info("Extracting Texture and Materials.\n")
        message = 'Generating Texture and Materials.'
        self.write_to_log(path, separator, message)
        ms.load_new_mesh(newpath)
        if swap_axis == 1:
            # logging.info("Correcting Axis.\r")
            message = 'Correcting Axis.'
            self.write_to_log(path, separator, message)
            ms.apply_filter('compute_matrix_from_rotation',
                            rotaxis=0,
                            rotcenter=0,
                            angle=90,
                            snapflag=False,
                            snapangle=30,
                            freeze=True,
                            alllayers=False)

        ms.apply_filter('compute_texcoord_parametrization_triangle_trivial_per_wedge',
                        sidedim=0,
                        textdim=10240,
                        border=1,
                        method='Space-optimizing')
        newpath_texturized = with_texture_output_folder + separator + filename.replace('ply', 'obj').replace('pts',
                                                                                                             'obj')
        ms.save_current_mesh(newpath_texturized,
                             save_vertex_color=True,
                             save_vertex_coord=True,
                             save_vertex_normal=True,
                             save_face_color=True,
                             save_wedge_texcoord=True,
                             save_wedge_normal=True,
                             save_polygonal=False)

        ms.load_new_mesh(newpath_texturized)
        newfile = filename.replace('.obj', '').replace('.pts', '').replace('.ply', '')
        ms.apply_filter('compute_texmap_from_color',
                        textname=newfile,
                        textw=10240,
                        texth=10240,
                        overwrite=False,
                        pullpush=True)

        ms.save_current_mesh(newpath_texturized,
                             save_vertex_color=True,
                             save_vertex_coord=False,
                             save_vertex_normal=False,
                             save_face_color=False,
                             save_wedge_texcoord=True,
                             save_wedge_normal=True,
                             save_polygonal=False)

        # We need to compress the texture file
        img = Image.open(newpath_texturized.replace('.obj', '.png'))
        img = img.convert("P", palette=Image.WEB, colors=256)
        img.save(newpath_texturized.replace('.obj', '.png'), optimize=True)


        # Let's compress
        self.compress_into_zip(with_texture_output_folder, newpath)
        files = [f for f in glob.glob(with_texture_output_folder + "/*.zip")]
        for file in files:
            shutil.copy(file, post_dest_folder)

        # copy the obj to the post folder
        shutil.copy(newpath_texturized, model_dest_folder + "/Model.obj")

        messagebox.showinfo('ARTAK 3D Map Maker', 'Reconstruction Complete.')
        # logging.info('Process complete.\r')
        message = 'Reconstruction Complete.'

        with open(log_folder + "/status.log", "w") as status:
            status.write("done")
        time.sleep(2)

        os.remove(log_folder + "/status.log")

        # Once done, we will cleanup
        try:
            shutil.rmtree("ARTAK_MM/DATA/PointClouds/" + folder_type + separator + pc_folder)
            # Remove the status flag for MM_GUI progressbar
            os.remove(log_folder + "/status.log")
        except FileNotFoundError:
            pass

        stats = "done"
        self.write_to_log(stats)
        time.sleep(2)
        sys.exit()

    def compress_into_zip(self, with_texture_output_folder, newpath):
        if 'lr_' in designator:
            extensions = ['.obj', '.obj.mtl', '.png', '.xyz', '.prj']
        else:
            extensions = ['.obj', '.obj.mtl', '.png']
        compression = zipfile.ZIP_DEFLATED
        zip_file = with_texture_output_folder + separator + designator+ filename.replace('.obj', '').replace('.ply',
                                                                                                         '').replace(
            '.pts', '') + '.zip'
        with zipfile.ZipFile(zip_file, mode="w") as zf:
            for ext in extensions:
                try:
                    zf.write(with_texture_output_folder + separator + filename.replace('.obj', '').replace('.ply',
                                                                                                           '').replace(
                        '.pts', '') + ext, filename.replace('.obj', '').replace('.ply', '').replace('.pts', '') + ext,
                             compress_type=compression, compresslevel=9)
                except FileExistsError:
                    pass
                except FileNotFoundError:
                    pass
        return
    def visualize(self, target, message):
        # This is the preview step
        o3d.visualization.draw_geometries([target],
                                          window_name=str(message),
                                          width=1280,
                                          height=900,
                                          zoom=0.32000000000000001,
                                          front=[-0.34267508672450531, 0.89966482743414444, 0.27051244558475285],
                                          lookat=[-15.934802105738544, -4.9954584521228949, 1.4543439424505489],
                                          up=[0.095768108125702828, -0.25299355589613992, 0.96271632900925208])
        return
    def write_to_log(self, path, separator, message):
        with open(log_folder + log_name, "a+") as log:
            log.write(message + "\r")
        return

if __name__ == '__main__':
    meshing().get_PointCloud()