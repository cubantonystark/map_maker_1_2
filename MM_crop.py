from moviepy.editor import VideoFileClip
import os

input_videos_dir = "C:/MapMaker-SapmleDatasets/PhotogrammetryDatasets/Underwater/Videos/NIWIC_Dehazed/NeedsCropping"
bottom = 1000
# top = 240 # type 1
top = 0 # type 2
right = 2432
left = 0

def crop_video(input_path, output_path, left, right, top, bottom):
    video_clip = VideoFileClip(input_path)
    cropped_clip = video_clip.crop(x1=left, x2=right, y1=top, y2=bottom)
    cropped_clip.write_videofile(output_path, codec='libx264')

for i in os.listdir(input_videos_dir):
     input_video_path = input_videos_dir + "/" + i
     output_video_path = "C:/cropped/" + i
     crop_video(input_video_path, output_video_path, left, right, top, bottom)
