import cv2
import os


def extract_frames(input_video, output_folder, frame_interval=1):
    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Open the video file
    cap = cv2.VideoCapture(input_video)
    if not cap.isOpened():
        print("Error: Cannot open the video file.")
        return

    # Get the frames per second (fps) of the video
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    # Calculate the number of frames to skip to get frames every 'frame_interval' seconds
    frames_to_skip = fps * frame_interval

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

        frame_number += 1

    # Release the video file and close any open windows
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    # Replace 'input_video_path' with the path to your input video file
    input_video_path = "C:/Users/micha/Downloads/SHERMAN2.MP4"

    # Replace 'output_folder_path' with the desired output folder path
    output_folder_path = "C:/test"

    # Extract frames every 1 second (change 'frame_interval' as needed)
    extract_frames(input_video_path, output_folder_path, frame_interval=1)
