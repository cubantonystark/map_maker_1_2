import time
from flask import request, jsonify
import os
from flask_cors import CORS, cross_origin
import MM_file_handler
from MM_objects import MapmakerProject
import MM_job_que
from flask import Flask, render_template
from MM_ingest import handle_new_zip
app = Flask(__name__)

CORS(app)

app = Flask(__name__)





@app.route('/')
def index():
    return render_template('upload.html')


@app.route('/log', methods=['GET'])
def _log():
    file_path = 'C:/Users/micha/Documents/Coding/Photogrammetry/samples/log.txt'

    # Define a function to read the file and return its contents as a JSON object
    with open(file_path, 'r') as f:
        contents = f.read()
    return jsonify({'file_contents': contents})


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


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
