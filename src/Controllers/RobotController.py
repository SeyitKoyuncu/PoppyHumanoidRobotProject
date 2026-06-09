import math
import time

try:
    from pypot.creatures import PoppyHumanoid
except ImportError:
    PoppyHumanoid = None

class RobotController:
    """Handles all pypot hardware and simulation interactions."""
    def __init__(self, log_callback=None):
        self.robot = None
        # Holder for logging function, defaults to print if not provided
        self.log = log_callback if log_callback else print

    def connect(self, is_simulation=True):
        if PoppyHumanoid is None:
            self.log("ERROR: 'pypot' library not found.")
            return False

        try:
            if is_simulation:
                self.robot = PoppyHumanoid(simulator='vrep')
            else:
                self.robot = PoppyHumanoid()
            return True
        except Exception as e:
            self.log(f"Connection failed: {str(e)}")
            return False

    def disconnect(self):
        if self.robot:
            self.robot.close()
            self.robot = None

    def get_motor_names(self):
        """Returns a list of available motor names."""
        if self.robot:
            return [motor.name for motor in self.robot.motors]
        return []

    def get_motor_by_name(self, motor_name):
        return getattr(self.robot, motor_name, None)

    def get_all_motors(self):
        if self.robot:
            return self.robot.motors
        return []

    def test_single_motor_smoothly(self, motor, process_events_callback=None):
        """Moves a single motor using a cosine trajectory."""
        if not motor: return
        
        current_pos = motor.present_position
        motor.compliant = False 
        
        amplitude = 40.0
        duration = 2.5
        dt = 0.05
        
        def move_phase(calculate_target_func):
            t = 0.0
            while t <= duration:
                smooth_factor = (1.0 - math.cos(math.pi * (t / duration))) / 2.0
                target = calculate_target_func(smooth_factor)
                
                motor.goto_position(target, dt, wait=False)
                time.sleep(dt)
                t += dt
                
                # Callback to process GUI events during the motor movement
                if process_events_callback:
                    process_events_callback()

        # 1. Forward motion
        move_phase(lambda sf: current_pos + (amplitude * sf))
        time.sleep(1) 
        
        # 2. Backward motion
        move_phase(lambda sf: (current_pos + amplitude) - (amplitude * sf))