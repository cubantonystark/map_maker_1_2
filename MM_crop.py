from moviepy.editor import VideoFileClip
import os
# MK46-03.m4v 2B2.m4v
#input_videos_dir = r"C:\Users\micha\Downloads\Enhanced\crop-bottom" # type1
input_videos_dir = r"C:\Users\micha\Downloads\Enhanced\f1" # type1
#input_videos_dir = r"C:\Users\micha\Downloads\Enhanced\crop-sonarandbot" # type2
#input_videos_dir = r"C:\Users\micha\Downloads\Enhanced\crop-sonarLargeandbot" # type3
#input_videos_dir = r"C:\Users\micha\Downloads\Enhanced\crop-bottomright" # type4
bottom = 1000
#bottom = 920 # type4
top = 0 # type 1
#top = 240 # type 2
#top = 360 # type 3
#top = 0 # type 4
right = 2432
left = 0

def crop_video(input_path, output_path, left, right, top, bottom):
    video_clip = VideoFileClip(input_path)
    cropped_clip = video_clip.crop(x1=left, x2=right, y1=top, y2=bottom)
    cropped_clip.write_videofile(output_path, codec='libx264')

for i in os.listdir(input_videos_dir):
     input_video_path = input_videos_dir + "/" + i
     output_video_path = os.path.join(r'C:\Users\micha\Downloads\Enhanced\cropped' , i)
     crop_video(input_video_path, output_video_path, left, right, top, bottom)
