import os
import sys
import time
import math

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "../../"))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from src.Controllers.RobotController import RobotController
from src.Controllers.IMUController import IMUController
from src.Controllers.MotorRelaxController import force_relax_motors

def run_balance_test(duration=30.0, kp=0.35, kd=0.03):
    # 1. Initialize Controllers
    imu = IMUController()
    if not imu.connect():
        print("[ERROR] Failed to connect to IMU.")
        return

    controller = RobotController()
    if not controller.connect(is_simulation=False):
        imu.disconnect()
        return

    try:
        print("\n1. Moving motors to standing posture...")
        controller.reset_all_motors_to_zero(duration=2.5, exclude_motors=[])
        
        # Initial ankle angle (Standing posture offset)
        base_ankle_angle = -1.0
        controller.motor_movement_go_to(
            target_angles={'r_ankle_y': base_ankle_angle, 'l_ankle_y': base_ankle_angle},
            duration=1.5,
            movement_name="Stand_Init",
            waitSituation=True
        )

        base_shoulder_angle = -8.0
        controller.motor_movement_go_to(
            target_angles={'r_shoulder_x': base_shoulder_angle},
            duration=1.5,
            movement_name="Open Arms a little",
            waitSituation=True
        )

        base_shoulder_angle = 8.0
        controller.motor_movement_go_to(
            target_angles={'l_shoulder_x': base_shoulder_angle},
            duration=1.5,
            movement_name="Open Arms a little",
            waitSituation=True
        )

        base_feet_angle = -10.0
        controller.motor_movement_go_to(
            target_angles={'r_hip_x': base_feet_angle},
            duration=1.5,
            movement_name="Open Legs a little",
            waitSituation=True
        )

        base_feet_angle = 10.0
        controller.motor_movement_go_to(
            target_angles={ 'l_hip_x': base_feet_angle},
            duration=1.5,
            movement_name="Open Legs a little",
            waitSituation=True
        )

        l_ankle = controller.get_motor_by_name('l_ankle_y')
        r_ankle = controller.get_motor_by_name('r_ankle_y')

        if not l_ankle or not r_ankle:
            print("[ERROR] Ankle motors not found!")
            return

        l_ankle.compliant = False
        r_ankle.compliant = False

        # --- USER TRIGGER FOR BALANCE LOOP ---
        print("\n" + "=" * 50)
        print("Robot is now in standing posture.")
        user_input = input("Hold the robot steady and press [ENTER] to calibrate & start balancing (or 'q' to abort): ")
        
        if user_input.strip().lower() == 'q':
            print("Balance test aborted by user.")
            return

        # 2. Calibrate reference angle only AFTER user confirmation (ensures a clean zero-point)
        print("\nCalibrating standing reference, please hold the robot completely still...")
        imu.calibrate_standing_reference(sample_duration=1.5)

        print(f"\n Balance loop active! Running for {duration} seconds...")
        print("Gently push the robot forward/backward by hand to feel the resistance (Stop with Ctrl+C).\n")

        dt = 0.03  # ~33 Hz loop rate
        start_time = time.time()
        prev_error = 0.0
        max_correction = 5.0  # Safety limit: max +/- 5 degrees
        deadband = 0.4        # Ignore vibrations below 0.4 degrees

        while time.time() - start_time < duration:
            loop_start = time.time()

            # Read current error angle (Forward: +, Backward: -)
            error = imu.get_pitch_error()

            # Deadband filter
            if abs(error) < deadband:
                effective_error = 0.0
            else:
                effective_error = error

            # Derivative calculation
            d_error = (effective_error - prev_error) / dt
            prev_error = effective_error

            # PD Control output
            correction = (kp * effective_error) + (kd * d_error)

            # Clamping
            correction = max(min(correction, max_correction), -max_correction)

            # Write new target angle directly to ankles
            target_pos = base_ankle_angle - correction  # If direction is reversed, change '-' to '+'
            l_ankle.goal_position = target_pos
            r_ankle.goal_position = target_pos

            # Monitor output
            print(f"Error: {error:5.2f}° | Correction: {correction:5.2f}° | Ankle Target: {target_pos:5.2f}°", end="\r")

            elapsed = time.time() - loop_start
            sleep_time = dt - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    except Exception as e:
        print(f"\n[ERROR] Runtime error: {e}")
    finally:
        print("\nClosing sensor and motor connections...")
        imu.disconnect()
        controller.disconnect()
        force_relax_motors()
        print("System safely relaxed.")

if __name__ == '__main__':
    run_balance_test(duration=45.0, kp=0.35, kd=0.03)