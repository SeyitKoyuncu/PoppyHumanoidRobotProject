import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "../../"))
sys.path.append(root_dir)


from src.Controllers.VoiceController import VoiceController, RobotAction
from src.Controllers.SpeakerController import SpeakerController

# from src.Movements.VaweHand import wave_hand_function
# from src.Movements.SitDown import sit_down_function

voice_controller = VoiceController()
speaker_controller = SpeakerController()

while True:
    action = voice_controller.listen_and_get_action()
    
    if action == RobotAction.HELLO:
        print("In Hello Action")
        speaker_controller.speak("Hello there! It is nice to meet you.")
        # wave_hand_function()
        pass
    elif action == RobotAction.SIT_DOWN:
        print("In Sit Down Action") 
        # sit_down_function()
        pass
    elif action == RobotAction.UNKNOWN_COMMAND:
        pass
    elif action == RobotAction.SILENCE_OR_ERROR:
        pass
