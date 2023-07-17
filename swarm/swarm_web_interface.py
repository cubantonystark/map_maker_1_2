import pandas as pd
from flask import Flask, render_template, send_file
import swarm_orchestrator
import MM_swarm_control_interface_methods
from flask import jsonify
from flask_cors import CORS, cross_origin
from my_location import get_my_position
import requests
from flask import request
import geo_math
import plot_on_map

app = Flask(__name__, static_url_path="/")

test_swarm = swarm_orchestrator.setup_demo()
CORS(app)
from markupsafe import escape

@app.route('/')
@cross_origin(origins='*')
def index():
    return render_template('map.html')

@app.route('/get_positions')
@cross_origin()
def get_positions():
    try:
        iss_response = requests.get('http://api.open-notify.org/iss-now.json').json()
    except:
        iss_response = {'iss_position': {'latitude': "0", 'longitude': "0"}}
    noaa17_response = {'noaa17_position': {'latitude': "44", 'longitude': "27"}}  # Replace with actual NOAA-17 API endpoint
    try:
        my_position = {'my_position': {'latitude': "0", 'longitude': "0"}}


        # my_position = get_my_position()
    except:
        my_position = {'my_position': {'latitude': "0", 'longitude': "0"}}

    try:
        iss_position = {
            'latitude': float(iss_response['iss_position']['latitude']),
            'longitude': float(iss_response['iss_position']['longitude'])
        }
        noaa17_position = {
            'latitude': float(0),
            'longitude': float(0)
        }

        my_position = {
            'latitude': float(0),
            'longitude': float(0)
       }
        return jsonify(iss_position=iss_position, noaa17_position=noaa17_position, my_position=my_position)
    except:
        return "error"
@app.route('/status')
def status():
    return "online"

@app.route('/all_drones')
def all_drones():
    my_dict = test_swarm.all_drones_as_dictionary()
    print (my_dict)
    df = pd.DataFrame.from_records(my_dict)
    #df = pd.DataFrame.from_dict(my_dict, orient='index', columns=['Value'])
    table = df.to_html()
    print (table)
    return table

@app.route('/kml')
def _kml():
    return send_file("KML_Samples.kml",mimetype='application/vnd.google-earth.kml+xml')

@app.route('/all_gcs')
def all_gcs():
    my_dict = test_swarm.all_gcs_as_dictionary()
    print (my_dict)
    df = pd.DataFrame.from_records(my_dict)
    #df = pd.DataFrame.from_dict(my_dict, orient='index', columns=['Value'])
    table = df.to_html()
    print (table)
    return table


@app.route('/commands')
def commands():

    return '<a href ="/connect_all" target="_blank">Connect All Drones</a><br>' \
           '<a href ="/all_drones" target="_blank">Pre-flight Checks</a><br>' \
           '<a href ="/takeoff_and_land_test" target="_blank">Commence Test Maneuver: Liftoff, Hover, and Land </a><br>' \
           '<a href ="/north_test_orbits" target="_blank">Commence Test Recon Mission: North Orbit </a><br>' \
           '<a href ="/retrieve_images" target="_blank">Retrieve Images from All Drones</a><br>'


@app.route('/retrieve_images')
def retrieve_images():
    MM_swarm_control_interface_methods.get_images()
    return "connecting"

@app.route('/cesium')
@cross_origin(origins='*')
def _cesium():
    return render_template('index.html')

@app.route('/map_this')
def _map_this():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    urls, coordinates = geo_math.cut_up_map(float(lat), float(lon))
    plot_on_map.plot_coordinates_on_map(coordinates, "testmap.html")
    MM_swarm_control_interface_methods.dynamic_orbit_test_lq(urls)
    return "sending something"

@app.route('/logo')
def _logo():
    return send_file('logo.png')


@app.route('/connect_all')
def connect_all():
    test_swarm.connect_all_drones()
    return "connecting"

@app.route('/disconnect_all')
def disconnect_all():
    test_swarm.disconnect_all_drones()
    return "disconnecting"

@app.route('/check_drone_wifi_connections')
def check_drone_wifi_connections():
    results = test_swarm.check_all_drone_connections()
    return results


@app.route('/takeoff_and_land_test')
def takeoff_and_land_test():
    MM_swarm_control_interface_methods.takeoff_land_test()
    return "Initializing Takeoff and Land Test."


@app.route('/north_test_orbits')
def north_test_orbits():
    MM_swarm_control_interface_methods.north_orbit_test()
    return "Sending the Swarm to the North."

@app.route('/north_test_orbits_hq')
def north_test_orbits_hq():
    MM_swarm_control_interface_methods.north_orbit_test_hq()
    return "Sending the Swarm to the North."

@app.route('/confirm_drones_online')
def confirm_drones_online():
    MM_swarm_control_interface_methods.confirm_drones_are_online()
    return "Sending the Swarm to the North."

@app.route('/all_mission_plans')
def all_mission_plans():
    my_dict = test_swarm.all_mission_plans_as_list_of_dictionaries()
    print (my_dict)
    df = pd.DataFrame.from_records(my_dict)
    #df = pd.DataFrame.from_dict(my_dict, orient='index', columns=['Value'])
    table = df.to_html()
    print (table)
    return table


if __name__ == '__main__':
    app.run(debug=True, port=5000)