import os

from moviepy.editor import VideoFileClip


def crop_bottom_of_video(input_video_path, output_video_path, crop_height):
    # Load the video
    video = VideoFileClip(input_video_path)

    # Calculate the cropping
    crop_area = (0, 0, video.size[0], video.size[1] - crop_height)

    # Crop the video
    cropped_video = video.crop(x1=crop_area[0], y1=crop_area[1], x2=crop_area[2], y2=crop_area[3])

    # Write the result to a file
    cropped_video.write_videofile(output_video_path, codec="libx264", audio_codec="aac")



crop_height = 50  # Height in pixels to crop from the bottom
path = r"C:\Users\micha\Downloads\Enhanced\crop-bottom"
output_path = r"C:\Users\micha\Downloads\Enhanced\cropped"
for i in os.listdir(path):
    input_video = os.path.join(path, i)
    output_video = os.path.join(output_path, i)
    crop_bottom_of_video(input_video, output_video, crop_height)
