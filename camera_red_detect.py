#this is the main code for the camera -- need to work little more to upload the output paramters

import os
import pyrealsense2.pyrealsense2 as rs
import numpy as np
import cv2
import asyncio

# Set an environment variable to disable GUI
os.environ["DISPLAY"] = ":0.0"

# Global variables to store the calculated values
left = 0
forward = 0
up = 0

async def process_frames(pipeline, out):
    global left, forward, up

    try:
        while True:
            frames = None
            for _ in range(5):
                frames = pipeline.wait_for_frames(timeout_ms=2000)  # Wait for up to 1 second
                if frames:
                    break

            if frames is None:
                print("No frames received within the timeout.")
                continue

            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()

            if not depth_frame or not color_frame:
                continue

            # Get the color image as a numpy array
            color_image = np.asanyarray(color_frame.get_data())

            # Convert the color image to HSV
            hsv = cv2.cvtColor(color_image, cv2.COLOR_BGR2HSV)

            # Define lower and upper bounds for the red color (adjust as needed)
            lower_red1 = np.array([0, 100, 100])
            upper_red1 = np.array([10, 255, 255])
            lower_red2 = np.array([160, 100, 100])
            upper_red2 = np.array([180, 255, 255])

            # Create masks for both ranges of red
            mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
            mask2 = cv2.inRange(hsv, lower_red2, upper_red2)

            # Combine both masks to detect strong red colors
            mask = cv2.bitwise_or(mask1, mask2)

            # Apply morphological operations to the mask
            kernel = np.ones((5, 5), np.uint8)
            mask = cv2.erode(mask, kernel, iterations=1)
            mask = cv2.dilate(mask, kernel, iterations=2)

            # Find contours in the mask
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Initialize variables to keep track of the largest obstacle
            largest_area = 0
            largest_obstacle = None

            for contour in contours:
                # Calculate the area of the contour
                area = cv2.contourArea(contour)

                # Find the largest obstacle
                if area > largest_area:
                    largest_area = area
                    largest_obstacle = contour

            if largest_obstacle is not None:
                # Draw a bounding box around the largest obstacle
                x, y, w, h = cv2.boundingRect(largest_obstacle)
                cv2.rectangle(color_image, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # Calculate the center of the largest obstacle
                center_x = x + w // 2
                center_y = y + h // 2

                # Get the depth value at the center of the obstacle
                depth_value = depth_frame.get_distance(center_x, center_y)

                # Display the distance on the image
                distance_text = f"Depth: {depth_value:.2f} meters"
                cv2.putText(
                    color_image,
                    distance_text,
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2,
                    cv2.LINE_AA,
                )

                # Calculate 'left', 'forward', and 'up' values based on your processing logic
                # Example:
                left = center_x - 320  # Calculate left value relative to the center
                forward = 480 - center_y  # Calculate forward value relative to the center
                up = depth_value  # Use depth value as the 'up' value

            # Display the color image with the largest obstacle and its distance
            cv2.imshow("Color Frame with Largest Obstacle", color_image)
            # Write the frame to the output video
            out.write(color_image)

            key = cv2.waitKey(1)
            if key == 27:  # Press 'Esc' to exit
                break

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Stop the pipeline
        pipeline.stop()
        out.release()

async def main():
    global left, forward, up

    # Create a context
    pipeline = rs.pipeline()
    config = rs.config()

    # Enable both depth and color streams with the desired settings
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

    # Start the pipeline
    pipeline.start(config)

    # Define the codec and create a VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')  # Change the codec to 'MJPG'
    output_file = '/home/drone/Desktop/output.avi'
    fps = 30  # Frames per second
    frame_size = (640, 480)  # Match the frame size to your input stream

    out = cv2.VideoWriter(output_file, fourcc, fps, frame_size)

    # Start the frame processing coroutine
    await process_frames(pipeline, out)

if __name__ == "__main__":
    asyncio.run(main())
