


def detection_to_position(detection, cam_position, pitch, yaw, roll, fov_h, fov_v):

    # calculate angle of detection
    x, y = fov_h * detection[0], fov_v * detection[1]
    print(str(x), str(y))
    print(pitch)
    offset = yaw - fov_h/2, pitch + fov_v/2
    print(offset)
    vector = offset[0] + x, offset[1] - y
    print(vector)
    return vector


cam_position = (0, 0, 200)
pitch, yaw, roll = -101.92743877023, -89.8554212568503, 34.5229225095474
fov_h = 69.1
fov_v = 42.6
detection = (0.250109, 0.304253)

detection_to_position(detection, cam_position, pitch, yaw, roll, fov_h, fov_v)