import requests
import time
from datetime import datetime
import os
import requests
import subprocess
import re


def parse_wifi_networks(content):
    network_list = []
    network_info_list = re.split(r'\n\n', content)

    for network_info in network_info_list:
        lines = network_info.split('\n')
        lines = lines[1:]
        count = 0
        for line in lines:
            load = {}
            if "Name" in line:
                count += 1
            network = {}
            if line.strip() and ':' in line:
                key, value = map(str.strip, line.split(':', 1))
                network[key] = value
            network_list.append(network)
        payload = {}
        count = 0
        name_cache = "na"
        load = {}
        data_list = []
        for i in network_list[2:]: #run through list of dicts
            for each_key in i.keys(): # run thru keys to check if a new name line is found
                if each_key == "Name":
                    name_cache = i[each_key]
                    data_list = []

            data_list.append(i)
            load[name_cache] = data_list
    listPayload = []
    for i in load.items():
        payload = {}
        for each_item in i[1]:
            for each_key in each_item.keys():
                payload[each_key] = each_item[each_key]
        listPayload.append(payload)
    newPayload = {}
    for i in listPayload:
        name = i["Name"]
        newPayload[name] = i
    return newPayload


def run_preflight_checklist_drone(gcs_ip):
    a = requests.get("http://" + gcs_ip + ":8000/mag", timeout=5)

    print("content = ", a.content.decode())
    return a.content.decode()

def confirm_drone_is_connected_to_network(network_name, interface_name):
    # Get the wireless interface details
    wlan_command = f'netsh wlan show interfaces name="{interface_name}"'
    wlan_output = subprocess.check_output(wlan_command, shell=True).decode()
    networkInfoDict = parse_wifi_networks(wlan_output)
    interface_info = networkInfoDict[interface_name]
    try:
        if interface_info["SSID"] == network_name:
            print ("connected")
            return True
    except:
        return False


def connect_network_to_drone(ssid, network_interface):
    command = 'netsh wlan connect name='+ ssid + ' ssid=' + ssid + ' interface="'+ network_interface + '"'
    print("Attempting to connect ", network_interface, " to " + ssid)
    print("Sending system command: +", command)
    os.system(command)


def disconnect_network_from_drone(ssid, network_interface):
    command = 'netsh wlan disconnect interface="'+ network_interface + '"'
    print("Attempting to disconnect ", network_interface)
    os.system(command)

def takeoff_land_test():
    requests.get('http://192.168.86.138:8000/take_off_and_land')
    requests.get('http://192.168.86.134:8000/take_off_and_land')
    requests.get('http://192.168.86.131:8000/take_off_and_land')
    requests.get('http://192.168.86.135:8000/take_off_and_land')


def get_images():
    requests.get('http://192.168.86.131:8000/retrieve_images')
    requests.get('http://192.168.86.133:8000/retrieve_images')
    requests.get('http://192.168.86.134:8000/retrieve_images')
    requests.get('http://192.168.86.135:8000/retrieve_images')
    requests.get('http://192.168.86.136:8000/retrieve_images')
    requests.get('http://192.168.86.137:8000/retrieve_images')
    requests.get('http://192.168.86.138:8000/retrieve_images')
    requests.get('http://192.168.86.139:8000/retrieve_images')


def confirm_gcs_is_online(gcs_ip):
    try:
        print("Confirming GCS is online")
        print("ip =", gcs_ip)
        a = requests.get("http://" + gcs_ip + ":8000", timeout=5)
        print("GCS Online")
        return True
    except:
        print("GCS Offline")
        return False


def confirm_drone_is_online(gcs_ip):
    try:
        print("Confirming Drone is online")
        print("ip =", gcs_ip)
        a = requests.get("http://" + gcs_ip + ":8000/check_drone", timeout=5)
        print("content = ", a.content.decode())
        if a.content.decode() == "connected":
            print(" a == connected")
            return True
        else:
            print(" a != connected")
            return False
    except:
        print("HTTP Error")
        return False


def confirm_drones_are_online():
    print("Confirming Drone is online for Each Drone in Swarm 'MAYFLY01'")
    a = requests.get('http://192.168.86.132:8000/check_drone')  
    print (a.content)
    if a.content == "connected":
        print("connected")
    else:
        state = "notConnected"
    a = requests.get('http://192.168.86.138:8000/check_drone')
    print (a.content)
    if a.content == "connected":
        state = "notConnected"
    a = requests.get('http://192.168.86.133:8000/check_drone')
    print (a.content)
    if a.content == "connected":
        state = "notConnected"
    a = requests.get('http://192.168.86.134:8000/check_drone')
    print (a.content)
    if a.content == "connected":
        state = "notConnected"
    a = requests.get('http://192.168.86.131:8000/check_drone')
    print (a.content)
    if a.content == "connected":
        state = "notConnected"
    a = requests.get('http://192.168.86.135:8000/check_drone')
    print (a.content)
    if a.content == "connected":
        state = "notConnected"
    if state == "notConnected":
        return False
    return True





def north_orbit_test():
    print("Initializing Takeoff Sequence on Swarm MAYFLY01")
    # R, Q L, O
    subprocess.Popen(['curl',
                      'http://192.168.86.135:8000//webform?Latitude=27.8877&Longitude=-82.7344&Address=&FlightType=orbit&Quality=Low&SendToDrone=yes&SelectDrone=a'])
    #time.sleep(4)
#    subprocess.Popen(['curl',
#                      'http://192.168.86.132:8000//webform?Latitude=27.8876&Longitude=-82.7264&Address=&FlightType=orbit&Quality=Low&SendToDrone=yes&SelectDrone=a'])
#    time.sleep(4)
    subprocess.Popen(['curl',
                      'http://192.168.86.134:8000//webform?Latitude=27.8876&Longitude=-82.7302&Address=&FlightType=orbit&Quality=Low&SendToDrone=yes&SelectDrone=a'])
   # time.sleep(4)
    subprocess.Popen(['curl',
                      'http://192.168.86.138:8000//webform?Latitude=27.8877&Longitude=-82.7265&Address=&FlightType=orbit&Quality=Low&SendToDrone=yes&SelectDrone=a'])
  #  time.sleep(4)
    subprocess.Popen(['curl',
                      'http://192.168.86.131:8000//webform?Latitude=27.8874&Longitude=-82.7229&Address=&FlightType=orbit&Quality=Low&SendToDrone=yes&SelectDrone=a'])

    print("Takeoff Sequence Initialized. 10 Seconds to Launch")
    time.sleep(5)
    print("T-5")
    time.sleep(1)
    print("T-4")
    time.sleep(1)
    print("T-3")
    time.sleep(1)
    print("T-2")
    time.sleep(1)
    print("T-1 Second")
    time.sleep(1)
    print("Liftoff")

def     dynamic_orbit_test_lq(urls):
    print("Initializing Takeoff Sequence on Swarm MAYFLY01")
    # X Z Q R S Y W U
    subprocess.Popen(['curl',
                      'http://192.168.86.131:8000//' + urls[0]])
    time.sleep(3)
    subprocess.Popen(['curl',
                      'http://192.168.86.133:8000//' + urls[1]])
    time.sleep(3)
    subprocess.Popen(['curl',
                      'http://192.168.86.134:8000//' + urls[2]])
    time.sleep(3)
    subprocess.Popen(['curl',
                      'http://192.168.86.135:8000//' + urls[3]])
    time.sleep(3)
    subprocess.Popen(['curl',
                      'http://192.168.86.136:8000//' + urls[4]])
    time.sleep(3)
    subprocess.Popen(['curl',
                      'http://192.168.86.137:8000//' + urls[5]])
    time.sleep(3)
    subprocess.Popen(['curl',
                      'http://192.168.86.138:8000//' + urls[6]])
    time.sleep(3)
    subprocess.Popen(['curl',
                      'http://192.168.86.139:8000//' + urls[7]])

    print("Takeoff Sequence Initialized. 10 Seconds to Launch")


def south_orbit_test():
    state = confirm_drones_are_online()
    if state == "n":
        print("all drones not connected")
        pass
    else:
        print ("Initializing Takeoff Sequence on Swarm MAYFLY01")
        subprocess.Popen(['curl', 'http://192.168.86.132:8000//webform?Latitude=27.889&Longitude=-82.7301&Address=&FlightType=orbit&Quality=High&SendToDrone=yes&SelectDrone=a'])
        time.sleep(2)
        subprocess.Popen(['curl', 'http://192.168.86.135:8000//webform?Latitude=27.8891&Longitude=-82.7302&Address=&FlightType=orbit&Quality=Low&SendToDrone=yes&SelectDrone=a'])
        time.sleep(2)
        subprocess.Popen(['curl', 'http://192.168.86.138:8000//webform?Latitude=27.8859&Longitude=-82.7284&Address=&FlightType=orbit&Quality=High&SendToDrone=yes&SelectDrone=a'])

        print("Takeoff Sequence Initialized. 10 Seconds to Launch")
        time.sleep(5)
        print("T-5")
        time.sleep(1)
        print("T-4")
        time.sleep(1)
        print("T-3")
        time.sleep(1)
        print("T-2")
        time.sleep(1)
        print("T-1 Second")    
        time.sleep(1)
        print("Liftoff")


#a = confirm_drones_are_online()
#print (a)