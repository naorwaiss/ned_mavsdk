#!/usr/bin/env python3


import asyncio
import mavsdk
from mavsdk import System
from mavsdk.offboard import (OffboardError, VelocityBodyYawspeed)
from coordinate import (get_geo_pos,geodetic_to_cartesian_ned)
from math import radians ,degrees , sqrt
import numpy as np


async def first_setup(drone):
    #i think that i can remove the position here
    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"-- Connected to drone!")
            break

    print("Waiting for drone to have a global position estimate...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("-- Global position estimate OK")
            break

        return

async def offboard(drone):
    print("-- Starting offboard")
    try:
        await drone.offboard.start()
    except OffboardError as error:
        print(f"Starting offboard mode failed with error code: \
                  {error._result.result}")
        print("-- Disarming")
        await drone.action.disarm()
        return

    return


async def absolute_yaw(drone):
    async for attitude_info in drone.telemetry.attitude_euler():
        absolute_yaw = attitude_info.yaw_deg
        return absolute_yaw






async def takeoff_velocity(drone,target_altitude):



    return














async def run():
    """ Does Offboard control using velocity body coordinates. """
    global latitude_i, longitude_i, altitude_i, x_i, y_i, z_i

    # Connect to the drone
    drone = System()
    await drone.connect(system_address="udp://:14540")

    # Setup and check GPS position, then convert to right-hand Cartesian NED from GPS geodetic position
    await first_setup(drone)
    geo_pos = await get_geo_pos(drone)
    latitude_i, longitude_i, altitude_i = geo_pos
    x_i, y_i, z_i = await geodetic_to_cartesian_ned(drone, latitude_i, longitude_i, altitude_i)

    offboard(drone)
    print("-- Arming")
    await drone.action.arm()

    print("-- Setting initial setpoint")
    await drone.offboard.set_velocity_body(
        VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))

    await offboard(drone)

    print("-- only climb")
    await drone.offboard.set_velocity_body(
        VelocityBodyYawspeed(0.0, 0.0, -1.0, 0))
    await asyncio.sleep(20)

    print("-- Turn back anti-clockwise")
    await drone.offboard.set_velocity_body(
        VelocityBodyYawspeed(0.0, 0.0, 0.0, -60.0))
    await asyncio.sleep(5)

    print("-- Wait for a bit")
    await drone.offboard.set_velocity_body(
        VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
    await asyncio.sleep(2)

    print("-- Fly a circle")
    await drone.offboard.set_velocity_body(
        VelocityBodyYawspeed(5.0, 0.0, 0.0, 30.0))
    await asyncio.sleep(15)

    print("-- Wait for a bit")
    await drone.offboard.set_velocity_body(
        VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
    await asyncio.sleep(5)

    print("-- Fly a circle sideways")
    await drone.offboard.set_velocity_body(
        VelocityBodyYawspeed(0.0, -5.0, 0.0, 30.0))
    await asyncio.sleep(15)

    print("-- Wait for a bit")
    await drone.offboard.set_velocity_body(
        VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
    await asyncio.sleep(8)

    print("-- Stopping offboard")
    try:
        await drone.offboard.stop()
    except OffboardError as error:
        print(f"Stopping offboard mode failed with error code: \
              {error._result.result}")


if __name__ == "__main__":
    # Run the asyncio loop
    asyncio.run(run())