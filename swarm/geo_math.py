from math import radians, cos, sin, asin, sqrt, degrees, atan2
import json

def haversine_distance(lat1, lon1, lat2, lon2):
    # Calculate the distance between two coordinates using the Haversine formula
    # This function is used to calculate the coordinates based on distances

    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of the Earth in kilometers
    return c * r * 1000  # Return distance in meters

def calculate_coordinates(lat, lon, distance, bearing):
    # Calculate the new coordinates based on distance and bearing from the original coordinates

    # Convert distance from meters to kilometers
    distance_km = distance / 1000.0

    # Convert latitude and longitude to radians
    lat_rad = radians(lat)
    lon_rad = radians(lon)

    # Convert bearing to radians
    bearing_rad = radians(bearing)

    # Earth's radius in kilometers
    radius = 6371.0

    # Calculate the new latitude
    new_lat = asin(sin(lat_rad) * cos(distance_km / radius) +
                   cos(lat_rad) * sin(distance_km / radius) * cos(bearing_rad))

    # Calculate the new longitude
    new_lon = lon_rad + atan2(sin(bearing_rad) * sin(distance_km / radius) * cos(lat_rad),
                              cos(distance_km / radius) - sin(lat_rad) * sin(new_lat))

    # Convert new latitude and longitude back to degrees
    new_lat_deg = degrees(new_lat)
    new_lon_deg = degrees(new_lon)

    return new_lat_deg, new_lon_deg


def cut_up_map(original_lat, original_lon):
    # Calculate new coordinates based on distances and directions
    spread = 375

    # breaks up map
    # 1   2   3   4
    #    center
    # 5   6   7   8

    # center quadrant 1
    q1_lat, q1_lon = calculate_coordinates(original_lat, original_lon, spread/2, 0)
    q1_lat, q1_lon = calculate_coordinates(q1_lat, q1_lon, (spread/2) + spread, 270)

    # center quadrant 2
    q2_lat, q2_lon = calculate_coordinates(q1_lat, q1_lon, spread, 90)

    # center quadrant 3
    q3_lat, q3_lon = calculate_coordinates(q2_lat, q2_lon, spread, 90)

    # center quadrant 4
    q4_lat, q4_lon = calculate_coordinates(q3_lat, q3_lon, spread, 90)

    # center quadrant 5
    q5_lat, q5_lon = calculate_coordinates(q1_lat, q1_lon, spread, 180)

    # center quadrant 6
    q6_lat, q6_lon = calculate_coordinates(q5_lat, q5_lon, spread, 90)

    # center quadrant 7
    q7_lat, q7_lon = calculate_coordinates(q6_lat, q6_lon, spread, 90)

    # center quadrant 8
    q8_lat, q8_lon = calculate_coordinates(q7_lat, q7_lon, spread, 90)

    # Create a dictionary with the new coordinates
    coordinates = {
        'q1': {'lat': q1_lat, 'lon': q1_lon},
        'q2': {'lat': q2_lat, 'lon': q2_lon},
        'q3': {'lat': q3_lat, 'lon': q3_lon},
        'q4': {'lat': q4_lat, 'lon': q4_lon},
        'q5': {'lat': q5_lat, 'lon': q5_lon},
        'q6': {'lat': q6_lat, 'lon': q6_lon},
        'q7': {'lat': q7_lat, 'lon': q7_lon},
        'q8': {'lat': q8_lat, 'lon': q8_lon}
    }
    list_of_urls = []
    for each_coordinate in coordinates:
        url = "/webform?Latitude=" + str(coordinates[each_coordinate]["lat"]) + "&Longitude=" + str(coordinates[each_coordinate]["lon"]) + "&Address=&FlightType=orbit&Quality=Low&SendToDrone=yes&SelectDrone=a"
        print (url)
        list_of_urls.append(url)
    # Convert the dictionary to JSON


    # Print the JSON object
    return (list_of_urls, coordinates)


# Original latitude and longitude
# lat = 27.82585
# lon = -82.62205
# cut_up_map(lat, lon)
