import subprocess
import re

def check_network_interface(interface_name, network_name):
    # Get the wireless interface details
    wlan_command = f'netsh wlan show interfaces name="{interface_name}"'
    wlan_output = subprocess.check_output(wlan_command, shell=True).decode()

    # Extract the network SSID from the wireless interface output using regular expressions
    ssid_match = re.search(r"SSID\s+:\s(.+)", wlan_output)
    if ssid_match:
        ssid = ssid_match.group(1).strip()
        if ssid == network_name:
            return True

    return False

# Usage example
interface_name = 'Wi-Fi 2'  # Replace with your network interface name
network_name = 'NETGEAR71'  # Replace with the network name you want to check

is_connected = check_network_interface(interface_name, network_name)
if is_connected:
    print(f'The network interface "{interface_name}" is connected to "{network_name}".')
else:
    print(f'The network interface "{interface_name}" is not connected to "{network_name}".')
