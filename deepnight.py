import os

folder = "c:/MyVideos"
destination_folder = "c:/MyVideos"
for i in os.listdir(folder):
    file = os.path.join(folder, i)
    dest = os.path.join(destination_folder, i)
    print("Performing Deep Night Underwater Image Enhancement on " + file)
    command = "scp " + str(file) + " " + str(dest)
  #  command = "python3 uie.py " + str(file) + " " + str(dest)
    print ("Running command :" + str(command))
    os.system(command)
    print("Successfully Enhanced " + str(dest))
