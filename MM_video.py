import cv2
import os
import MM_logger

def extract_frames(input_video, output_folder, frame_interval=1, logger=MM_logger.initialize_logger(), frame_spacing=30):

    if frame_spacing == "":
        frame_spacing = 20
    logger.info("extracting frames")
    # Create the output folder if it doesn't exist
    og_path = output_folder
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
                finished = True
            except:
                print("trying again")
        else:
            destination_folder_versioned = og_path + "-V" + str(count)
            os.makedirs(destination_folder_versioned)
            folder_path = destination_folder_versioned
            finished = True

    logger.info("Attempting to make directory " + str(folder_path))
    logger.info("Successfully made directory " + str(folder_path))
    output_folder = folder_path
    os.makedirs(output_folder, exist_ok=True)

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
    payload_file_folder_name = folder_path.split("/")[len(folder_path.split("/"))-1].split(".")[0]
    return payload_file_folder_name
#
# if __name__ == "__main__":
#     # Replace 'input_video_path' with the path to your input video file
#     input_video_path = "C:/MapMaker-SapmleDatasets/PhotogrammetryDatasets/Outdoors/Videos/EO-Anafi/Sherman/SHERMAN2.MP4"
#
#     # Replace 'output_folder_path' with the desired output folder path
#     output_folder_path = "C:/test"
#
#     # Extract frames every 1 second (change 'frame_interval' as needed)
#     extract_frames(input_video_path, output_folder_path, frame_interval=1)
