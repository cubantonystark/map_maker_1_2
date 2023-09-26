import os


def upload(path):
    os.system(
        r'curl -F uploadFile=@' + path + ' -F partition_key= https://resqview.eastus2.cloudapp.azure.com/api/upload-tileset -H "Content-Type: multipart/form-data"')


_path = r"C:\Users\micha\OneDrive\Desktop\MauiFire.zip"
upload(_path)   