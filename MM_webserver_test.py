import os

import requests

#source = r"C:\MapMaker-SapmleDatasets\PhotogrammetryDatasets\Outdoors\Images_geotagged\EO-Anafi\13Images\images\autotest"
source = r"C:\Users\micha\Downloads\Enhanced\cropped\New folder"


def send_file(zip_file_path):
    receiver_ip = 'http://192.168.1.7:8080/upload'

    # Path to the zip file you want to send
    #zip_file_path = r"C:\Users\micha\Apps\MapMaker6\map_maker_1_2\ARTAK_MM\ORCHESTRATOR\P3460363.zip"

    # Create a dictionary with any additional data you want to send along with the file
    payload = {'key1': 'value1', 'key2': 'value2'}

    try:
        # Create a POST request with the zip file and payload
        with open(zip_file_path, 'rb') as file:
            files = {'file': (zip_file_path, file)}
            response = requests.post(receiver_ip, data=payload, files=files)

        # Check if the request was successful
        if response.status_code == 200:
            print('File sent successfully.')
            print(response.content)
        else:
            print(f'Error sending file. Status code: {response.status_code}')
    except Exception as e:
        print(f'Error: {str(e)}')

for i in os.listdir(source):
    send_file(os.path.join(source, i))