import requests
import time
from datetime import datetime
import os
import requests
import subprocess
print ("ARTAK Drone Swarm Command Line Test Interface")
print (".............................................")
#print ("GREETINGS PROFESSOR FALKEN")
#print ("SHALL WE PLAY A GAME?")
print ("PLEASE SELECT FUNCTION TO TEST")


def connect_network_to_drone():
    os.system

def connect_swarm():
    print("Connecting to All Drones in Swarm 'MAYFLY01'")
    os.system('netsh wlan connect name=NETGEAR71 ssid=NETGEAR71 interface="Wi-Fi "')
    os.system('netsh wlan connect name=ANAFI-G040477 ssid=ANAFI-G040477 interface="Wi-Fi 3"')
    os.system('netsh wlan connect name=ANAFI-G058795 ssid=ANAFI-G058795 interface="Wi-Fi 4"')
    os.system('netsh wlan connect name=ANAFI-G059285 ssid=ANAFI-G059285 interface="Wi-Fi 2"')

    time.sleep(10)

    print("Confirming API is online for Each Drone in Swarm 'MAYFLY91'")
  #  assert requests.get('http://192.168.86.133:8000')
    assert requests.get('http://192.168.86.132:8000')
    assert requests.get('http://192.168.86.131:8000')
    assert requests.get('http://192.168.86.138:8000')

    time.sleep(20)
    print ("Pre-check: Pass - All APIs are Online.")

    print("Confirming Drone is online for Each Drone in Swarm 'MAYFLY01'")
    a = confirm_drones_are_online()
    if a == "notConnected":
        print ("Pre-check: FAIL - All Drones are NOT Online.")

    else:
        print ("Pre-check: PASS - All Drones are Online.")


def takeoff_land_test():
    requests.get('http://192.168.86.131:8000/take_off_and_land')
    requests.get('http://192.168.86.132:8000/take_off_and_land')
    requests.get('http://192.168.86.133:8000/take_off_and_land')

def get_images():
    print("Retrieving Images in 5 Seconds.")
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
    requests.get('http://192.168.86.131:8000/retrieve_images')
    requests.get('http://192.168.86.132:8000/retrieve_images')
   # requests.get('http://192.168.86.133:8000/retrieve_images')
    requests.get('http://192.168.86.138:8000/retrieve_images')

def confirm_drones_are_online():
    print("Confirming Drone is online for Each Drone in Swarm 'MAYFLY01'")
  #  a = requests.get('http://192.168.86.133:8000/check_drone')
  #  state = "connected"
  #  print (a.content)
  #  if a.content == "connected":
  #      print("connected")
  #  else:
  #      state = "notConnected"
    a = requests.get('http://192.168.86.132:8000/check_drone')  
    print (a.content)
    if a.content == "connected":
        print("connected")
    else:
        state = "notConnected"
    a = requests.get('http://192.168.86.131:8000/check_drone')
    print (a.content)
    if a.content == "connected":
        print("connected")
    else:
        state = "notConnected"
    a = requests.get('http://192.168.86.138:8000/check_drone')
    print (a.content)
    if a.content == "connected":
        print("connected")
    else:
        state = "notConnected"
    return state

print ("Pre-check: Pass - All Drones are Online.")
def south_orbit_test():
    state = confirm_drones_are_online()
    if state == "n":
        print("all drones not connected")
        pass
    else:
        print ("Initializing Takeoff Sequence on Swarm MAYFLY01")
        subprocess.Popen(['curl', 'http://192.168.86.132:8000//webform?Latitude=27.889&Longitude=-82.7301&Address=&FlightType=orbit&Quality=High&SendToDrone=yes&SelectDrone=a'])
     #   time.sleep(2)
     #   subprocess.Popen(['curl', 'http://192.168.86.133:8000//webform?Latitude=27.8891&Longitude=-82.7302&Address=&FlightType=orbit&Quality=Low&SendToDrone=yes&SelectDrone=a'])
      #  time.sleep(2)
        subprocess.Popen(['curl', 'http://192.168.86.131:8000//webform?Latitude=27.8909&Longitude=-82.726&Address=&FlightType=orbit&Quality=High&SendToDrone=yes&SelectDrone=a'])
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

while 1==1:
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    print("Current Time =", dt_string, "EST")
    a = input("(1) Connect Swarm (2) Send Drones (3) Retrieve Images  : ")

    if a == "1":
      #  i = input("How about a nice game of chess?")
      
      #  if i == "ok":
      #      pass
        connect_swarm()
        
    if a == "2":
      #  i = input("How about a nice game of chess?")
     #   if i == "ok":
     #       pass
        south_orbit_test()
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        print("Wheels Up @ =", dt_string)
            
    if a=="3":
       # i = input("How about a nice game of chess?")
       # if i == "ok":
       #     pass
        now = datetime.now()
        start = now.strftime("%d/%m/%Y %H:%M:%S")
        print("Extracting Images. Start time =", start)
        get_images()
    
