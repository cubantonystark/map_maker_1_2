import numpy as np
from math import tan, radians, cos, sin


def euler_to_rotation_matrix(pitch, yaw, roll):
    # Convert angles from degrees to radians
    pitch = radians(pitch)
    yaw = radians(yaw)
    roll = radians(roll)

    # Calculate rotation matrix components
    Rz_yaw = np.array([
        [cos(yaw), -sin(yaw), 0],
        [sin(yaw), cos(yaw), 0],
        [0, 0, 1]
    ])

    Ry_pitch = np.array([
        [cos(pitch), 0, sin(pitch)],
        [0, 1, 0],
        [-sin(pitch), 0, cos(pitch)]
    ])

    Rx_roll = np.array([
        [1, 0, 0],
        [0, cos(roll), -sin(roll)],
        [0, sin(roll), cos(roll)]
    ])

    # Combined rotation matrix
    R = Rz_yaw @ Ry_pitch @ Rx_roll

    return R


def camera_frame_corners(camera_position, pitch, yaw, roll, fov_x, fov_y, near_clip):
    # Camera rotation matrix
    R = euler_to_rotation_matrix(pitch, yaw, roll)

    # Aspect ratio (assuming fov_x and fov_y are in degrees)
    aspect_ratio = tan(radians(fov_x) / 2) / tan(radians(fov_y) / 2)

    # Half dimensions of the near clip plane
    half_height = near_clip * tan(radians(fov_y) / 2)
    half_width = half_height * aspect_ratio

    # Direction vectors
    forward = np.array([0, 0, 1])
    up = np.array([0, 1, 0])
    right = np.array([1, 0, 0])

    # Rotate direction vectors
    forward = R @ forward
    up = R @ up
    right = R @ right

    # Center of the near clip plane
    center = np.array(camera_position) + forward * near_clip

    # Corners of the near clip plane
    top_left = center + (up * half_height) - (right * half_width)
    top_right = center + (up * half_height) + (right * half_width)
    bottom_left = center - (up * half_height) - (right * half_width)
    bottom_right = center - (up * half_height) + (right * half_width)

    return {
        'center': center.tolist(),
        'top_left': top_left.tolist(),
        'top_right': top_right.tolist(),
        'bottom_left': bottom_left.tolist(),
        'bottom_right': bottom_right.tolist()
    }


# Example usage:
camera_position = (0, 0, 0)  # (x, y, z)
pitch = 0  # rotation around x-axis
yaw = 0  # rotation around y-axis
roll = 0  # rotation around z-axis
fov_x = 90  # field of view in x-axis in degrees
fov_y = 90  # field of view in y-axis in degrees
near_clip = 1  # distance from camera to near clip plane

corners = camera_frame_corners(camera_position, pitch, yaw, roll, fov_x, fov_y, near_clip)
print("Frame Corners and Center:")
for k, v in corners.items():
    print(f"{k}: {v}")
