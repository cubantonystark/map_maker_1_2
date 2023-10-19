import os


def upload_to_world(zip_payload_location):
    os.system(
        r'curl -F uploadFile=@' + zip_payload_location + ' -F partition_key='' http://tileserver.eastus2.cloudapp.azure.com/api/upload-tileset -H "Content-Type: multipart/form-data"')

upload_to_world(r"C:\Users\micha\Apps\MapMaker6\map_maker_1_2\ARTAK_MM\POST\Photogrammetry\2B_1_dehazed-V3465\Productions\Production_1 (3)\Scene\UnderwaterTest.zip")