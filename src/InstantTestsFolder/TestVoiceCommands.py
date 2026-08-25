import sys
import os
from pypot.creatures import PoppyTorso

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "../../"))
sys.path.append(root_dir)


from src.Controllers.VoiceController import VoiceController, RobotAction
from src.Controllers.SpeakerController import SpeakerController
from src.Movements.WaveHand import WaveMotion

# from src.Movements.WaveHand import wave_hand_function
# from src.Movements.SitDown import sit_down_function

voice_controller = VoiceController()
speaker_controller = SpeakerController()

poppy = None
wave_hand_motion_action = None  


while True:
    action = voice_controller.listen_and_get_action()
    
    if action == RobotAction.HELLO:
        print("In Hello Action")
        speaker_controller.speak("Hello there! It is nice to meet you.")
        if(poppy is None):
            poppy = PoppyTorso(check_full_config=False, camera='dummy')

            # Run the waving sequence
            if wave_hand_motion_action is None:
                wave_hand_motion_action = WaveMotion(poppy)
            wave_hand_motion_action.wave_left_hand(duration=5.0)
        else:
            # Run the waving sequence
            if wave_hand_motion_action is None:
                wave_hand_motion_action = WaveMotion(poppy)
            wave_hand_motion_action.wave_left_hand(duration=5.0)
        pass
    elif action == RobotAction.SIT_DOWN:
        print("In Sit Down Action") 
        # sit_down_function()
        pass
    elif action == RobotAction.UNKNOWN_COMMAND:
        pass
    elif action == RobotAction.SILENCE_OR_ERROR:
        pass
