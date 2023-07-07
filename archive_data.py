import os
import shutil


def delete_files_and_subdirectories_except_productions(location):
    print ("Starting")
    for each_dir in os.walk(location):
        print (each_dir, " " , location)
        for each_folder_name in os.listdir(str(location) + each_dir):
            if each_folder_name != "Productions":
                dir_path = os.path.join(location, each_dir, each_folder_name)
              #  shutil.rmtree(dir_path)
                print("Removed Folder" + str(dir_path))


# Specify the folder path
folder_to_clean = "C:/ARTAK_MM/POST/Photogrammetry"

# Call the method
delete_files_and_subdirectories_except_productions(folder_to_clean)
