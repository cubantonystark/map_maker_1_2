## Script looks for a zip file in the /new folder
## unzips file and begins the group/process pipeline
## usage: API gets zip file from HTTP and places it in the /new folder, then this script handles it

# todo confirm this works with updated scripts


import os
import random
import subprocess
import time
import logging
import shutil
import requests

import MM_file_handler
import MM_processing_photogrammetry
import MM_ingest
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
    file_name_list = os.listdir(os.getcwd()+"/ARTAK_MM/ORCHESTRATOR")
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
                logger.info ('Attempting to send file. Filename = ' + each_file)
                send_file(os.getcwd()+"/ARTAK_MM/ORCHESTRATOR/" + each_file)
                dest = os.getcwd()+"/ARTAK_MM/ARCHIVE/"
                if not os.path.isdir(dest):
                    os.makedirs(os.getcwd()+"/ARTAK_MM/ARCHIVE")
                shutil.move(os.getcwd()+"/ARTAK_MM/ORCHESTRATOR/" + each_file, dest + each_file)
        time.sleep(frequency)

def send_file(zip_file_path):
    receiver_ip = 'http://192.168.1.7:8080/upload'

    # Path to the zip file you want to send
    #zip_file_path = r"C:\Users\micha\Apps\MapMaker6\map_maker_1_2\ARTAK_MM\ORCHESTRATOR\P3460363.zip"

    # Create a dictionary with any additional data you want to send along with the file
    payload = {'key1': 'value1', 'key2': 'value2'}

    try:
        # Create a POST request with the zip file and payload
        with open(zip_file_path, 'rb') as file:
            files = {'file': (zip_file_path, file)}
            response = requests.post(receiver_ip, data=payload, files=files)

        # Check if the request was successful
        if response.status_code == 200:
            print('File sent successfully.')
            print(response.content)
        else:
            print(f'Error sending file. Status code: {response.status_code}')
    except Exception as e:
        print(f'Error: {str(e)}')

main_loop(logger=logger)