from wonderwords import RandomWord
from random import Random
import pandas as pd
import time
from datetime import datetime
import os
import requests
import subprocess
import MM_swarm_control_interface_methods
import threading, time


def connect_drone_to_its_network(drone, arg2):
    if confirm_drone_is_connected_to_its_network(drone):
        print("Drone already connected to it's network interface.")
    else:
        print("Drone not yet connected to it's network interface. Connecting now.")
        MM_swarm_control_interface_methods.connect_network_to_drone(drone.ssid, drone.network_interface)
    url = "http://" + drone.gcs + ":8000/connect_drone"
    print("url = ", url)
    time.sleep(8)
    try:
        a = requests.get(url)
        print("connection response", a)
    except:
        print("error exception caught")


def disconnect_drone_from_its_network(drone, arg2):
    if confirm_drone_is_connected_to_its_network(drone):
        print("Drone is connected to it's network interface.")
        MM_swarm_control_interface_methods.disconnect_network_from_drone(drone.ssid, drone.network_interface)

    else:
        print("Drone not yet connected to it's network interface. Connecting now.")


def confirm_drone_is_connected_to_its_network(drone):
    result = MM_swarm_control_interface_methods.confirm_drone_is_connected_to_network(drone.ssid, drone.network_interface)
    return result


def run_preflight_checks(drone):
    try:
        result = MM_swarm_control_interface_methods.run_preflight_checklist_drone(drone.gcs)
    except:
        return "Failed to reach CGS"
    return result

def confirm_drone_is_accessible_by_gcs(drone):
    result = MM_swarm_control_interface_methods.confirm_drone_is_online(drone.gcs)
    print ("cd =", result)
    return result


def confirm_gcs_is_online(drone):
    result = MM_swarm_control_interface_methods.confirm_gcs_is_online(drone.gcs)
    print ("GCS Online = ", result)
    return result


class Drone:
    def __init__(self, ssid, password, label, network_interface):
        self.ssid = ssid
        self.label = label
        self.password = password
        self.network_interface = network_interface
        self.gcs = "unassigned"
        r = RandomWord()
        self.callsign = r.word(starts_with="a",
                               word_min_length=3,
                               include_parts_of_speech=["nouns"]
                               ) + "0" + str(Random().randint(1, 9))

    def preflight_checklist(self):
        result = eval(run_preflight_checks(self))
        return result

    def confirm_this_drone_is_connected_to_its_network(self):
        result = confirm_drone_is_connected_to_its_network(self)
        print ("Drone -> Network Interface = ", result)

        return result

    def confirm_gcs_is_able_to_access_drone(self):
        result = confirm_drone_is_accessible_by_gcs(self)
        print ("CGS -> Drone Check result = ", result)
        return result

    def confirm_the_gcs_is_online(self):
        result = confirm_gcs_is_online(self)
        print ("Portal -> GCS check result = ", result)
        return result

    def as_tuple(self):
        return (self.callsign, self.ssid, self.password)

    def as_dictionary(self):
        dict = {"label": self.label,
                "callsign": self.callsign,
                "ssid": self.ssid,
                "password": self.password,
                "network_interface": self.network_interface,
                "gcs": self.gcs,
                "wifi_connected_to_drone": self.confirm_this_drone_is_connected_to_its_network(),
                "gcs_online": self.confirm_the_gcs_is_online(),
                "gcs_connected_to_drone": self.confirm_gcs_is_able_to_access_drone(),
                "drone_status": self.preflight_checklist()
                }
        return dict


class GroundControlStation:
    def __init__(self, ip):
        self.ip = ip
        self.assigned_drone = ""
        self.assigned_mission_plan = ""

    def assign_drone(self, drone):
        self.assigned_drone = drone
        drone.gcs = self.ip

    def assign_mission_plan(self, mission_plan):
        self.assigned_mission_plan = mission_plan

    def as_dict(self):
        payload = {"ip": self.ip,
                   "assigned_drone": self.assigned_drone,
                   "assigned_mission": self.assigned_mission_plan}
        return payload


class MissionPlan:
    def __init__(self, name):
        self.name = name

    def as_dict(self):
        payload = {"name": self.name}
        return payload


class SwarmController:

    def __init__(self):
        self.drones = []
        self.ground_control_stations = []
        self.mission_plans = []

    def all_drones_as_list_of_tuples(self):
        payload = []
        for each_drone in self.drones:
            payload.append(each_drone.as_tuple())
        return payload

    def all_drones_as_list_of_dictionaries(self):
        payload = []
        for each_drone in self.drones:
            payload.append(each_drone.as_dictionary())
        return payload

    def all_drones_as_dictionary(self):
        payload = {}
        count = 1
        for each_drone in self.drones:
            payload[count] = each_drone.as_dictionary()
            count += 1
        return payload

    def all_gcs_as_list_of_dictionaries(self):
        payload = []
        for each_gcs in self.ground_control_stations:
            payload.append(each_gcs.as_dict())
        return payload

    def all_gcs_as_dictionary(self):
        payload = {}
        count = 1
        for each_gcs in self.ground_control_stations:
            payload[count] = each_gcs.as_dict()
            count += 1
        return payload

    def all_mission_plans_as_list_of_dictionaries(self):
        payload = []
        for each_plan in self.mission_plans:
            payload.append(each_plan.as_dict())
        return payload

    def add_drones(self, drones):
        for each_drone in drones:
            self.drones.append(each_drone)

    def add_mission_plans(self, mission_plans):
        for each_mission_plan in mission_plans:
            self.mission_plans.append(each_mission_plan)

    def add_ground_control_stations(self, gcs):
        for each_gcs in gcs:
            self.ground_control_stations.append(each_gcs)

    def assign_drone_to_gcs(self, drone, gcs):
        self.ground_control_stations[gcs].assign_drone(self.drones[drone])

    def assign_mission_plan_to_drone_via_gcs(self, plan, gcs):
        print (self.ground_control_stations[1])
        self.ground_control_stations[plan].assign_mission_plan(self.mission_plans[gcs])

    def check_all_drone_connections(self):
        results = {}
        for each_drone in self.drones:
            result = confirm_drone_is_connected_to_its_network(each_drone)
            results[each_drone.label] = result
        return results

    def disconnect_all_drones(self):
        for each_drone in self.drones:
            thread = threading.Thread(target=disconnect_drone_from_its_network, args=(each_drone, 1))
            thread.start()

    def connect_all_drones(self):
        for each_drone in self.drones:
            thread = threading.Thread(target=connect_drone_to_its_network, args=(each_drone, 2))
            thread.start()



def setup_demo():
    # create swarm control object
    swarm = SwarmController()

    # Example Usage
    # create drone object for each drone
    #new_drone1 = Drone("ANAFI-G058795", "", "J", network_interface="Wi-Fi 4")
    new_drone2 = Drone("ANAFI-W", "", "W", network_interface="Wi-Fi 3")
    new_drone3 = Drone("ANAFI-Q", "", "Q", network_interface="Wi-Fi 18")
    new_drone4 = Drone("ANAFI-X", "", "X", network_interface="Wi-Fi")
    new_drone5 = Drone("ANAFI-T", "", "T", network_interface="Wi-Fi 10")
    new_drone6 = Drone("ANAFI-Z", "", "Z", network_interface="Wi-Fi 4")
    new_drone7 = Drone("ANAFI-S", "", "S", network_interface="Wi-Fi 13")
    new_drone8 = Drone("ANAFI-Y", "", "Y", network_interface="Wi-Fi 15")
    new_drone9 = Drone("ANAFI-U", "", "U", network_interface="Wi-Fi 16")

    # create list containing all new drones
    list_of_new_drones = [new_drone2, new_drone3, new_drone4, new_drone5, new_drone6, new_drone7, new_drone8, new_drone9]


    # add list of drones to swarm control object
    swarm.add_drones(list_of_new_drones)

    # create list of ground control stations
    #new_gcs1 = GroundControlStation("192.168.86.132")6
    new_gcs2 = GroundControlStation("192.168.86.138")
    new_gcs3 = GroundControlStation("192.168.86.134")
    new_gcs4 = GroundControlStation("192.168.86.131")
    new_gcs5 = GroundControlStation("192.168.86.135")
    new_gcs6 = GroundControlStation("192.168.86.133")
    new_gcs7 = GroundControlStation("192.168.86.136")
    new_gcs8 = GroundControlStation("192.168.86.137")
    new_gcs9 = GroundControlStation("192.168.86.139")

    list_of_gcs = [new_gcs2, new_gcs3, new_gcs4, new_gcs5, new_gcs6, new_gcs7, new_gcs8, new_gcs9]
    swarm.add_ground_control_stations(list_of_gcs)
    
    # sync drones with ground control stations
    count = 0
    for each_gcs in list_of_gcs:
        swarm.assign_drone_to_gcs(count, count)
        count += 1

    # add mission plan
    new_mission_plan1 = MissionPlan(name="4345234")
    new_mission_plan2 = MissionPlan(name="4345235")
    new_mission_plan3 = MissionPlan(name="4345236")
    new_mission_plan4 = MissionPlan(name="4345236")
    new_mission_plan5 = MissionPlan(name="4345236")
    new_mission_plan6 = MissionPlan(name="4345236")
    new_mission_plan7 = MissionPlan(name="4345236")
    new_mission_plan8 = MissionPlan(name="4345236")

    list_of_mission_plans = [new_mission_plan1, new_mission_plan2, new_mission_plan3, new_mission_plan4, new_mission_plan5, new_mission_plan6, new_mission_plan7, new_mission_plan8]
    swarm.add_mission_plans(list_of_mission_plans)
    count = 0
    for each_mission_plan in list_of_mission_plans:
        swarm.assign_mission_plan_to_drone_via_gcs(count, count)
        count += 1



    return swarm




