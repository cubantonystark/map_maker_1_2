import time
from flask import Flask, request, jsonify
import os
import subprocess
from flask import Flask, render_template, send_file
from flask_cors import CORS, cross_origin
import MM_file_handler
import MM_processing_photogrammetry
from MM_objects import MapmakerProject
from MM_logger import initialize_logger
import MM_services
from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

CORS(app)

app = Flask(__name__)


def handle_new_zip(file, _quality, _maptype, _video_frame_extraction_rate, _partition_key):
    file_name = file
    print('Attempting to UNZIP file. Filename = ' + file)
    log = initialize_logger("testing-zip-upload")
    file_handler = MM_file_handler.MMfileHandler(file, log)
    file = file_handler.unzip()
    print('Completed the UNZIP of file. Filename = ' + file_name)
    print('Completed the UNZIP of file. File = ' + file)
    print('Starting photogrammetry processing = ' + file_name)
    new_project = MapmakerProject(name=file, time_first_image=file_name,
                                  time_mm_start=time.time(),
                                  image_folder=file, total_images=100,
                                  session_project_number=1, map_type=_maptype, status="pending", quality=_quality,
                                  video_frame_extraction_rate=_video_frame_extraction_rate, partition_key=_partition_key
                                  )
    MM_services.add_job_to_que(new_project)


@app.route('/')
def index():
    return render_template('upload.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    target_folder = os.path.join(os.getcwd(), r'ARTAK_MM\DATA\Raw_Images\ZIP\New')
    if not os.path.isdir(target_folder):
        os.makedirs(target_folder)

    if 'file' not in request.files:
        return 'No file uploaded', 400

    file = request.files['file']

    if file.filename == '':
        return 'No file selected', 400

    # Additional form data
    quality = request.form.get('quality')
    mapType = request.form.get('mapType')
    frameRate = request.form.get('frameRate')
    mapPartitionKey = request.form.get('mapPartitionKey')
    timeBetweenSorties = request.form.get('timeBetweenSorties')

    # Process the file and form data here
    # For demonstration, I'm just printing the data
    print("File:", file.filename)
    print("Quality:", quality)
    print("Map Type:", mapType)
    print("Frame Extraction Rate:", frameRate)
    print("Map Partition Key:", mapPartitionKey)
    print("Time Between Sorties:", timeBetweenSorties)

    if file:
        path = os.path.join(target_folder, file.filename)
        file.save(path)
        handle_new_zip(file.filename, quality, mapType, frameRate, mapPartitionKey)

        return jsonify({'message': 'File and data received successfully'}), 200


@app.route('/log', methods=['GET'])
def _log():
    file_path = 'C:/Users/micha/Documents/Coding/Photogrammetry/samples/log.txt'

    # Define a function to read the file and return its contents as a JSON object
    with open(file_path, 'r') as f:
        contents = f.read()
    return jsonify({'file_contents': contents})


if __name__ == '__main__':
    obj_folder = 'path_to_obj_folder'
    folder_path = 'path_to_folder'
    mtl_folder = 'path_to_mtl_folder'
    textures_folder = 'path_to_textures_folder'
    app.run(debug=True, host='0.0.0.0', port=8080)
