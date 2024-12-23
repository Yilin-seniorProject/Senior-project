from pymavlink import mavutil


def connect_drone():
    # Connect to device
    master = mavutil.mavlink_connection("/dev/ttyAMA0", baud=57600)
    master.wait_heartbeat()
    print("Heartbeat from system (system %u component %u)" %
          (master.target_system, master.target_component))
    return master


def send_message(master, message_id, *params):
    # Define command_long_encode message to send MAV_CMD_SET_MESSAGE_INTERVAL command
    params = list(params)
    if len(params) != 6:
        for i in range(6):
            if len(params) == 6:
                break
            else:
                params.append(0)

    message = master.mav.command_long_encode(
        master.target_system,  # Target system ID
        master.target_component,  # Target component ID
        mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,  # ID of command to send
        0,  # Confirmation
        message_id,  # param1: Message ID to be streamed
        params[0],
        params[1],
        params[2],
        params[3],
        params[4],
        params[5],
    )

    # Send message
    master.mav.send(message)

    # Wait for a response
    response = master.recv_match(type='COMMAND_ACK', blocking=True)
    if response and response.command == mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL and response.result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
        return True
    else:
        return False


master = connect_drone()
ret = send_message(
    master, mavutil.mavlink.MAVLINK_MSG_ID_GLOBAL_POSITION_INT, 1e6)
ret = send_message(
    master, mavutil.mavlink.MAVLINK_MSG_ID_ATTITUDE, 1e6)


def get_gps_info():
    # Receive message
    try:
        gps_info = master.recv_match(
            type="GLOBAL_POSITION_INT", blocking=True).to_dict()
        lat = gps_info["lat"] * 1e-7
        lon = gps_info["lon"] * 1e-7
        alt = gps_info['relative_alt'] * 1e-3
        hdg = gps_info["hdg"] * 0.01
        print(f'lat:{lat}, lon:{lon}, alt:{alt}, hdg:{hdg}')
        return (lat, lon, alt, hdg)
    except KeyboardInterrupt:
        exit(0)
    except Exception as e:
        print(e)
        exit(1)

def get_attitude_info():
    # Receive message
    try:
        alt_info = master.recv_match(
            type="ATTITUDE", blocking=True).to_dict()
        roll = alt_info["roll"]
        pitch = alt_info["pitch"]
        yaw = alt_info["yaw"]
        print(f'roll:{roll}, pitch:{pitch}, yaw:{yaw}')
        return (roll, pitch, yaw)
    except KeyboardInterrupt:
        exit(0)
    except Exception as e:
        print(e)
        exit(1)

print("mavlink package on ready")

if __name__ == "__main__":
    while True:
        get_gps_info()
        get_attitude_info()