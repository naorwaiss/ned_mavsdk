import numpy as np
from math import radians ,degrees , sqrt,cos,sin
import paramters


async def get_geo_pos(drone):

    """
    :param drone: connect strings
    :return: the current position of the drone at geo
    """
    default_coordinates = (0, 0, 0)
    try:
        async for position in drone.telemetry.position():
            latitude = position.latitude_deg
            longitude = position.longitude_deg
            altitude = position.absolute_altitude_m
            break
    except Exception as e:
        print(f"Error getting location: {e}")
        print("Using default coordinates.")
        return default_coordinates

    return latitude, longitude, altitude


import numpy as np
from math import radians, cos, sin

import numpy as np
from math import radians, cos, sin

import numpy as np
from math import radians, cos, sin


async def geodetic_to_cartesian_budy(drone, latitude_i, longitude_i, altitude_i, rotation_angle_degrees=0):
    """
    :param drone: connect string
    :return: make geo position to Cartesian one and rotate it to the right-hand axis budy coordinate
    """
    latitude, longitude, altitude = await get_geo_pos(drone)

    # Constants for Earth (assuming it's a perfect sphere)
    radius_earth = 6371000.0  # in meters

    # Convert latitude and longitude from degrees to radians
    lat_rad = radians(latitude)
    lon_rad = radians(longitude)

    # Convert reference latitude and longitude from degrees to radians
    ref_lat_rad = radians(latitude_i)
    ref_lon_rad = radians(longitude_i)

    # Calculate the difference in coordinates
    delta_lat = lat_rad - ref_lat_rad
    delta_lon = lon_rad - ref_lon_rad
    delta_altitude = altitude - altitude_i

    # Convert geodetic coordinates to Cartesian coordinates (NED convention)
    ned_x = radius_earth * delta_lon * cos(lat_rad)
    ned_y = radius_earth * delta_lat
    ned_z = -delta_altitude  # Negate altitude to align with NED convention

    # Get the absolute yaw angle from telemetry
    async for attitude_info in drone.telemetry.attitude_euler():
        absolute_yaw = radians(attitude_info.yaw_deg)
        break  # Exit the loop after obtaining the yaw

    # Calculate the rotation matrix based on the absolute yaw and additional rotation angle
    rotation_angle = radians(90)  # Rotate by 90 degrees to make the forward direction the y-axis
    total_angle = absolute_yaw + rotation_angle_degrees
    rotation_matrix = np.array([[cos(total_angle), -sin(total_angle), 0],
                                [sin(total_angle), cos(total_angle), 0],
                                [0, 0, -1]])  # Negate the Z-axis component to point downward

    ned_coordinates = np.dot(rotation_matrix, np.array([ned_x, ned_y, ned_z]))
    x_final, y_final, z_final = ned_coordinates


    return x_final, y_final, z_final

async def cartesian_to_geodetic(x, y, z, drone):
    # the revers function - from cartazian go to geo
    # Constants for Earth (assuming it's a perfect sphere)
    radius_earth = 6371000.0  # in meters

    # Define the rotation matrix for the reverse transformation
    rotation_matrix = np.array([[0, -1, 0], [1, 0, 0], [0, 0, 1]])

    # Apply the reverse rotation to get NED coordinates
    ned_coordinates = np.dot(rotation_matrix, np.array([x, y, z]))

    # Extract NED coordinates
    ned_x, ned_y, ned_z = ned_coordinates

    # Get reference geodetic coordinates
    ref_latitude, ref_longitude, ref_altitude = await get_geo_pos(drone)
    ref_lat_rad = radians(ref_latitude)
    ref_lon_rad = radians(ref_longitude)

    # Convert NED coordinates to geodetic coordinates
    delta_lat = ned_x / radius_earth
    delta_lon = ned_y / radius_earth
    delta_altitude = ned_z

    lat_rad = ref_lat_rad + delta_lat
    lon_rad = ref_lon_rad + delta_lon
    altitude = ref_altitude + delta_altitude

    # Convert back to degrees
    latitude = degrees(lat_rad)
    longitude = degrees(lon_rad)


    return latitude, longitude, altitude






