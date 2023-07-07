import serial
import pynmea2

# Define the serial port and baud rate
serial_port = "COM9"  # Update with your GPS device's serial port
baud_rate = 9600  # Update with your GPS device's baud rate

# Connect to the serial port


def get_my_position():
    ser = serial.Serial(serial_port, baud_rate, timeout=5)
    # Read data from the GPS device
    while True:
        try:
            # Read a line of data from the GPS device
            line = ser.readline().decode('utf-8')

            # Check if the line contains the GPS position data
            if line.startswith('$GPGGA'):
                # Parse the NMEA sentence
                data = pynmea2.parse(line)

                # Extract the latitude and longitude
                latitude = data.latitude
                longitude = data.longitude
                payload = (latitude, longitude)
                # Print the current position
                print("Latitude: {}".format(latitude))
                print("Longitude: {}".format(longitude))
                return payload
                # Exit the loop after retrieving the position
                break

        except serial.SerialException:
            print("Error reading data from the GPS device.")
            return (0, 0)
    # Close the serial port
    ser.close()
    return

