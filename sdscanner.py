import os
import time
import threading
from random import random

import win32file
import MM_image_grouper
import MM_processing_photogrammetry
import logging

from map_maker_1_2 import MM_logger


def detect_sd_card():
    drive_list = []
    drives = win32file.GetLogicalDrives()

    for drive in range(1, 26):
        mask = 1 << drive
        if drives & mask:
            drive_letter = chr(ord('A') + drive)
            try:
                drive_type = win32file.GetDriveType(drive_letter + ":\\")
                if drive_type == win32file.DRIVE_REMOVABLE:
                    drive_list.append(drive_letter)
            except Exception:
                pass

    return drive_list


def print_sd_card_files(drive_letter):
    path = drive_letter + ":\\DCIM\\100MEDIA\\"
    try:
        files = os.listdir(path)
        print(f"Files on {path}:")
        for file in files:
            print(file)
        foldename = MM_image_grouper.group_images(path)
        r = random.Random()
        session_id = r.randint(1, 10000000)
        logger = MM_logger.initialize_logger("SessionLog" + str(session_id))
        themap = input("(1) OBJ or (2) Cesium :")
        print(themap)
        delete_after = input("Delete from SD Card after Transfer? (Y) YES or (N) NO :")
        print (themap, " ", delete_after )
        if delete_after == "Y":
            for f in files:
                os.remove(path+f)
        if themap == "1":
            a = MM_processing_photogrammetry.ProcessingPhotogrammetry(foldename, logger=logger)
        if themap == "2":
            a = MM_processing_photogrammetry.ProcessingPhotogrammetry(foldename, logger=logger, _cesium=True)
        a.do_photogrammetry()


    except Exception as e:
        print(f"Error accessing files on {path}: {e}")


def sd_card_monitor():
    while True:
        drives_before = set(detect_sd_card())
        time.sleep(1)
        drives_after = set(detect_sd_card())
        new_drives = drives_after - drives_before
        for drive_letter in new_drives:
            threading.Thread(target=print_sd_card_files, args=(drive_letter,)).start()


if __name__ == "__main__":
    threading.Thread(target=sd_card_monitor).start()
    input("Press Enter to exit...\n")
