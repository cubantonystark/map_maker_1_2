import shutil
from datetime import datetime
from PIL import Image
import random
from MM_video import *
import MM_file_handler
from MM_objects import MapmakerProject
from MM_logger import initialize_logger
import MM_job_que
import time


def get_image_files(folder):
    """
    Used to get a list of the image files in a folder (does not search child folders)

    Args:
        folder: os.path() complete filepath to search

    Returns:
    List of images
    """
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif']  # Add more extensions if needed
    image_files = []

    for root, dirs, files in os.walk(folder):
        for file in files:
            if any(file.lower().endswith(ext) for ext in image_extensions):
                image_files.append(os.path.join(root, file))

    return image_files


def get_lidar_files(folder):
    lidar_extensions = ['.pts', '.ply', '.e57']  # Add more extensions if needed
    lidar_files = []

    for i in os.listdir(folder):
        for each_ext in lidar_extensions:
            if each_ext in i:
                lidar_files.append(os.path.join(folder, i))
    return lidar_files


def get_video_files(folder):
    """
    Used to get a list of the video files in a folder (does not search child folders)

    Args:
        folder: os.path() complete filepath to search

    Returns:
    List of images

    """
    video_extensions = ['.mpeg', '.mp4', '.ts', ".m4v"]  # Add more extensions if needed
    video_files = []

    for root, dirs, files in os.walk(folder):
        for file in files:
            if any(file.lower().endswith(ext) for ext in video_extensions):
                video_files.append(os.path.join(root, file))

    return video_files


def handle_new_zip(file, _quality, _maptype, _video_frame_extraction_rate, _partition_key):
    """
    Handles a zip file with either a single video or a set of images
    Args:
        file:
        _quality:
        _maptype:
        _video_frame_extraction_rate:
        _partition_key:
    """
    print('Attempting to UNZIP file. Filename = ' + file)
    log = initialize_logger("testing-zip-upload")
    file_handler = MM_file_handler.MMfileHandler(file, log)
    folder = file.split(".")[0]
    new_path = os.path.join(os.getcwd(), 'ARTAK_MM/DATA/Raw_Images/UNZIPPED', folder)
    new_file_path = file_handler.unzip()

    # handle different data types
    # set variables
    video_found = False
    video = ""
    lidar_found = False
    lidar = ""
    lidar_extensions = ['.ply', '.pts', '.e57']
    video_extensions = ['.mpeg', '.mp4', '.ts', ".m4v"]  # Add more extensions if needed

    for i in os.listdir(new_file_path):
        for each_extension in video_extensions:
            if each_extension in i:
                video_found = True
                video = i
                video = os.path.join(new_file_path, i)
        for each_extension in lidar_extensions:
            if each_extension in i:
                lidar_found = True
                lidar = os.path.join(new_file_path, i)
    data_type = "Imagery"
    if lidar_found:
        data_type = "LiDAR"
        new_file_path = lidar
    try:
        unique_folder_name = new_file_path.split("UNZIPPED/")[len(new_path.split("UNZIPPED/"))]
    except IndexError:
        unique_folder_name = "nonamemade"
    print('Completed the UNZIP of file. Filename = ' + file)
    print('Unique Name = ' + unique_folder_name)
    print('New Path = ' + new_file_path)
    print('Starting photogrammetry processing = ' + file)
    new_project = MapmakerProject(name=unique_folder_name, time_first_image='unknown', data_type=data_type,
                                  time_mm_start=time.time(),
                                  local_image_folder=new_file_path, total_images=100,
                                  session_project_number=1, map_type=_maptype, status="pending", quality=_quality,
                                  video_frame_extraction_rate=_video_frame_extraction_rate, partition_key=_partition_key
                                  )
    MM_job_que.add_job_to_que(new_project)


def ingest_data(source, logger=None, image_spacing=60, rerun=False, frame_spacing=30, sort=False):
    """
    Sole method for ingesting local data into MapMaker

    Args:
        source: os.path() location of the data to ingest
        logger: logger to send the status updates to
        image_spacing: the maximum time (in sec) between datasets, to use when categorizing data with multiple sorties
        rerun: process job regardless of whether the data already exists in the system
        frame_spacing: for videos, the time (in sec) between extracted frames

    Returns:
    List of folder paths which contain the ingested data
    """
    results = ""
    if os.path.isdir(source):
        results = ingest_folder(source, logger=logger, image_spacing=image_spacing, rerun=rerun, frame_spacing=frame_spacing, sort=sort)
    return results


def ingest_folder(source, logger=None, image_spacing=60, rerun=False, frame_spacing=30, sort=False):
    folder_name_paths = []

    # region handle videos
    # Part 1 handle any videos

    # get a list of all video files in the folder
    videos = get_video_files(source)

    # for each video in the list
    for each_video in videos:
        video_frames_path = ingest_video(each_video, logger, frame_spacing=frame_spacing)
        # get filename
        folder_name_paths.append(video_frames_path)
    # region handle images

    # Handle exception if image spacing is incorrectly set by user as an empty string
    if image_spacing == "":
        image_spacing = 60

    image_folder_paths = ingest_images(source, logger=logger, image_spacing=image_spacing, rerun=rerun, sort=sort)
    for i in image_folder_paths:
        folder_name_paths.append(i)

    lidar_files = get_lidar_files(source)
    for each_lidar in lidar_files:
        folder_name = ingest_lidar(each_lidar, logger=logger)
        folder_name_paths.append(folder_name)
    return folder_name_paths
    # Define the path to the source folder containing the photos


def ingest_images(source, logger=None, image_spacing=60, rerun=False, sort=False):
    folder_name_paths = []
    exif_exists = False

    file_list = get_image_files(source)

    # Define the path to the destination folder where the photos will be moved
    destination_folder = os.getcwd() + '/ARTAK_MM/DATA/Raw_Images/UNZIPPED/'

    # Create the destination folder if it does not exist
    # this is the root directory where the new directories for each dataset are added
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    # Sort the files by creation time from the EXIF data
    file_list = sort_files_by_datetime(file_list)
    # except:
    #     file_list = file_list
    image_spacing = int(image_spacing)

    if not sort:
        count = 0
        for i in file_list:
            if count == 0:
                folder_name = os.path.basename(i).split('.')[0]
                version_set = False
                version = 1
                while not version_set:
                    if os.path.exists(destination_folder + '/' + folder_name + "-V" + str(version)):
                        version += 1
                    else:
                        os.makedirs(destination_folder + '/' + folder_name + "-V" + str(version))
                        folder_name = folder_name + "-V" + str(version)
                        version_set = True

                count = count + 1
            file = i
            dest = destination_folder + '/' + folder_name
            folder_name_paths.append(dest)

            shutil.copy(file, dest)
    # Create a list of lists containing the file names of photos taken within the time interval
    if sort:
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
                        grouped_files[len(grouped_files)-1].append(file_list[i])
                    else:
                        grouped_files.append([file_list[i]])
                except TypeError:
                    print ('error')

        for i, files in enumerate(grouped_files):
            try:
                folder_name = datetime.strptime(Image.open(os.path.join(files[0]))._getexif()[36867],
                                                '%Y:%m:%d %H:%M:%S').strftime('%Y-%m-%d_%H-%M-%S')
            except:
                folder_name = os.path.basename(files[0])
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
                                print("Directory already exists. Sequencing up version")
                        else:
                            destination_folder_versioned = og_path + "-V" + str(count)
                            os.makedirs(destination_folder_versioned)
                            folder_path = destination_folder_versioned
                            folder_name = folder_name + "-V" + str(count)
                            finished = True

                    logger.info("Attempting to make directory " + str(folder_path))
                    logger.info("Successfully made directory " + str(folder_path))
            # except Exception as e:
            #     logger.error(e)

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
                    folder_name_paths.append(os.path.join(destination_folder, folder_name))

                    metadata = {'total_photos': num_files, 'photos': photo_data}
                    metadata_file = os.path.join(folder_path, 'metadata.json')
                    # with open(metadata_file, 'w') as f:
                    #    json.dump(dict(metadata), f, indent=4)
                else:
                    logger.info("exif non-existent")

            except FileExistsError:
                logger.warning("Files already processed")
    #             if rerun:
    #                 logger.info("Rerun = True. Rerunning")
    #                 if " " in folder_name:
    #                     folder_name = folder_name.replace(" ", "_")
    #                 if "." in folder_name:
    #                     folder_name = folder_name.replace(".", "-")
    #                 folder_name = folder_name + str(random.randint(1, 5000))
    #                 folder_path = os.path.join(destination_folder, folder_name)
    #
    #                 logger.info("Attempting to make directory = " + folder_path)
    #                 os.makedirs(folder_path)
    #                 logger.info("Successfully made directory = " + folder_path)
    #                 num_files = len(files)
    #                 photo_data = []
    #                 for file in files:
    #                     logger.info(file)
    #                     image = Image.open(os.path.join(file))
    #                     exif_data = image._getexif()
    #                     creation_time = datetime.strptime(exif_data[36867], '%Y:%m:%d %H:%M:%S')
    #                     gps_data = None
    #                     if exif_data.get(34853):
    #                         gps_data = {
    #                             'latitude': eval(str(exif_data[34853][2])),
    #                             'longitude': eval(str(exif_data[34853][4]))
    #                         }
    #                     photo_data.append({'filename': file, 'creation_time': str(creation_time), 'gps': gps_data})
    #                     source_path = os.path.join(file)
    #                     file = file.split("\\")
    #                     splits = len(file)
    #                     file = file[splits - 1]
    #                     logger.info("File = " + file)
    #                     destination_path = os.path.join(destination_folder, folder_name, file)
    #                     logger.info("attempting to copy " + source_path + " + to " + destination_path)
    #                     shutil.copy(source_path, destination_path)
    #                     logger.info("copied " + source_path + " + to " + destination_path)
    #                 folder_name_paths.append(os.path.join(destination_folder, folder_name))
    #
    #             else:
    #                 logger.info("Rerun = False. Not re-running.")
    #                 stop_process = True
    #                 pass
    #
    #     # now handle the case in which there is no exif data
    #     if not exif_exists and len(file_list) > 0:
    #
    #         logger.info("exif does not non-existent")
    #         # folder_name = "VIDEO"
    #         # logger.info ("Folder name = " + folder_name)
    #         # folder_name_paths.append(folder_name)
    #         folder_path = os.path.join(destination_folder, "test")
    #         # print (folder_path)
    #         if not os.path.exists(folder_path):
    #             os.makedirs(folder_path)
    #         for each_file in file_list:
    #             each_file_name = os.path.basename(each_file)
    #             if " " in each_file_name:
    #                 each_file_name = folder_name.replace(" ", "_")
    #             if "." in each_file_name:
    #                 each_file_name = folder_name.replace(".", "-")
    #             logger.info(each_file_name)
    #             logger.info("file = " + each_file_name)
    #             logger.info("File = " + each_file_name)
    #             destination_path = os.path.join(folder_path, each_file_name)
    #             logger.info("attempting to copy " + each_file + " + to " + destination_path)
    #             shutil.copy(each_file, destination_path)
    #             logger.info("copied " + each_file + " + to " + destination_path)
    # # # endregion
    #
    # logger.info("Data ingested successfully. List of new folders: " + str(folder_name_paths))
    return folder_name_paths


def ingest_lidar(source, logger=None):
    lidar_file_name = str(os.path.basename(source))
    print("Lidar found: " + lidar_file_name)
    lidar_name = lidar_file_name.split(".")[0]
    extension = lidar_file_name.split(".")[1]
        # cleanup the filename
    lidar_name_nospaces = lidar_name.replace(" ", "_")
    lidar_name_nospaces_noperiods = lidar_name_nospaces.replace(".", "-")
    logger.info("Lidar identified. Proceeding to copy lidar.")
    dest_folder = os.path.join(os.getcwd(), 'ARTAK_MM/DATA/Raw_Images/UNZIPPED/' + lidar_name_nospaces_noperiods)
    count = 1
    saved = False
    while not saved:
            # if the destination folder already exists, increment the -V up one until successfully saving
        if os.path.exists(dest_folder + "-V" + str(count)):
            logger.info("Directory already exists. Sequencing up version.")
            count += 1
            try:
                destination_folder_versioned = dest_folder + "-V" + str(count)
                logger.info("Video destination folder versioned = " + destination_folder_versioned)
                os.makedirs(destination_folder_versioned)
                shutil.copy(source, os.path.join(destination_folder_versioned + "/" + lidar_name_nospaces_noperiods + "-V" + str(count)) + '.' + extension)
                folder_name_path = destination_folder_versioned
                saved = True
                return folder_name_path

            except FileExistsError:
                logger.info("Directory already exists. Sequencing up version.")

        else:
            os.makedirs(dest_folder + "-V" + str(count))
            shutil.copy(source,
                            os.path.join(dest_folder + "-V" + str(count) + "/" + lidar_name_nospaces_noperiods + "-V" + str(count) + '.' + extension))
            folder_name_path = os.path.join(dest_folder + "-V" + str(count))
            saved = True
            return folder_name_path
        # add the path of the extracted     frames to the folder paths array to be returned to mapmaker for processing


def ingest_video(video_path, logger, frame_spacing=30):
    video_file_name = str(os.path.basename(video_path))

        # remove .mp4 from filename
    video_name = video_file_name.split(".")[0]

        # cleanup the filename
    video_name_nospaces = video_name.replace(" ", "_")
    video_name_nospaces_noperiods = video_name_nospaces.replace(".", "-")
        # extract the frames from the video
    logger.info("Video identified. Proceeding to copy video.")
    dest_folder = os.path.join(os.getcwd(), 'ARTAK_MM/DATA/Raw_Images/UNZIPPED/' + video_name_nospaces_noperiods)
    count = 1
    saved = False
    while not saved:
            # if the destination folder already exists, increment the -V up one until successfully saving
        if os.path.exists(dest_folder + "-V" + str(count)):
            logger.info("Directory already exists. Sequencing up version.")
            count += 1
            try:
                destination_folder_versioned = dest_folder + "-V" + str(count)
                logger.info("Video destination folder versioned = " + destination_folder_versioned)
                os.makedirs(destination_folder_versioned)
                shutil.copy(video_path, os.path.join(destination_folder_versioned + "/" + os.path.basename(
                        video_path)))
                extract_frames(input_video=destination_folder_versioned + "/" + os.path.basename(
                        video_path),
                                   output_folder=destination_folder_versioned,
                                   logger=logger, frame_spacing=int(frame_spacing))
                folder_name_path = destination_folder_versioned
                saved = True
                return folder_name_path

            except FileExistsError:
                logger.info("Directory already exists. Sequencing up version.")

        else:
            os.makedirs(dest_folder + "-V" + str(count))
            shutil.copy(video_path,
                            os.path.join(dest_folder + "-V" + str(count) + "/" + os.path.basename(video_path)))
            destination_folder_versioned = dest_folder + "-V" + str(count)
            extract_frames(input_video=destination_folder_versioned + "/" + os.path.basename(
                video_path),
                           output_folder=destination_folder_versioned,
                           logger=logger, frame_spacing=int(frame_spacing))

            folder_name_path = os.path.join(dest_folder + "-V" + str(count))
            saved = True
            return folder_name_path
        # add the path of the extracted     frames to the folder paths array to be returned to mapmaker for processing
    # endregion


def sort_files_by_datetime(file_list):
    """
    Sorts a set of image files by the date-time in the exif data

    Args:
        file_list: list of full file paths

    Returns:
    List of files sorted by the exif date-time
    """
    try:
        file_list.sort(key=lambda x: Image.open(x)._getexif().get(36867))
    except:
        print("no exif data")
    return file_list


