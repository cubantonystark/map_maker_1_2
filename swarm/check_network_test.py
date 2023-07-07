import re
import subprocess


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


def check_network_interface(interface_name, network_name):
    # Get the wireless interface details
    wlan_command = f'netsh wlan show interfaces name="{interface_name}"'
    wlan_output = subprocess.check_output(wlan_command, shell=True).decode()
    networkInfoDict = parse_wifi_networks(wlan_output)
    interface_info = networkInfoDict[interface_name]
    if interface_info["SSID"] == network_name:
        print ("connected")
        return True

    return False

# Usage example
interface_name = 'Wi-Fi'  # Replace with your network interface name
network_name = 'NETGEAR71'  # Replace with the network name you want to check

is_connected = check_network_interface(interface_name, network_name)
if is_connected:
    print(f'The network interface "{interface_name}" is connected to "{network_name}".')
else:
    print(f'The network interface "{interface_name}" is not connected to "{network_name}".')

# Content containing the Wi-Fi network information
