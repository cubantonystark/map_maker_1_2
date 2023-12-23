## Script looks for a zip file in the /new folder
## unzips file and begins the group/process pipeline
## usage: API gets zip file from HTTP and places it in the /new folder, then this script handles it

# todo confirm this works with updated scripts


import os
import random
import subprocess
import time
import logging

import MM_file_handler
import MM_processing_photogrammetry
import MM_image_grouper
from MM_objects import MapmakerProject
from MM_logger import initialize_logger
from MM_objects import MapmakerProject

# Define a method to log messages
# def my_method():
#     logger.debug('This is a debug message')
#     logger.info('This is an info message')
#     logger.warning('This is a warning message')
#     logger.error('This is an error message')
#     logger.critical('This is a critical message')

# Call the method to log messages
r = random.Random()
new_id = r.randint(1, 100000)
logger = initialize_logger("CheckFileLoopID" + str(new_id))


def check(logger=""):
    file_name_list = os.listdir(os.getcwd()+"/ARTAK_MM/DATA/Raw_Images/ZIP/New/")
    file_count = len(file_name_list)
    if file_count > 0:
        logger.info('File Located.')
        new_file_exists = True
    else:
        new_file_exists = False
    return new_file_exists, file_name_list


def main_loop(frequency=3, logger=""):
    logger.info('Starting main loop. Frequency = ' + str(frequency))
    while 1:
        new_file_exists, file_name_list = check(logger)
        if new_file_exists:
            for each_file in file_name_list:
                logger.info ('Attempting to UNZIP file. Filename = '+ each_file)
                file_handler = MM_file_handler.MMfileHandler(each_file, logger)
                file = file_handler.unzip()
                logger.info('Completed the UNZIP of file. '
                            'Filename = '+ each_file)
                logger.info('Starting photogrammetry processing = '+ each_file)
                new_project = MapmakerProject(name=each_file, time_first_image=each_file,
                                              time_mm_start=time.time(),
                                              image_folder=each_file, total_images=100, logger=logger,
                                              session_project_number=1, map_type="OBJ"
                                              )
                a = MM_processing_photogrammetry.ProcessingPhotogrammetry(file, logger, mm_project=new_project)
                a.do_photogrammetry()
                time.sleep(5)
        time.sleep(frequency)


main_loop(logger=logger)