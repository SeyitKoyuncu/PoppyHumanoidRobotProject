import time
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "../../"))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from src.Controllers.IMUController import IMUController

imu = IMUController()
if not imu.connect():
    exit()

time.sleep(1)
# Calibrate while holding the robot upright manually
imu.calibrate_standing_reference(sample_duration=1.5)

print("\n--- LOOP STARTED ---")
print("Tilt the robot FORWARD and BACKWARD manually to observe the readings (Exit: Ctrl+C):\n")

try:
    while True:
        pitch_error = imu.get_pitch_error()
        raw_pitch = imu.latest_pitch
        
        # Terminal output
        status = "UPRIGHT"
        if pitch_error > 2.0:
            status = "TILTED FORWARD (or backward depending on mount)"
        elif pitch_error < -2.0:
            status = "TILTED BACKWARD (or forward depending on mount)"

        print(f"Raw Pitch: {raw_pitch:6.2f}° | Error: {pitch_error:6.2f}° | Status: {status}", end="\r")
        time.sleep(0.05)

except KeyboardInterrupt:
    print("\nTest terminated.")
finally:
    imu.disconnect()