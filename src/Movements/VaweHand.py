import time
import math
from pypot.creatures import PoppyTorso
from Controllers.MotorRelaxController import relax_motors

class WaveMotion:
    """A class containing smooth movement trajectories for the Poppy Torso."""
    
    def __init__(self, robot):
        self.robot = robot
        # We define the specific motors needed for the left arm gesture.
        # Since there is no wrist joint, 'l_arm_z' will rotate the whole forearm.
        self.left_arm_motors = ['l_shoulder_y', 'l_shoulder_x', 'l_arm_z', 'l_elbow_y']

    def check_left_arm(self):
        """Checks if all required left arm motors are active in the configuration."""
        for motor_name in self.left_arm_motors:
            if not hasattr(self.robot, motor_name) or getattr(self.robot, motor_name) is None:
                print(f"[ERROR] {motor_name} not found! Check connection.")
                return False
        return True

    def wave_left_hand(self, duration=5.0, speed=6.0, amplitude=120.0):
        """Raises the forearm using the elbow and rotates it to create a waving effect."""
        if not self.check_left_arm():
            return

        print("\n[STEP 1] Locking ONLY the left arm motors...")
        # To prevent other body parts from twitching, we engage ONLY the left arm.
        # Every other motor on the robot stays completely relaxed (compliant = True).
        for motor_name in self.left_arm_motors:
            motor = getattr(self.robot, motor_name)
            motor.goal_position = motor.present_position
            motor.compliant = False
            motor.torque_limit = 20.0

        time.sleep(0.5)  # Short pause to let motors stabilize

        print("[STEP 2] Bringing the arm to the waving posture...")
        starting_l_shoulder_x = self.robot.l_shoulder_x.present_position
        starting_l_arm_z = self.robot.l_arm_z.present_position
        starting_l_elbow_y = self.robot.l_elbow_y.present_position
        # We bring the arm forward and bend the elbow so the hand points upwards.
        self.robot.l_shoulder_x.goto_position(90, 1.5, wait=True) # Keep the arm slightly away from body 
        self.robot.l_arm_z.goto_position(90, 1.5, wait=True) # Rotate arm
        self.robot.l_elbow_y.goto_position(-60, 1.5, wait=True) # Bend the elbow sharply so hand faces up

        print(f"[STEP 3] Starting the wave loop ({duration} seconds)...")
        start_time = time.time()
        base_elbow_angle = -60.0 
        while time.time() - start_time < duration:
            t = time.time() - start_time
            
            # Since there is no joint right at the wrist, we rotate 'l_elbow_y'.
            # This turns the entire forearm axis left and right, making the hand wave.
            wave_angle = base_elbow_angle + (amplitude * math.sin(speed * t))
            self.robot.l_elbow_y.goto_position(wave_angle + 20, duration = 0.1, wait = False)
            
            # 20Hz refresh rate to ensure smooth communication with the Dynamixel motors
            time.sleep(0.05)

        print("[STEP 4] Resetting arm smoothly to default position...")
        # Return all arm angles back to 0 before releasing torque.
        self.robot.l_elbow_y.goto_position(starting_l_elbow_y, 1.0, wait=True) # Rotate elbow to initial position
        self.robot.l_arm_z.goto_position(starting_l_arm_z, 1.5, wait=True) # Rotate arm to initial position
        self.robot.l_shoulder_x.goto_position(starting_l_shoulder_x, 1.5, wait=True) # Rotate Shoulder to initial position 


        
        print("[INFO] Waving motion completed successfully!")

# --- MAIN EXECUTION ---
if __name__ == '__main__':
    poppy = None
    try:
        # Initialize Poppy Torso with camera disabled to prevent port locks
        poppy = PoppyTorso(check_full_config=False, camera='dummy')
        
        print("Ensuring all motors start in relaxed mode...")
        for m in poppy.motors:
            m.compliant = True
            
        # Run the waving sequence
        action = WaveMotion(poppy)
        #ElbowTest()
        action.wave_left_hand(duration=5.0)

    except Exception as e:
        print(f"\n[SYSTEM ERROR] {e}")

    finally:
        relax_motors(poppy)