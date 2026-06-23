import time
import math
#from pypot.creatures import PoppyHumanoid
from pypot.creatures import PoppyTorso

class WaveMotion:
    """A class containing smooth movement trajectories for the Poppy Humanoid."""
    
    def __init__(self, robot):
        self.robot = robot

    def check_left_arm(self):
        """Checks if the left arm motors are present in the system."""
        required_motors = ['l_shoulder_y', 'l_shoulder_x', 'l_elbow_y', 'l_arm_z']
        for motor_name in required_motors:
            if not hasattr(self.robot, motor_name) or getattr(self.robot, motor_name) is None:
                print(f"[ERROR] {motor_name} not found! The left arm is either disconnected or inactive.")
                return False
        return True

    def wave_left_hand(self, duration=5.0, speed=6.0, amplitude=30.0):
        """
        Raises the left arm and waves it in a human-like manner.
        
        Parameters:
            duration (float): The duration of the waving motion in seconds.
            speed (float): The waving speed (Sine wave frequency).
            amplitude (float): The waving angle amplitude of the hand.
        """
        if not self.check_left_arm():
            return

        print("\n Raising the left arm...")
        
        # 1. PREPARATION POSITION: Raise the arm and bend the elbow
        # All motors move simultaneously using goto_position(target, duration, wait=False)
        #self.robot.l_shoulder_y.goto_position(5, 4, wait=False) # Raise the arm forward
        #self.robot.l_shoulder_x.goto_position(-25, 2, wait=False)  # Slightly open the arm outward
        self.robot.l_arm_z.goto_position(0, 2, wait=False)        # Straighten the wrist
        #self.robot.l_elbow_y.goto_position(-10, 2, wait=True)     # Bend the elbow (wait=True waits for completion)

        print(f"Waving animation started ({duration} seconds)...")
        
        # 2. WAVING LOOP: Smooth hand waving using a sine wave
        start_time = time.time()
        while time.time() - start_time < duration:
            t = time.time() - start_time
            
            # Rotate the wrist (arm_z) left and right
            wave_angle = amplitude * math.sin(speed * t)
            #self.robot.l_arm_z.goal_position = wave_angle
            
            # Slightly bounce the elbow (elbow_y) for a natural, human-like look
            bounce_angle = -70 + (10 * math.cos(speed * t))
            #self.robot.l_elbow_y.goal_position = bounce_angle
            
            # A tiny delay to prevent the loop from running too fast (50Hz refresh rate)
            time.sleep(0.02)

        print("Returning the arm to the starting position (0)...")
        
        # 3. ENDING: Slowly lower the arm back to the default position
        #self.robot.l_shoulder_y.goto_position(0, 2, wait=False)
        #self.robot.l_shoulder_x.goto_position(0, 2, wait=False)
        #self.robot.l_elbow_y.goto_position(0, 2, wait=False)
        #self.robot.l_arm_z.goto_position(0, 2, wait=True)
        
        print("Waving motion completed!")


# --- MAIN EXECUTION (For testing) ---
if __name__ == '__main__':
    poppy = None
    try:
        # Use check_full_config=False to bypass previous connection lock issues
        #poppy = PoppyHumanoid(check_full_config=False)
        poppy = PoppyTorso(check_full_config=False, camera = 'dummy')
        
        # Make motors stiff (compliant = False) so they can move
        for m in poppy.motors:
            m.goal_position = m.present_position
            m.compliant = False
            
        # Initialize the class and start the motion
        action = WaveMotion(poppy)
        action.wave_left_hand(duration=4.0)

    except Exception as e:
        print(f"\n[SYSTEM ERROR] {e}")

    finally:
        # Release motors and SECURELY CLOSE THE PORT even if the code crashes
        if poppy is not None:
            for m in poppy.motors:
                m.compliant = True
            poppy.close()
            print("Port successfully closed and released.")