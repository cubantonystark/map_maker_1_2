import os
import shutil
from datetime import datetime, timedelta
from PIL import Image
import json
import random
import MM_logger
import MM_video


def get_image_files(folder):
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif']  # Add more extensions if needed
    image_files = []

    for root, dirs, files in os.walk(folder):
        for file in files:
            if any(file.lower().endswith(ext) for ext in image_extensions):
                image_files.append(os.path.join(root, file))

    return image_files


def get_video_files(folder):
    video_extensions = ['.mp4', '.ts', ".m4v"]  # Add more extensions if needed
    video_files = []

    for root, dirs, files in os.walk(folder):
        for file in files:
            if any(file.lower().endswith(ext) for ext in video_extensions):
                video_files.append(os.path.join(root, file))

    return video_files


def remove_mp4_elements(lst):
    lst[:] = [element for element in lst if "MP4" not in element]


def find_mp4_elements(lst):
    lst[:] = [element for element in lst if "MP4" in element]


def sort_files_by_datetime(file_list):
    try:
        file_list.sort(key=lambda x: Image.open(x)._getexif().get(36867))
    except:
        print("no exif data")
    return file_list


def handle_video():
    print("handling video")


def group_images(source, logger=None, image_spacing=60, rerun=False, frame_spacing=30):
    rerun_jobs = rerun
    logger.info("rerun = " + str(rerun_jobs))
    # Part 1 handle any videos

    # empty array to later append and return to mapmaker for processing said folders
    folder_name_paths = []

    # get a list of all video files in the folder
    videos = get_video_files(source)
    logger.info(videos)
    exif_exists = False

    # for each video in the list
    for each_video in videos:
        # get filename
        video_file_name = str(os.path.basename(each_video))

        # remove .mp4 from filename
        video_name = video_file_name.split(".")[0]

        video_name_nospaces = video_name.replace(" ", "_")
        video_name_nospaces_noperiods = video_name_nospaces.replace(".", "-")
        # extract the frames from the video
        logger.info("Video identified. Proceeding to extract frames.")
        video_name = MM_video.extract_frames(each_video, os.path.join(os.getcwd(),
                                                         'ARTAK_MM/DATA/Raw_Images/UNZIPPED/',
                                                         video_name_nospaces_noperiods), logger=logger, frame_spacing=int(frame_spacing))
        # add the path of the extracted frames to the folder paths array to be returned to mapmaker for processing
        folder_name_paths.append(video_name)

    # Part 2 Handle Images

    # Handle exception if image spacing is incorrectly set by user as an empty string
    if image_spacing == "":
        image_spacing = 60

    # Define the path to the source folder containing the photos
    file_list = get_image_files(source)

    # Define the path to the destination folder where the photos will be moved
    destination_folder = os.getcwd() + '/ARTAK_MM/DATA/Raw_Images/UNZIPPED/'

    # Create the destination folder if it does not exist
    # this is the root directory where the new directories for each dataset are added
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
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
            try:
                prev_time = datetime.strptime(Image.open(os.path.join(file_list[i - 1]))._getexif()[36867],
                                              '%Y:%m:%d %H:%M:%S')
                curr_time = datetime.strptime(Image.open(os.path.join(file_list[i]))._getexif()[36867],
                                              '%Y:%m:%d %H:%M:%S')
                exif_exists = True
                if (curr_time - prev_time).total_seconds() <= image_spacing:
                    grouped_files[-1].append(file_list[i])
                else:
                    grouped_files.append([file_list[i]])
            except:
                grouped_files.append([file_list[i]])
    logger.info(len(grouped_files))

    # Move the photos into new folders based on the time interval and create a JSON file for each folder
    for i, files in enumerate(grouped_files):
        try:
            folder_name = datetime.strptime(Image.open(os.path.join(files[0]))._getexif()[36867],
                                            '%Y:%m:%d %H:%M:%S').strftime('%Y-%m-%d_%H-%M-%S')
        except:
            folder_name = "VIDEO"
        logger.info("Folder name = " + folder_name)
        stop_process = False
        try:
            if exif_exists:
                logger.info("EXIF exists")
                folder_path = os.path.join(destination_folder, folder_name)

                og_path = folder_path
                count = 1
                finished = False
                while not finished:
                    path = og_path + "-V" + str(count)
                    logger.info("OGPath = " + og_path)
                    logger.info("Path = " + path)
                    if os.path.exists(path):
                        logger.info("Directory already exists. Sequencing up version.")
                        count += 1
                        try:
                            destination_folder_versioned = og_path + "-V" + str(count)
                            logger.info("Destination folder versioned = " + destination_folder_versioned)
                            os.makedirs(destination_folder_versioned)
                            folder_path = destination_folder_versioned
                            folder_name = folder_name + "-V" + str(count)
                            finished = True
                        except:
                            print("trying again")
                    else:
                        destination_folder_versioned = og_path + "-V" + str(count)
                        os.makedirs(destination_folder_versioned)
                        folder_path = destination_folder_versioned
                        folder_name = folder_name + "-V" + str(count)
                        finished = True

                logger.info ("Attempting to make directory " + str(folder_path))
                logger.info("Successfully made directory " + str(folder_path))

                num_files = len(files)
                photo_data = []
                for file in files:
                    logger.info(file)
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
                    file = file[splits - 1]
                    logger.info("File = " + file)
                    destination_path = os.path.join(destination_folder, folder_name, file)
                    logger.info("attempting to copy " + source_path + " + to " + destination_path)
                    shutil.copy(source_path, destination_path)
                    logger.info("copied " + source_path + " + to " + destination_path)
                folder_name_paths.append(folder_name)

                metadata = {'total_photos': num_files, 'photos': photo_data}
                metadata_file = os.path.join(folder_path, 'metadata.json')
                # with open(metadata_file, 'w') as f:
                #    json.dump(dict(metadata), f, indent=4)
            else:
                logger.info("exif non-existent")

            #   shutil.make_archive("FlightPlanner/flight_data/grouped/ziped/" + folder_name, 'zip', folder_path)
        except FileExistsError:
            logger.warning("Files already processed")
            if rerun:
                logger.info("Rerun = True. Rerunning")
                if " " in folder_name:
                    folder_name = folder_name.replace(" ", "_")
                if "." in folder_name:
                    folder_name = folder_name.replace(".", "-")
                folder_name = folder_name + str(random.randint(1, 5000))
                folder_path = os.path.join(destination_folder, folder_name)

                logger.info("Attempting to make directory = " + folder_path)
                os.makedirs(folder_path)
                logger.info("Successfully made directory = " + folder_path)
                num_files = len(files)
                photo_data = []
                for file in files:
                    logger.info(file)
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
                    file = file[splits - 1]
                    logger.info("File = " + file)
                    destination_path = os.path.join(destination_folder, folder_name, file)
                    logger.info("attempting to copy " + source_path + " + to " + destination_path)
                    shutil.copy(source_path, destination_path)
                    logger.info("copied " + source_path + " + to " + destination_path)
                folder_name_paths.append(folder_name)

            else:
                logger.info("Rerun = False. Not re-running.")
                stop_process = True
                pass

    # now handle the case in which there is no exif data
    if not exif_exists and len(file_list) > 0:

        logger.info("exif does not non-existent")
        # folder_name = "VIDEO"
        # logger.info ("Folder name = " + folder_name)
        # folder_name_paths.append(folder_name)
        # folder_path = os.path.join(destination_folder, folder_name)
        # print (folder_path)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        for each_file in file_list:
            each_file_name = os.path.basename(each_file)
            if " " in each_file_name:
                each_file_name = folder_name.replace(" ", "_")
            if "." in each_file_name:
                each_file_name = folder_name.replace(".", "-")
            logger.info(each_file_name)
            logger.info("file = " + each_file_name)
            logger.info("File = " + each_file_name)
            destination_path = os.path.join(folder_path, each_file_name)
            logger.info("attempting to copy " + each_file + " + to " + destination_path)
            shutil.copy(each_file, destination_path)
            logger.info("copied " + each_file + " + to " + destination_path)
    logger.info("FNP " + str(folder_name_paths))
    return folder_name_paths
