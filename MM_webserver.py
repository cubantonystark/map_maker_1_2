from flask import Flask, request, jsonify
import os
import subprocess
from flask import Flask, render_template, send_file
from flask_cors import CORS, cross_origin

app = Flask(__name__)

CORS(app)
from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('obj.html')

# @app.route('/files/<path:filename>')
# def serve_file(filename):
#     return send_from_directory('folder_path', filename)

@app.route('/upload', methods=['POST'])
def upload_file():
    target_folder = r'C:\Users\micha\Apps\MapMaker6\map_maker_1_2\ARTAK_MM\DATA\Raw_Images\ZIP\New'
    if not os.path.isdir(target_folder):
        os.makedirs(target_folder)

    if 'file' not in request.files:
        return 'No file uploaded', 400

    file = request.files['file']
    if file.filename == '':
        return 'No file selected', 400

    if file:
        filename = os.path.basename(file.filename)
        path = os.path.join(target_folder, filename)
        file.save(path)
        return ' successfully' + str(path), 200

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
