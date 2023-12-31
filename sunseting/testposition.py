from geopy.distance import geodesic
import math


def calculate_bearing(yaw):
    """Calculate the bearing based on the yaw angle (degrees)."""
    return (yaw + 360) % 360


def calculate_distance_to_ground(altitude, pitch, vertical_fov, y_pos):
    """
    Calculate the distance from the camera to the point directly under
    the object in the image.

    :param altitude: altitude of the camera above ground
    :param pitch: pitch angle of the camera (0 degrees is looking straight ahead)
    :param vertical_fov: vertical field of view of the camera in degrees
    :param y_pos: vertical position of the object in the image (0 top, 1 bottom)
    :return: distance in meters
    """
    # Convert pitch and FOV to radians for calculation
    pitch_rad = math.radians(pitch)
    fov_rad = math.radians(vertical_fov)

    # Calculate the angle from the camera to the object's position in the image
    angle_from_center_rad = (y_pos - 0.5) * fov_rad

    # Calculate the angle from the camera to the ground point directly below the object
    angle_to_ground_rad = pitch_rad + angle_from_center_rad

    # Calculate the distance to the ground point using trigonometry
    distance_to_ground = altitude / math.cos(angle_to_ground_rad)

    return distance_to_ground


def calculate_real_world_position(image_pos, camera_pos, camera_rotation, horizontal_fov, vertical_fov):
    """
    Calculate the real-world position of an object in an image.

    :param image_pos: tuple (x, y) where x and y range from 0 to 1
    :param camera_pos: tuple (lat, lon, alt) representing the camera's geographic position and altitude
    :param camera_rotation: tuple (pitch, yaw, roll) representing the camera's rotation angles in degrees
    :param horizontal_fov: horizontal field of view of the camera in degrees
    :param vertical_fov: vertical field of view of the camera in degrees
    :return: tuple (lat, lon) representing the geographic position of the object
    """
    # Calculate the camera's bearing based on its yaw rotation
    camera_bearing = calculate_bearing(camera_rotation[1])

    # Calculate the horizontal angle from the center of the image to the object
    angle_from_center_horizontal = (image_pos[0] - 0.5) * horizontal_fov

    # Calculate the object's bearing relative to the camera's bearing
    object_bearing = camera_bearing + angle_from_center_horizontal

    # Calculate the distance from the camera to the ground point directly below the object
    distance_to_ground = calculate_distance_to_ground(camera_pos[2], camera_rotation[0], vertical_fov, image_pos[1])

    # Calculate the distance on the ground to the object's position
    distance_on_ground = distance_to_ground * math.sin(math.radians(angle_from_center_horizontal))

    # Calculate the new position based on the camera's location, object's bearing, and distance on the ground
    new_position = geodesic(meters=distance_on_ground).destination((camera_pos[0], camera_pos[1]), object_bearing)

    return new_position.latitude, new_position.longitude


# Example usage:
image_position = (0.1, 0.1)  # Center of the image
camera_position = (-70.6948020706945, 19.4400550374444, 66)
camera_rotation = (90, 0, 0)
horizontal_fov = 68  # Horizontal field of view in degrees
vertical_fov = 43  # Vertical field of view in degrees

object_lat_lon = calculate_real_world_position(image_position, camera_position, camera_rotation, horizontal_fov,
                                               vertical_fov)
print("The object's real-world position (lat, lon) is:", object_lat_lon)

# Example usage:

