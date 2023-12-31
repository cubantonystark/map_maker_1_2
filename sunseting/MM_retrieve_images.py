import olympe
from olympe.messages.camera import take_photo, photo_taken

# Connect to the drone
drone = olympe.Drone("192.168.42.1")
drone.connect()

# Take a photo and wait for it to be taken
photo_saved = drone(
    take_photo(cam_id=0)
    >> photo_taken()
).wait()

# Get the path to the saved photo
photo_path = photo_saved.received_events()[0].message["mediaUrl"]

# Download the photo
drone.media.download(photo_path, "./photo.jpg")

# Disconnect from the drone
drone.disconnect()
