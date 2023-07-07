from olympe.messages.ardrone3.PilotingState import AlertStateChanged

def check_magnetic_interference(drone):
    magnetic_interference = False

    def magnetic_interference_callback(alert_state):
        nonlocal magnetic_interference
        if alert_state == AlertStateChanged.ALERT_STATE_USER_MAGNETIC_INTERFERENCE:
            magnetic_interference = True

    # Subscribe to the magnetic interference alert state
    drone.subscribe(AlertStateChanged(magnetic_interference_callback))

    # Wait for the callback to set the magnetic_interference variable
    while not magnetic_interference:
        drone.smart_sleep(0.1)

    # Unsubscribe from the alert state
    drone.unsubscribe(AlertStateChanged(magnetic_interference_callback))

    return magnetic_interference
