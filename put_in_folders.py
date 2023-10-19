import os
import shutil

path = "C:/MapMaker-SapmleDatasets/PhotogrammetryDatasets/Underwater/Videos/NIWIC_Dehazed/Cropped"

for i in os.listdir(path):
    print (i)
    os.mkdir("folders"+ "/" + i)
    shutil.copy(path + "/" + i, "./folders/" + i + "/" + i)