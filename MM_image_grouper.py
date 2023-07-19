import os
import shutil
from datetime import datetime, timedelta
from PIL import Image
import json
import random
import MM_logger
# Set the time interval (in seconds) between photos


def get_image_files(folder):
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif']  # Add more extensions if needed
    image_files = []

    for root, dirs, files in os.walk(folder):
        for file in files:
            if any(file.lower().endswith(ext) for ext in image_extensions):
                image_files.append(os.path.join(root, file))

    return image_files


def remove_mp4_elements(lst):
    lst[:] = [element for element in lst if "MP4" not in element]


def sort_files_by_datetime(file_list):
    file_list.sort(key=lambda x: Image.open(x)._getexif().get(36867))
    return file_list

def group_images(source, logger=None, image_spacing=60):

    if image_spacing == "":
        image_spacing = 60
    # Define the path to the source folder containing the photos
    file_list = get_image_files(source)
    # Define the path to the destination folder where the photos will be moved
    destination_folder = os.getcwd()+'/ARTAK_MM/DATA/Raw_Images/UNZIPPED/'
    
    # Create the destination folder if it does not exist
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    
    # Get a list of all the files in the source folder

    # for each_file in file_list:
    #     if "MP4" in str(each_file):
    #         print ("Found MP4.")
    #         print ("Count =" + str(count))
    #         file_list.remove(count)
    #         print("MP4 removed")
    #     count = count+1

    # Example usage

    remove_mp4_elements(file_list)

    # Sort the files by creation time from the EXIF data
    file_list = sort_files_by_datetime(file_list)
    image_spacing = int(image_spacing)
    # Create a list of lists containing the file names of photos taken within the time interval
    grouped_files = []
    for i in range(len(file_list)):
        if i == 0:
            grouped_files.append([file_list[i]])
        else:
            prev_time = datetime.strptime(Image.open(os.path.join(file_list[i-1]))._getexif()[36867], '%Y:%m:%d %H:%M:%S')
            curr_time = datetime.strptime(Image.open(os.path.join(file_list[i]))._getexif()[36867], '%Y:%m:%d %H:%M:%S')
            if (curr_time - prev_time).total_seconds() <= image_spacing:
                grouped_files[-1].append(file_list[i])
            else:
                grouped_files.append([file_list[i]])
    
    # Move the photos into new folders based on the time interval and create a JSON file for each folder    
    folder_name_paths = []
    for i, files in enumerate(grouped_files):
        folder_name = datetime.strptime(Image.open(os.path.join(files[0]))._getexif()[36867], '%Y:%m:%d %H:%M:%S').strftime('%Y-%m-%d_%H-%M-%S')
        logger.info ("Folder name = " + folder_name)
        folder_path = os.path.join(destination_folder, folder_name)
        logger.info("Folder path =" + folder_path)
        try:
            os.makedirs(folder_path)
            num_files = len(files)
            photo_data = []
            for file in files:
                image = Image.open(os.path.join(file))
                exif_data = image._getexif()
                creation_time = datetime.strptime(exif_data[36867], '%Y:%m:%d %H:%M:%S')
                gps_data = None
                if exif_data.get(34853):
                    gps_data = {
                        'latitude': eval(str(exif_data[34853][2])),
                        'longitude': eval(str(exif_data[34853][4]))
                    }
                photo_data.append({'filename': file, 'creation_time': str(creation_time), 'gps': gps_data})
                source_path = os.path.join(file)
                file = file.split("\\")
                splits = len(file)
                file = file[splits-1]
                logger.info ("File = " + file)
                destination_path = os.path.join(destination_folder, folder_name, file)
                logger.info ("attempting to copy " + source_path + " + to " + destination_path)
                shutil.copy(source_path, destination_path)
                logger.info ("copied " + source_path + " + to " + destination_path)

            metadata = {'total_photos': num_files, 'photos': photo_data}
            metadata_file = os.path.join(folder_path, 'metadata.json')
            with open(metadata_file, 'w') as f:
                json.dump(dict(metadata), f, indent=4)
         #   shutil.make_archive("FlightPlanner/flight_data/grouped/ziped/" + folder_name, 'zip', folder_path)
            folder_name_paths.append(folder_name)
        except FileExistsError:
            logger.warning ("Files already processed")
    logger.info("FNP " + str(folder_name_paths))
    return folder_name_paths
#group_images("E:\\DCIM\\101MEDIA\\")