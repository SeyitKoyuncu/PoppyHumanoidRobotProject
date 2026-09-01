import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "../../"))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from src.Controllers.RobotController import RobotController
from src.Controllers.MotorRelaxController import force_relax_motors, relax_motors


controller = RobotController()
controller.connect(is_simulation=False)
#exclude_motors = ['r_elbow_y']
#exclude_motors = ['r_shoulder_x', 'r_shoulder_y', 'r_arm_z']

#First stiff motors for putin poppy in up position manually
controller.reset_all_motors_to_zero(duration=3.0, process_events_callback=None, exclude_motors=[])
target_step_1 = {
            'r_ankle_y': -3.0, 
            'l_ankle_y': -3.0,
        }
        
controller.motor_movement_go_to(
    target_angles=target_step_1, 
    duration=2.5, 
    movement_name="", 
    waitSituation=True
)
controller.disconnect()


while True:
    user_input = input("\nFor making free to motors input 'q': ")
    
    if user_input.strip().lower() == 'q':
        force_relax_motors()
        break
    else:
        print("Geçersiz tuş. Sadece 'q' tuşunu kullanabilirsiniz.")