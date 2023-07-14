'''
Mesh generation from PointClouds.
Optimized for Cesium Tiling. Version 1.1.
For Enya, John and Willy.
(C) 2022 - 2023, Reynel Rodriguez
All rights reserved.
Compile with pyinstaller --onefile cesium.py  --collect-all=pymeshlab --collect-all=open3d
'''
import open3d as o3d
o3d.utility.set_verbosity_level(o3d.utility.VerbosityLevel.Error)
import pymeshlab
from datetime import date, datetime
from PIL import Image
import os, platform, shutil, zipfile, logging, sys, glob
from tkinter import Tk
from tkinter import filedialog, messagebox

Image.MAX_IMAGE_PIXELS = None

level    = logging.INFO
format   = '%(message)s'
handlers = [logging.StreamHandler()]
logging.basicConfig(level = level, format='%(asctime)s \033[1;34;40m%(levelname)-8s \033[1;37;40m%(message)s',datefmt='%H:%M:%S', handlers = handlers)

mesh_depth = 12
        
class meshing():

    def get_PointCloud(self):

        global swap_axis, path, filename, mesh_output_folder, simplified_output_folder, with_texture_output_folder, obj_file, separator, c, log_name, lat, lon, utm_easting, utm_northing, zone, log_name, log_folder, pc_folder, post_dest_folder, model_dest_folder

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

        #Define o3d data object to handle PointCloud

        ply_point_cloud = o3d.data.PLYPointCloud()

        root = Tk()
        
        root.iconbitmap(default = 'gui_images/ARTAK_103_drk.ico')
        
        root.withdraw()
        
        fullpath = filedialog.askopenfile(filetypes=(("PointClouds", "*.ply;*.pts;"),("All files", "*.*")))
        
        fullpath = str(fullpath)  

        #Separate source path from filename

        path, filename = os.path.split(fullpath)
        
        path = path.replace("<_io.TextIOWrapper name='", '')
        
        filename = filename.replace("' mode='r' encoding='cp1252'>", '')
        
        fullpath = path+separator+filename
        
        if 'None' in fullpath:
            
            quit()

        logfilename = filename.replace('.ply', '').replace('.pts', '').replace('.obj', '')
        
        pc_folder = logfilename
        
        log_name = "hr_"+filename.replace('.ply', '').replace('.pts', '').replace('.obj', '')+"_"+str(d)+"_"+str(ct)+".log"

        #Derive destination folders from source path
        
        post_dest_folder = "ARTAK_MM/POST/Photogrammetry"+separator+"hr_"+pc_folder+separator+"Productions/Production_1/Data/Model/Preprocessed"
        
        model_dest_folder = "ARTAK_MM/POST/Photogrammetry"+separator+"hr_"+pc_folder+separator+"Productions/Production_1/Data/Model"

        mesh_output_folder = "ARTAK_MM/DATA/PointClouds/HighRes"+separator+pc_folder+separator+"mesh_hr"

        simplified_output_folder = "ARTAK_MM/DATA/PointClouds/HighRes"+separator+pc_folder+separator+"simplified_hr"

        with_texture_output_folder = "ARTAK_MM/DATA/PointClouds/HighRes"+separator+pc_folder+separator+"final_hr"
        
        log_folder = "ARTAK_MM/LOGS/"

        #Create directories within the source folder if they dont exist

        if not os.path.exists(mesh_output_folder):

            os.makedirs(mesh_output_folder)

        if not os.path.exists(simplified_output_folder):

            os.makedirs(simplified_output_folder, mode = 777)

        if not os.path.exists(with_texture_output_folder):

            os.makedirs(with_texture_output_folder, mode = 777)     
            
        if not os.path.exists(post_dest_folder):
    
            os.makedirs(post_dest_folder, mode = 777)          

        if ".obj" in filename:

            shutil.copy(fullpath, simplified_output_folder)

            file_size_pre_edit = int(os.path.getsize(fullpath)) #Here we get the file size in bytes.

            shutil.rmtree(mesh_output_folder)

            generated_mesh = fullpath
            
            swap_axis = 1

            self.mesh_processing(generated_mesh, swap_axis, file_size_pre_edit, file_size_post_edit)
            
        else:

            swap_axis = 0
        
        preview = 0
        
        with open("ARTAK_MM/LOGS/status.log", "w") as status:
            
            pass
        
        #logging.info('Loading PointCloud.\r')
    
        message = 'Loading PointCloud. '+str(fullpath)

        self.write_to_log(path, separator, message)

        pcd = o3d.io.read_point_cloud(fullpath)
        
        if preview == 1 :
    
            target = pcd
    
            message = 'Generated Mesh'	
    
            self.visualize(target, message)		
    
        else:
    
            pass        

        #This will output the Point count

        #logging.info(str(pcd)+"\r")

        message = str(pcd)

        self.write_to_log(path, separator, message)			

        self.downsample(preview, pcd, swap_axis)

    def downsample(self, preview, pcd, swap_axis):

        #We need to downsample the PointCloud to make it less dense and easier to work with

        #logging.info("Downsampling.\r")

        message = 'Downsampling.'

        self.write_to_log(path, separator, message)				

        downpcd = pcd.voxel_down_sample(voxel_size = 0.01)

        #logging.info(str(downpcd)+"\r")

        message = str(downpcd)

        self.write_to_log(path, separator, message)			

        if preview == 1 :

            target = downpcd

            message = 'Optimized PointCloud'

            self.visualize(target, message)

        self.compute_normals_and_generate_mesh(preview, downpcd, swap_axis, mesh_depth)

    def compute_normals_and_generate_mesh(self, preview, downpcd, swap_axis, mesh_depth):

        #Since some PointClouds don't include normals information (needed for texture and color extraction) we will have to calculate it.

        #logging.info("Computing Normals.\r")

        message = 'Computing Normals.'

        self.write_to_log(path, separator, message)				

        downpcd.estimate_normals(search_param = o3d.geometry.KDTreeSearchParamHybrid(radius = 0.1, max_nn = 30))

        #logging.info('Generating Mesh.\r')

        message = 'Generating Mesh.'

        self.write_to_log(path, separator, message)	

        mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(downpcd, depth = mesh_depth, width = 0, scale = 1.1, linear_fit = False)[0]

        ##logging.info(mesh)		

        generated_mesh = mesh_output_folder+separator+filename.replace('ply', 'obj').replace('pts', 'obj')

        if preview == 1 :

            target = mesh

            message = 'Generated Mesh'	

            self.visualize(target, message)		

        else:

            pass

        #logging.info("Exporting Mesh.\r")

        o3d.io.write_triangle_mesh(generated_mesh,
                                    mesh,
                                    write_ascii = False,
                                    compressed = True,
                                    write_vertex_normals = True,
                                    write_vertex_colors = True,
                                    write_triangle_uvs = True,
                                    print_progress = False)

        message = 'Exporting Mesh'

        self.write_to_log(path, separator, message)
        
        mesh_size = int(os.path.getsize(generated_mesh))
        
        if mesh_size > 4000000000:
            
            mesh_depth = 11
            
            #logging.info("Mesh is not memory friedly. Retrying with safer parameters.\r")
    
            message = 'Mesh is not memory friedly. Retrying with safer parameters.'            
            
            self.write_to_log(path, separator, message)
            
            self.compute_normals_and_generate_mesh(preview, downpcd, swap_axis, mesh_depth)
            
        else:
            
            self.mesh_processing(generated_mesh, swap_axis)

    def mesh_processing(self, generated_mesh, swap_axis):

        try:

            #We will use Meshlab from now on to to handle the processing.

            ms = pymeshlab.MeshSet()

            #logging.info("Loading and Analyzing Mesh.\r")

            message = 'Loading and Analyzing Mesh.'

            self.write_to_log(path, separator, message)				

            ms.load_new_mesh(generated_mesh)	
            
            try:
                
                #In order to get closer to the usable faces as much as possible, we will calculate the unusable face edge legth by dividing the
                #mesh diagonal bounding box mesurement by 200. This is the value that meshlab uses as a default on its filter.
                #Caveat: If the object was edited too much (The total manually removed faces is higher than 25% of the entire bounding box), the bounding box method to determine 
                #the face length will bee too much, therefore, we will have to use an arbitrary static value; we have found that 1.6 works well.
    
                boundingbox =  ms.current_mesh().bounding_box()
                diag = boundingbox.diagonal()
            
                t_hold = diag / 200
                
                file_size = int(os.path.getsize(generated_mesh))
                
                if file_size <= 500000000:
                    
                    p = pymeshlab.Percentage(10)
                    
                else:
            
                    p = pymeshlab.Percentage(50)
            
                #logging.info('Refining.\r')
            
                message = 'Refining'
            
                self.write_to_log(path, separator, message)    
            
                #We will select faces that are long based on the bounding box calculation and then remove them
            
                ms.apply_filter('compute_selection_by_edge_length',
                                            threshold = t_hold)
            
                ms.apply_filter('meshing_remove_selected_faces')
            
                #The selection process and removal of long faces will create floaters, we will remove isolated faces
            
                ms.apply_filter('meshing_remove_connected_component_by_diameter',
                                            mincomponentdiag = p)
                
                # if this is a generated file from exyn sensors, then we need to use 'safe' values different from the leica ones.
                
                if ".ply" in filename:
                    
                    file_size = int(os.path.getsize(generated_mesh))
                
                    if file_size <= 500000000:
                        
                        t_hold = 0.3
                        p = pymeshlab.Percentage(10)
                
                    else:
                        
                        t_hold = 0.3
                        p = pymeshlab.Percentage(50)                    
                    
                else:
                    
                    t_hold = 0.06
                    p = pymeshlab.Percentage(25)
            
                #Since there will still be some long faces, we will mark them and remove them, this time applying a 0.06 thershold. This is 
            
                ms.apply_filter('compute_selection_by_edge_length',
                                            threshold = t_hold)  
            
                ms.apply_filter('meshing_remove_selected_faces')
            
                #Then we remove any isolated faces (floaters) that might still be laying around
            
                ms.apply_filter('meshing_remove_connected_component_by_diameter',
                                            mincomponentdiag = p)     
   
                #logging.info("Exporting Mesh.")
            
                message = 'Exporting Mesh.'
            
                self.write_to_log(path, separator, message)				
            
                newpath = simplified_output_folder+separator+filename.replace('ply', 'obj').replace('pts', 'obj')
            
                ms.save_current_mesh(newpath,
                                    save_vertex_color = True,
                                    save_vertex_coord = True,
                                    save_vertex_normal = True,
                                    save_face_color = True,
                                    save_wedge_texcoord = True,
                                    save_wedge_normal = True,
                                    save_polygonal = True)	
                
            except pymeshlab.pmeshlab.PyMeshLabException:
                
                try:
                    
                    ms.load_new_mesh(generated_mesh)
                    
                    #logging.info('Mesh not optimal. Retargeting parameters (1).\r')
                
                    message = 'Mesh not optimal. Retargeting parameters (1).'
                
                    self.write_to_log(path, separator, message)                      
                    
                    boundingbox =  ms.current_mesh().bounding_box()
                    
                    diag = boundingbox.diagonal()
                
                    t_hold = diag / 200
                
                    p = pymeshlab.Percentage(25)
                
                    #logging.info('Refining.\r')
                
                    message = 'Refining'
                
                    self.write_to_log(path, separator, message)    
                
                    #We will select faces that are long based on the bounding box calculation and then remove them
                
                    ms.apply_filter('compute_selection_by_edge_length',
                                                threshold = t_hold)
                
                    ms.apply_filter('meshing_remove_selected_faces')
                
                    #The selection process and removal of long faces will reate floaters, we will remove isolated faces
                
                    ms.apply_filter('meshing_remove_connected_component_by_diameter',
                                                mincomponentdiag = p)
                    
                    if ".ply" in filename:
                        
                        file_size = int(os.path.getsize(generated_mesh))
                    
                        if file_size <= 500000000:                        
                        
                            t_hold = 0.5
                            p = pymeshlab.Percentage(25)
                            
                        else:
                            
                            t_hold = 0.5
                            p = pymeshlab.Percentage(10)                            
                            
                    
                    else:
                        
                        t_hold = 0.075
                        p = pymeshlab.Percentage(25)
                
                    #Since there will still be some long faces, we will mark them and remove them, this time applying a 0.06 thershold. This is 
                
                    ms.apply_filter('compute_selection_by_edge_length',
                                                threshold = t_hold)  
                
                    ms.apply_filter('meshing_remove_selected_faces')
                
                    #Then we remove any isolated faces (floaters) that might still be laying around
                
                    ms.apply_filter('meshing_remove_connected_component_by_diameter',
                                                mincomponentdiag = p)  
                    
                    #logging.info("Exporting Mesh.")
                
                    message = 'Exporting Mesh.'
                
                    self.write_to_log(path, separator, message)				
                
                    newpath = simplified_output_folder+separator+filename.replace('ply', 'obj').replace('pts', 'obj')
                
                    ms.save_current_mesh(newpath,
                                        save_vertex_color = True,
                                        save_vertex_coord = True,
                                        save_vertex_normal = True,
                                        save_face_color = True,
                                        save_wedge_texcoord = True,
                                        save_wedge_normal = True,
                                        save_polygonal = True)
                
                except pymeshlab.pmeshlab.PyMeshLabException:
                    
                    try:
                    
                        ms.load_new_mesh(generated_mesh)
                        
                        #logging.info('Mesh not optimal. Retargeting parameters (2).\r')
                    
                        message = 'Mesh not optimal. Retargeting parameters (2).'
                    
                        self.write_to_log(path, separator, message)                      
                        
                        boundingbox =  ms.current_mesh().bounding_box()
                        
                        diag = boundingbox.diagonal()
                    
                        t_hold = diag / 200
                    
                        p = pymeshlab.Percentage(25)
                    
                        #logging.info('Refining.\r')
                    
                        message = 'Refining'
                    
                        self.write_to_log(path, separator, message)    
                    
                        #We will select faces that are long based on the bounding box calculation and then remove them
                    
                        ms.apply_filter('compute_selection_by_edge_length',
                                                    threshold = t_hold)
                    
                        ms.apply_filter('meshing_remove_selected_faces')
                    
                        #The selection process and removal of long faces will reate floaters, we will remove isolated faces
                    
                        ms.apply_filter('meshing_remove_connected_component_by_diameter',
                                                    mincomponentdiag = p)
                        
                        if ".ply" in filename:
                            
                            file_size = int(os.path.getsize(generated_mesh))
                        
                            if file_size <= 500000000:                        
                            
                                t_hold = 0.9
                                p = pymeshlab.Percentage(10)
                                
                            else:
                                
                                t_hold = 0.9
                                p = pymeshlab.Percentage(25)                            
                        
                        else:
                            
                            t_hold = 0.08
                            p = pymeshlab.Percentage(25)
                    
                        #Since there will still be some long faces, we will mark them and remove them, this time applying a 0.06 thershold. This is 
                    
                        ms.apply_filter('compute_selection_by_edge_length',
                                                    threshold = t_hold)  
                    
                        ms.apply_filter('meshing_remove_selected_faces')
                    
                        #Then we remove any isolated faces (floaters) that might still be laying around
                    
                        ms.apply_filter('meshing_remove_connected_component_by_diameter',
                                                    mincomponentdiag = p)  
                        
                        #logging.info("Exporting Mesh.")
                    
                        message = 'Exporting Mesh.'
                    
                        self.write_to_log(path, separator, message)				
                    
                        newpath = simplified_output_folder+separator+filename.replace('ply', 'obj').replace('pts', 'obj')
                    
                        ms.save_current_mesh(newpath,
                                            save_vertex_color = True,
                                            save_vertex_coord = True,
                                            save_vertex_normal = True,
                                            save_face_color = True,
                                            save_wedge_texcoord = True,
                                            save_wedge_normal = True,
                                            save_polygonal = True)
                        
                    except pymeshlab.pmeshlab.PyMeshLabException:
                        
                        #If we got to this exception, then it means the generated mesh has way too many disconnected faces and cannot be fully 
                        #cleaned, so we will have to export with some artifacts in it. 
                        
                        ms.load_new_mesh(generated_mesh)
                        
                        #logging.info('Mesh not optimal. Retargeting parameters (2).\r')
                    
                        message = 'Mesh still not optimal. Retargeting parameters (3) and going to best effort.'
                    
                        self.write_to_log(path, separator, message)                      
                        
                        boundingbox =  ms.current_mesh().bounding_box()
                        
                        diag = boundingbox.diagonal()
                    
                        t_hold = 3
                    
                        #We will select faces that are long based on the bounding box calculation and then remove them
                    
                        ms.apply_filter('compute_selection_by_edge_length',
                                                    threshold = t_hold)
                    
                        ms.apply_filter('meshing_remove_selected_faces')      
                        
                        message = 'Exporting Mesh.'
                    
                        self.write_to_log(path, separator, message)				
                    
                        newpath = simplified_output_folder+separator+filename.replace('ply', 'obj').replace('pts', 'obj')
                    
                        ms.save_current_mesh(newpath,
                                            save_vertex_color = True,
                                            save_vertex_coord = True,
                                            save_vertex_normal = True,
                                            save_face_color = True,
                                            save_wedge_texcoord = True,
                                            save_wedge_normal = True,
                                            save_polygonal = True) 
                        
            m = ms.current_mesh()
        
            v_number = m.vertex_number()
            f_number = m.face_number()
        
            #logging.info("Initial VC: "+str(v_number)+". Initial FC: "+str(f_number)+".\r")
        
            message = 'Initial VC: '+str(v_number)+'. Initial FC: '+str(f_number)+"."   
            
            self.write_to_log(path, separator, message)	

            #Let's take a look at the mesh file to see how big it is. We are constrained to about 120Mb in this case, therefore we 
            #will have to decimate if the file is bigger than that number.
            
            newpath = simplified_output_folder+separator+filename.replace('ply', 'obj').replace('pts', 'obj')

            if f_number > 6500000: #Decimate over 6500000 faces (approx.650Mb)

                self.decimation(ms, newpath, f_number)

            else:

                self.add_texture_and_materials(newpath, swap_axis)	

        except MemoryError:

            #logging.info('Error. Not enough Memory to run the process. Quitting.\r')

            message = 'Error. Not enough Memory to run the process. Quitting.'

            self.write_to_log(path, separator, message)		

            quit()

    def decimation(self, ms, newpath, f_number):

        #The mesh decimation works best if we take a percentage of faces at a time. We will decimate to target amount 
        #of (faces / weight) and save the file, then read the file size and if necessary (over the 185Mb threshold), we will repeat 
        #the decimation process again until the resulting mesh meets the file size criteria, we will do this n times (passes).

        m = ms.current_mesh()
        
        c = 1
    
        while f_number > 6500000:
            
            m = ms.current_mesh()
            
            f_number = m.face_number()
            
            target_faces = int(f_number / 1.125)
            
            #logging.info("Target: "+str(int(target_faces))+" F. Iter. "+str(c)+".\r")

            message = "Target: "+str(int(target_faces))+" F. Iter. "+str(c)+"."

            self.write_to_log(path, separator, message)	            
            
            ms.apply_filter('meshing_decimation_quadric_edge_collapse', 
                            targetfacenum = int(target_faces), targetperc = 0, 
                            qualitythr  = 0.3, 
                            optimalplacement = True,
                            preservenormal = True,
                            autoclean = True)  
            
            f_number = m.face_number()
            
            v_number = m.vertex_number()
            
            ratio = (abs(target_faces / f_number) - 1.1)* 10 #Efficiency ratio. resulting amt faces vs target amt of faces
        
            #logging.info("Achieved: "+str(f_number)+" F. Ratio ==> "+"%.2f" % abs(ratio)+":1.00.\r")
        
            message = 'Achieved: '+str(f_number)+' F. Ratio ==> '+'%.2f' % abs(ratio)+':1.00.'
        
            self.write_to_log(path, separator, message) 
            
            c += 1
        
        m = ms.current_mesh()
        
        f_number = m.face_number()
        v_number = m.vertex_number()
            
        #logging.info("End VC: "+str(v_number)+". End FC: "+str(f_number)+".\r")

        message = 'End VC: '+str(v_number)+'. End FC: '+str(f_number)+"."

        self.write_to_log(path, separator, message)	         
        
        newpath = simplified_output_folder+separator+filename.replace('ply', 'obj').replace('pts', 'obj')

        ms.save_current_mesh(newpath,
                            save_vertex_color = True,
                            save_vertex_coord = True,
                            save_vertex_normal = True,
                            save_face_color = False,
                            save_wedge_texcoord = False,
                            save_wedge_normal = False,
                            save_polygonal = False)		

        generated_mesh = newpath

        self.add_texture_and_materials(generated_mesh, swap_axis)

    def add_texture_and_materials(self, newpath, swap_axis):

        #This part creates the materials and texture file (.mtl and .png) by getting the texture coordinates from the vertex,
        #tranfering the vertex info to wedges and reating a trivialized texture coordinate from the per wedge info. In the end,
        #we will just extract the texture form the color present at that texture coordinate and thats how we get the texture info into a png
        
        ms = pymeshlab.MeshSet()
        
        #logging.info("Loading and Analyzing Mesh.\r")

        message = 'Loading and Analyzing Mesh.'

        self.write_to_log(path, separator, message)				

        ms.load_new_mesh(newpath)        
        
        #logging.info("Extracting Texture and Materials.\n")

        message = 'Generating Texture and Materials.'

        self.write_to_log(path, separator, message)	

        ms.load_new_mesh(newpath)

        if swap_axis == 1:

            #logging.info("Correcting Axis.\r")

            message = 'Correcting Axis.'

            self.write_to_log(path, separator, message)			

            ms.apply_filter('compute_matrix_from_rotation',
                            rotaxis = 0,
                            rotcenter = 0,
                            angle = 90,
                            snapflag = False,
                            snapangle  = 30,
                            freeze = True,
                            alllayers = False)	
        
        ms.apply_filter('compute_texcoord_parametrization_triangle_trivial_per_wedge',
                        sidedim = 0,
                        textdim = 10240,
                        border = 2,
                        method = 'Space-optimizing')

        newpath_texturized = with_texture_output_folder+separator+filename.replace('ply', 'obj').replace('pts', 'obj')
        
        ms.save_current_mesh(newpath_texturized,
                            save_vertex_color = True,
                            save_vertex_coord = True,
                            save_vertex_normal = True,
                            save_face_color = True,
                            save_wedge_texcoord = True,
                            save_wedge_normal = True,
                            save_polygonal = False)	
        
        ms.load_new_mesh(newpath_texturized)

        newfile = filename.replace('.obj', '').replace('.pts', '').replace('.ply', '')
        
        ms.apply_filter('compute_texmap_from_color',
                        textname = newfile,
                        textw = 16384, 
                        texth = 16384,
                        overwrite = False,
                        pullpush = True)
        
        ms.save_current_mesh(newpath_texturized,
                            save_vertex_color = True,
                            save_vertex_coord = False,
                            save_vertex_normal = False,
                            save_face_color = False,
                            save_wedge_texcoord = True,
                            save_wedge_normal = True,
                            save_polygonal = False)
        
        #We need to compress the texture file
        
        img = Image.open(newpath_texturized.replace('.obj','.png'))
        img = img.convert("P", palette=Image.WEB, colors=256)
        img.save(newpath_texturized.replace('.obj','.png'), optimize=True)
        
        #copy the obj to the post folder
        
        shutil.copy(newpath_texturized, post_dest_folder+"/Model.obj")
        
        #Let's compress
        
        self.compress_into_zip(with_texture_output_folder, newpath)
        
        #Once done, we will cleanup
        
        files = [f for f in glob.glob(with_texture_output_folder+"/*.zip")]
        
        for file in files:
            
            shutil.copy(file, model_dest_folder)
            
        try:
            
            shutil.rmtree("ARTAK_MM/DATA/PointClouds/HighRes"+separator+pc_folder)
            
            #Remove the status flag for MM_GUI progressbar
            
            os.remove(log_folder+"/status.log")
            
        except FileNotFoundError:
            
            pass 
        
        messagebox.showinfo('ARTAK 3D Map Maker', 'Reconstruction Complete.')

        #logging.info('Process complete.\r')

        message = 'Reconstruction Complete.'   
        
        os.remove("ARTAK_MM/LOGS/status.log")
        
        sys.exit()

    def compress_into_zip(self, with_texture_output_folder, newpath):

        extensions = ['.obj', '.obj.mtl', '.png', '.xyz', '.prj']

        compression = zipfile.ZIP_DEFLATED
        
        zip_file = with_texture_output_folder+separator+"hr_"+filename.replace('.obj', '').replace('.ply', '').replace('.pts', '')+'.zip'

        with zipfile.ZipFile(zip_file, mode = "w") as zf:

            for ext in extensions:

                try:

                    zf.write(with_texture_output_folder+separator+filename.replace('.obj', '').replace('.ply', '').replace('.pts', '')+ext, filename.replace('.obj', '').replace('.ply', '').replace('.pts', '')+ext, compress_type = compression, compresslevel = 9)

                except FileExistsError:

                    pass
                    
                except FileNotFoundError:
                    
                    pass                
        
        return

    def visualize(self, target, message):

        #This is the preview step

        o3d.visualization.draw_geometries([target],
                                            window_name = str(message),
                                            width = 1280,
                                            height = 900,
                                            zoom = 0.32000000000000001,
                                            front = [-0.34267508672450531, 0.89966482743414444, 0.27051244558475285],
                                            lookat = [-15.934802105738544, -4.9954584521228949, 1.4543439424505489],
                                            up = [0.095768108125702828, -0.25299355589613992, 0.96271632900925208])		
        return

    def write_to_log(self, path, separator, message):

        with open(log_folder+log_name, "a+") as log:

            log.write(message+"\r")

        return

if __name__ == '__main__':

    meshing().get_PointCloud()
