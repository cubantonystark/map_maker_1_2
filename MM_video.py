import cv2
import os
import MM_logger

video_extensions = ['.mpeg', '.mp4', '.ts', ".m4v"]

def extract_frames(input_video, output_folder, frame_interval=1, logger=MM_logger.initialize_logger(), frame_spacing=90):

    if frame_spacing == "":
        frame_spacing = 20
    logger.info("extracting frames")
    # # Create the output folder if it doesn't exist
    # og_path = output_folder
    # destination_folder_versioned = output_folder
    # count = 1
    # finished = False
    # while not finished:
    #     path = og_path + "-V" + str(count)
    #     logger.info("OGPath = " + og_path)
    #     logger.info("Path = " + path)
    #     if os.path.exists(path):
    #         logger.info("Directory already exists. Sequencing up version.")
    #         count += 1
    #         try:
    #             destination_folder_versioned = og_path + "-V" + str(count)
    #             logger.info("Destination folder versioned = " + destination_folder_versioned)
    #             os.makedirs(destination_folder_versioned)
    #             folder_path = destination_folder_versioned
    #             finished = True
    #         except:
    #             print("trying again")
    #     else:
    #         destination_folder_versioned = og_path + "-V" + str(count)
    #         os.makedirs(destination_folder_versioned)
    #         folder_path = destination_folder_versioned
    #         finished = True
    #
    # logger.info("Attempting to make directory " + str(folder_path))
    # logger.info("Successfully made directory " + str(folder_path))
    # output_folder = folder_path
    # os.makedirs(output_folder, exist_ok=True)

    # Open the video file
    cap = cv2.VideoCapture(input_video)
    if not cap.isOpened():
        logger.info("Error: Cannot open the video file.")
        return

    # Get the frames per second (fps) of the video
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    # Calculate the number of frames to skip to get frames every 'frame_interval' seconds
    logger.info("Video FPS:  " + str(fps))
    logger.info("Frame Extraction Rate (in seconds):  " + str(frame_interval))

    # frames_to_skip = fps * frame_interval
    frames_to_skip = frame_spacing
#    frames_to_skip = 90

    frame_number = 0
    while True:
        # Read a frame from the video
        ret, frame = cap.read()

        if not ret:
            break  # Break the loop if the video has ended

        # Check if the current frame number is within the desired interval
        if frame_number % frames_to_skip == 0:
            # Save the frame as an image in the output folder
            output_path = os.path.join(output_folder, f"frame_{frame_number}.jpg")
            cv2.imwrite(output_path, frame)
            logger.info("Extracted frame " + str(frame_number))
        frame_number += 1

    # Release the video file and close any open windows
    cap.release()
    cv2.destroyAllWindows()
    return "OK"


def list_of_videos_in_folder(directory):
    video_list = []
    for i in os.listdir(directory):
        for each_extension in video_extensions:
            if each_extension in i.lower():
                video_i_path = os.path.join(directory, i)
                video_list.append(video_i_path)
    return video_list

def folder_contains_videos(directory):
    for i in os.listdir(directory):
        for each_extension in video_extensions:
            if each_extension in i.lower():
                return True
    return False


def is_video(file_path):
    for each_extension in video_extensions:
        if each_extension in file_path.lower():
            return True
    return False
