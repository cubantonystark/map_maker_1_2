import os

file_path = 'C:/Users/micha/Apps/MapMaker6/map_maker_1_2\ARTAK_MM\POST\Photogrammetry/2021-12-12_09-23-03287\Productions\Production_1'
os.system("cd " + file_path)
os.system(file_path + "python -m http.server")




