import os


def upload(path):
    os.system(r'curl -F uploadFile=@' + path + ' -F partition_key=mapmakertest http://cesium.eastus2.cloudapp.azure.com:3000/api/upload-tileset -H "Content-Type: multipart/form-data"')


_path = r"C:\Users\micha\Apps\MapMaker6\map_maker_1_2\ARTAK_MM\POST\Photogrammetry\2023-07-10_20-58-1773\Productions\Production_1\13ImagesV6.zip"
upload(_path)