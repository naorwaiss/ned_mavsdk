#!/usr/bin/env python3


import asyncio
import mavsdk
from mavsdk import System,telemetry
from mavsdk.offboard import (OffboardError, VelocityBodyYawspeed)
from coordinate import (get_geo_pos,geodetic_to_cartesian_ned)
from math import radians ,degrees , sqrt



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

    #need to change this code that if the drone is mid air the drone need to go to land
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
            return 1
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


    if await spare(x,y,target_altitude,drone)==1 :
        print(await geodetic_to_cartesian_ned(drone,latitude_i, longitude_i, altitude_i))
        await drone.offboard.set_velocity_body(
            VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
        await drone.offboard.stop()
    else:
        print ("problem")

    return



async def x_axis(drone,target):
    #move to cartzian position at the x axis

    await drone.offboard.set_velocity_body(
        VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
    await offboard(drone)
    print("start flight at x axes ")
    drone.offboard.set_velocity_body(
        VelocityBodyYawspeed(1.0, 0.0, 0.0, 0.0))



    return








async def run():

    """ Does Offboard control using velocity body coordinates. """
    global latitude_i, longitude_i, altitude_i, x_i, y_i, z_i
    latitude_i = longitude_i = altitude_i = 0

    # Connect to the drone
    drone = System()
    await drone.connect(system_address="udp://:14540")

    # Setup and check GPS position, then convert to right-hand Cartesian NED from GPS geodetic position
    await first_setup(drone)
    geo_pos = await get_geo_pos(drone)
    latitude_i, longitude_i, altitude_i = geo_pos
    x_i, y_i, z_i = await geodetic_to_cartesian_ned(drone,latitude_i, longitude_i, altitude_i)
    print (x_i,y_i,z_i)

    target_altitude = int(input("Enter the target altitude in meters: "))

    await takeoff_velocity(drone,target_altitude)
    #
    # print("-- Arming")
    # await drone.action.arm()
    #
    # print("-- Setting initial setpoint")
    # await drone.offboard.set_velocity_body(
    #     VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
    #
    # await offboard(drone)
    #
    # print("-- only climb")
    # await drone.offboard.set_velocity_body(
    #     VelocityBodyYawspeed(0.0, 0.0, -1.0, 0))
    # await asyncio.sleep(5)
    # print (await geodetic_to_cartesian_ned(drone, latitude_i, longitude_i, altitude_i))

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