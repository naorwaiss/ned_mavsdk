#!/usr/bin/env python3


import asyncio
import time
from mavsdk import System,telemetry
from mavsdk.offboard import (OffboardError, VelocityBodyYawspeed)
from coordinate import (get_geo_pos,geodetic_to_cartesian_ned)
from math import radians ,degrees , sqrt
import subprocess


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


async def get_flight_mode(drone):
    async for flight_mode in drone.telemetry.flight_mode():
        return flight_mode



async def offboard(drone):


    print("-- Starting offboard")
    try:
        await drone.offboard.start()
    except OffboardError as error:
        print(f"Starting offboard mode failed with error code: \
                  {error._result.result}")

        print("stop offbord")
        await drone.offboard.stop()
        return

    return


async def absolute_yaw(drone):
    async for attitude_info in drone.telemetry.attitude_euler():
        absolute_yaw = attitude_info.yaw_deg
        return absolute_yaw



async def spare(x_dist, y_dist, z_dist, drone):
    while True:
        dist = sqrt(x_dist ** 2 + y_dist ** 2 + z_dist ** 2)
        x_local, y_local, z_local = await geodetic_to_cartesian_ned(drone,latitude_i, longitude_i, altitude_i)
        local_dist = sqrt(x_local ** 2 + y_local ** 2 + z_local ** 2)
        accuracy = dist - local_dist

        if accuracy < 0.1:
            await drone.offboard.set_velocity_body(
                VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
            await drone.offboard.stop()
            return
        else:
            await asyncio.sleep(0.1)




async def takeoff_velocity(drone,target_altitude):
    #only move at the z at the start of the drone
    x=y=0
    print("-- Arming")
    await drone.action.arm()

    print("-- Setting initial setpoint")
    await drone.offboard.set_velocity_body(
        VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))

    await offboard(drone) #change to offboard

    print("-- only climb")
    await drone.offboard.set_velocity_body(
        VelocityBodyYawspeed(0.0, 0.0, -1.0, 0))


    await spare(x,y,target_altitude,drone)
    return


async def x_axis(drone,target,latitude_i, longitude_i, altitude_i):
    #move to cartzian position at the x axis

    x_local,y_local,z_local = await geodetic_to_cartesian_ned(drone,latitude_i, longitude_i, altitude_i)

    await drone.offboard.set_velocity_body(
        VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
    await offboard(drone)

    print("start flight at x axes ")
    if target > 0:
        await drone.offboard.set_velocity_body(
            VelocityBodyYawspeed(1.0, 0.0, 0.0, 0.0))

    else:
        await drone.offboard.set_velocity_body(
            VelocityBodyYawspeed(-1.0, 0.0, 0.0, 0.0))

    await spare(target,y_local,z_local,drone)
    print (await geodetic_to_cartesian_ned(drone,latitude_i, longitude_i, altitude_i))
    return

async def y_axis(drone, target, latitude_i, longitude_i, altitude_i):
    # Move to Cartesian position along the Y-axis

    x_local, y_local, z_local = await geodetic_to_cartesian_ned(drone, latitude_i, longitude_i, altitude_i)

    await drone.offboard.set_velocity_body(
        VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
    await offboard(drone)

    print("Start flight along the Y-axis ")
    if target > 0:
        print ("move right")
        await drone.offboard.set_velocity_body(
            VelocityBodyYawspeed(0.0, 1.0, 0.0, 0.0))
    else:
        print ("move left")
        await drone.offboard.set_velocity_body(
            VelocityBodyYawspeed(0.0, -1.0, 0.0, 0.0))

    await spare(x_local, target, z_local, drone)
    print (await geodetic_to_cartesian_ned(drone,latitude_i, longitude_i, altitude_i))
    return

async def camera_control():

    return


async def main():
    global latitude_i, longitude_i, altitude_i, x_i, y_i, z_i
    latitude_i = longitude_i = altitude_i = 0

    drone = System()
    await drone.connect(system_address="udp://:14540")

    await first_setup(drone)
    geo_pos = await get_geo_pos(drone)
    latitude_i, longitude_i, altitude_i = geo_pos
    x_i, y_i, z_i = await geodetic_to_cartesian_ned(drone, latitude_i, longitude_i, altitude_i)


    target_altitude = int(input("Enter the target altitude in meters: "))
    await takeoff_velocity(drone, target_altitude)


    while True:
        direction = input("What should the drone do? (land, x, y, camera): ")
        if direction == "land":
            break
        elif direction == "x":
            x_dist = int(input("Enter the target movement at x in meters: "))
            await x_axis(drone, x_dist, latitude_i, longitude_i, altitude_i)

        elif direction == "y":
            y_dist = int(input("Enter the target movement at y in meters: "))
            await y_axis(drone, y_dist, latitude_i, longitude_i, altitude_i)

    print("-- Landing")
    await drone.action.land()

if __name__ == "__main__":
    asyncio.run(main())
