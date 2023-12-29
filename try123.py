import subprocess
import re
#try to run the camera code with subproces

def run_camera_script():
    print("Running camera script...")
    process = subprocess.Popen(["python", "camera_red_detect.py"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               universal_newlines=True)

    try:
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                # Extract and print x, y, z values from the camera script's output
                match = re.match(r"Left: ([-+]?\d*\.\d+|\d+), Forward: ([-+]?\d*\.\d+|\d+), Up: ([-+]?\d*\.\d+|\d+)",
                                 output)
                if match:
                    left, forward, up = match.groups()
                    print(f"Received: Left={left}, Forward={forward}, Up={up}")
    except KeyboardInterrupt:
        print("Script terminated by user.")
    finally:
        process.terminate()
        process.wait()
        print("Camera script finished.")


if __name__ == "__main__":
    run_camera_script()








