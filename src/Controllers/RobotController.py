import math
import time
import numpy as np
import os
import ikpy.chain
from ikpy.link import OriginLink, URDFLink


if not hasattr(np, 'float'):
    np.float = float

    
try:
    from pypot.creatures import PoppyHumanoid
except ImportError:
    PoppyHumanoid = None

try:
    import ikpy.chain
except ImportError:
    ikpy = None


class RobotController:
    """Handles all pypot hardware, simulation interactions, and Cartesian IK control."""
    
    def __init__(self, log_callback=None):
        self.robot = None
        self.log = log_callback if log_callback else print
        self.ik_chains = {}  # Holds IKPy kinematic chains for arms

    def connect(self, is_simulation=True, is_camera_dummy=True):
        if PoppyHumanoid is None:
            self.log("ERROR: 'pypot' library not found.")
            return False

        try:
            if is_simulation:
                self.robot = PoppyHumanoid(simulator='vrep')
            else:
                self.robot = PoppyHumanoid(camera='dummy' if is_camera_dummy else None)
            
            # Initialize kinematic chains after connecting the robot
            self._init_ik_chains()
            return True
        except Exception as e:
            self.log(f"Connection failed: {str(e)}")
            return False

    def disconnect(self):
        if self.robot:
            self.robot.close()
            self.robot = None
            self.ik_chains.clear()

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

    def reset_all_motors_to_zero(self, duration=3.0, process_events_callback=None, exclude_motors=None):
        """Resets all motors to 0 degrees using a smooth cosine trajectory."""
        self.log("Starting to reset all motors to zero degrees...")

        motor_names = self.get_motor_names()

        if not motor_names:
            self.log("WARNING: No motors found to reset. Is the robot connected?")
            return

        target_angles = {
            motor_name: (10.0 if motor_name == 'r_elbow_y' else 0.0)
            for motor_name in motor_names 
            if motor_name not in exclude_motors
        }
        
        self.motor_movement_go_to(
            logFunction=self.log,
            target_angles=target_angles,
            duration=duration,
            movement_name="Reset_All_Motors_To_Zero",
            waitSituation=True,
            process_events_callback=process_events_callback
        )

    # =========================================================================
    # KINEMATICS (IK & FK) INFRASTRUCTURE
    # =========================================================================

    def _init_ik_chains(self):
        """Builds the arm kinematic chains directly in code without requiring a URDF file."""
        if ikpy is None:
            self.log("ERROR: 'ikpy' is not installed.")
            return

        # Poppy arm lengths (in meters)
        L_UPPER_ARM = 0.18  # Shoulder to elbow (~18 cm)
        L_FOREARM = 0.15  # Elbow to end-effector / hand tip (~15 cm)

        arms_data = {
            'r_arm': {
                'shoulder_offset': [0.0, -0.14, 0.18],  # From torso center to right shoulder
                'motors': [
                    'r_shoulder_y',
                    'r_shoulder_x',
                    'r_arm_z',
                    'r_elbow_y',
                ],
            },
            'l_arm': {
                'shoulder_offset': [0.0, 0.14, 0.18],  # From torso center to left shoulder
                'motors': [
                    'l_shoulder_y',
                    'l_shoulder_x',
                    'l_arm_z',
                    'l_elbow_y',
                ],
            },
        }

        for arm_name, cfg in arms_data.items():
            try:
                links = [
                    OriginLink(),
                    # 1. Torso to shoulder transition + shoulder_y (Pitch)
                    URDFLink(
                        name=cfg['motors'][0],
                        bounds=(-math.pi, math.pi),
                        translation_vector=cfg['shoulder_offset'],
                        orientation=[0, 0, 0],
                        rotation=[0, 1, 0],
                    ),
                    # 2. shoulder_x (Roll)
                    URDFLink(
                        name=cfg['motors'][1],
                        bounds=(-math.pi, math.pi),
                        translation_vector=[0, 0, 0],
                        orientation=[0, 0, 0],
                        rotation=[1, 0, 0],
                    ),
                    # 3. arm_z (Yaw) + Upper arm length
                    URDFLink(
                        name=cfg['motors'][2],
                        bounds=(-math.pi, math.pi),
                        translation_vector=[0, 0, -L_UPPER_ARM],
                        orientation=[0, 0, 0],
                        rotation=[0, 0, 1],
                    ),
                    # 4. elbow_y (Elbow Pitch) + Forearm / hand length
                    URDFLink(
                        name=cfg['motors'][3],
                        bounds=(0, math.pi),  # Elbow typically flexes in one direction
                        translation_vector=[0, 0, -L_FOREARM],
                        orientation=[0, 0, 0],
                        rotation=[0, 1, 0],
                    ),
                ]

                # Build the chain: First link (OriginLink) is fixed, remaining 4 links are active motors
                chain = ikpy.chain.Chain(
                    name=arm_name,
                    links=links,
                    active_links_mask=[False, True, True, True, True],
                )

                self.ik_chains[arm_name] = {'chain': chain, 'motor_names': cfg['motors']}
                self.log(f"IK chain successfully built in code: {arm_name}")

            except Exception as e:
                self.log(f"ERROR: Exception occurred while setting up {arm_name} chain: {str(e)}")

    def get_arm_cartesian_position(self, arm_name='r_arm'):
        """Returns current [x, y, z] coordinates of the end-effector using forward kinematics (FK) (in meters)."""
        if arm_name not in self.ik_chains:
            self.log(f"IK chain for {arm_name} is not initialized.")
            return None

        chain_info = self.ik_chains[arm_name]
        chain = chain_info['chain']
        motor_names = chain_info['motor_names']

        current_angles_rad = [0.0] * len(chain.links)
        for i, link in enumerate(chain.links):
            if link.name in motor_names:
                motor = self.get_motor_by_name(link.name)
                if motor:
                    current_angles_rad[i] = math.radians(motor.present_position)

        fk_matrix = chain.forward_kinematics(current_angles_rad)
        xyz = fk_matrix[:3, 3]  # The last column provides the translation
        return xyz.tolist()

    def calculate_arm_ik(self, arm_name, target_xyz):
        """
        Calculates joint angles for target [x, y, z] coordinates.
        Returns: Dictionary of {'motor_name': target_degree, ...}.
        """
        if arm_name not in self.ik_chains:
            self.log(f"IK chain for {arm_name} is not initialized.")
            return None

        chain_info = self.ik_chains[arm_name]
        chain = chain_info['chain']
        motor_names = chain_info['motor_names']

        # Pass current angles as initial guess to prevent the numerical solver from falling into local minima
        initial_angles_rad = [0.0] * len(chain.links)
        for i, link in enumerate(chain.links):
            if link.name in motor_names:
                motor = self.get_motor_by_name(link.name)
                if motor:
                    initial_angles_rad[i] = math.radians(motor.present_position)

        # Inverse kinematics solution (in meters)
        ik_angles_rad = chain.inverse_kinematics(
            target_position=target_xyz,
            initial_position=initial_angles_rad
        )

        target_joint_angles = {}
        for i, link in enumerate(chain.links):
            if link.name in motor_names:
                target_joint_angles[link.name] = math.degrees(ik_angles_rad[i])

        return target_joint_angles

    def move_arm_cartesian(self, arm_name, target_xyz, duration=2.5, process_events_callback=None, waitSituation=True):
        """
        Moves the end-effector to the target [x, y, z] point in Cartesian space
        using the cosine smoothing profile of the motor_movement_go_to function.
        """
        self.log(f"Directing {arm_name} to target: X={target_xyz[0]:.3f}, Y={target_xyz[1]:.3f}, Z={target_xyz[2]:.3f} m")
        
        target_angles = self.calculate_arm_ik(arm_name, target_xyz)
        if not target_angles:
            self.log("Failed to compute IK solution. Movement canceled.")
            return False

        # Trigger smooth cosine trajectory execution
        self.motor_movement_go_to(
            logFunction=self.log,
            target_angles=target_angles,
            duration=duration,
            movement_name=f"IK_{arm_name}_Cartesian_Move",
            waitSituation=waitSituation,
            process_events_callback=process_events_callback
        )
        return True

    # =========================================================================
    # MOTOR AND TRAJECTORY MOTION METHODS
    # =========================================================================

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
                current_pos = motor.present_position
                motor.compliant = False
                amplitude = target_angle - current_pos
                
                t = 0.0
                while t <= duration:
                    smooth_factor = (1.0 - math.cos(math.pi * (t / duration))) / 2.0
                    current_target = current_pos + (amplitude * smooth_factor)
                    
                    motor.goto_position(current_target, dt, wait=False)
                    time.sleep(dt)
                    t += dt
                    
                    if process_events_callback:
                        process_events_callback()
                        
                motor.goto_position(target_angle, 0.1, wait=False)
                logFunction(f"{motor} successfully reached {target_angle} degrees.")
                
        except Exception as e:
            logFunction(f"Error moving {motor}: {str(e)}")

    def motor_movement_go_to(self, target_angles, duration, movement_name, logFunction = None, waitSituation=True, process_events_callback=None, torque_limit=None):

        # ... (The preparation phase can remain the same, where you find the motors and set compliant=False) ...
        active_motors = []
        for motor_name, target_angle in target_angles.items():
            motor = self.get_motor_by_name(motor_name)
            if motor:
                motor.compliant = False
                if torque_limit is not None and torque_limit["motor_name"] == motor_name:
                    motor.torque_limit = torque_limit["torque_limit_value"]
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
            if logFunction:
                logFunction(f"No valid motors found for {movement_name}.")  
            return

        dt = 0.05
        start_time = time.time()
        
        while True:
            t = time.time() - start_time
            if t > duration:
                break
                
            smooth_factor = (1.0 - math.cos(math.pi * (t / duration))) / 2.0
            
            for m_data in active_motors:
                current_target = m_data['current_pos'] + (m_data['amplitude'] * smooth_factor)
                m_data['motor'].goal_position = current_target 
            
            if process_events_callback:
                process_events_callback()
                
            time.sleep(dt)

        for m_data in active_motors:
            m_data['motor'].goto_position(m_data['target_angle'], 0.1, wait=False)
            
        if waitSituation:
            time.sleep(0.1)

        if logFunction:
            logFunction(f"{movement_name} completed smoothly.")


