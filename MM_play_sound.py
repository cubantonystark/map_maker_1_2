import playsound
import os


def play_sound_processing_complete():
    playsound.playsound(os.path.join(os.getcwd(), "completed.wav"))
    print ("playing sound: completed ")
def play_sound_processing_started():
    playsound.playsound(os.path.join(os.getcwd(), "apocalypse_mission.wav"))
    print ("playing sound: started ")

play_sound_processing_complete()
play_sound_processing_complete()
play_sound_processing_complete()