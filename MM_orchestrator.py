from flask import Flask, request, jsonify
import os
import subprocess
from flask import Flask, render_template, send_file
from flask_cors import CORS, cross_origin
import requests
app = Flask(__name__)

CORS(app)
from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_file():
    target_folder = r'C:\Users\micha\Apps\MapMaker6\map_maker_1_2\ARTAK_MM\ORCHESTRATOR'
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




if __name__ == '__main__':

    app.run(debug=True, host='0.0.0.0', port=8001)
