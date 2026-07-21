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

    def goto_custom_angle(self, logFunction, motor, target_angle, process_events_callback=None):            
        duration = 2.0 
        dt = 0.05
        
        try:
            logFunction(f"Moving {motor} smoothly to {target_angle} degrees...")
            
            if motor:
                # 1. Take the current position and set the motor to non-compliant for smooth movement
                current_pos = motor.present_position
                motor.compliant = False
                
                # 2. Calculate the amplitude of movement
                amplitude = target_angle - current_pos
                
                # 3. With Cosine trajectory, move the motor to the target angle
                t = 0.0
                while t <= duration:
                    # Smooth factor based on cosine function for smooth acceleration and deceleration
                    smooth_factor = (1.0 - math.cos(math.pi * (t / duration))) / 2.0
                    current_target = current_pos + (amplitude * smooth_factor)
                    
                    motor.goto_position(current_target, dt, wait=False)
                    time.sleep(dt)
                    t += dt
                    
                    # For protected GUI applications, process events to keep the interface responsive
                    if process_events_callback:
                        process_events_callback()
                        
                # 4. After the loop, ensure the motor reaches the exact target angle
                motor.goto_position(target_angle, 0.1, wait=False)
                logFunction(f"{motor} successfully reached {target_angle} degrees.")
                
        except Exception as e:
            logFunction(f"Error moving {motor}: {str(e)}")

    def motor_movement_go_to(self, logFunction, target_angles, duration, movement_name, waitSituation=True, process_events_callback=None):
        # ... (The preparation phase can remain the same, where you find the motors and set compliant=False) ...
        active_motors = []
        for motor_name, target_angle in target_angles.items():
            motor = self.get_motor_by_name(motor_name)
            if motor:
                motor.compliant = False
                current_pos = motor.present_position
                amplitude = target_angle - current_pos
                
                active_motors.append({
                    'motor': motor,
                    'motor_name': motor_name,
                    'current_pos': current_pos,
                    'target_angle': target_angle,
                    'amplitude': amplitude
                })
        
        if not active_motors:
            logFunction(f"No valid motors found for {movement_name}.")
            return

        # 2. MOVEMENT PHASE (REAL-TIME LOOP)
        dt = 0.05
        start_time = time.time()  # Get the start time of the loop
        
        while True:
            # Calculate the actual elapsed time
            t = time.time() - start_time
            
            if t > duration:
                break # Break the loop if the duration has elapsed
                
            # Cosine smoothing factor
            smooth_factor = (1.0 - math.cos(math.pi * (t / duration))) / 2.0
            
            for m_data in active_motors:
                current_target = m_data['current_pos'] + (m_data['amplitude'] * smooth_factor)
                
                # IMPORTANT CHANGE: Set the target angle directly instead of using goto_position
                m_data['motor'].goal_position = current_target 
                # (If your library doesn't have goal_position, find the command that assigns the instantaneous angle, like set_goal_position(current_target))
            
            # Callback to prevent the UI from freezing
            if process_events_callback:
                process_events_callback()
                
            time.sleep(dt)

        # 3. FINISHING PHASE: Snap to the target one last time to close any remaining millimeter-level gaps
        for m_data in active_motors:
            m_data['motor'].goto_position(m_data['target_angle'], 0.1, wait=False)
            
        if waitSituation:
            time.sleep(0.1)

        logFunction(f"{movement_name} completed smoothly.")