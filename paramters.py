
#make yoad validation from the rc controler

async def get_flight_mode(drone):
    async for flight_mode in drone.telemetry.flight_mode():
        return flight_mode


async def yoad_prearm(drone):
    while True:
        flight_mode = await get_flight_mode(drone)
        print(f"Flight mode: {flight_mode}")

        if flight_mode == "OFFBOARD":
            break

        # Set velocity to zero to keep the drone stationary
        await drone.offboard.set_velocity_body(VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))

        # Add a short sleep to reduce CPU usage
        await asyncio.sleep(0.5)

# Rest of your code
