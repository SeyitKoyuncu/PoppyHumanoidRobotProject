import sys
import os
from pypot.creatures import PoppyTorso
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("API_KEY")
base_url = os.getenv("BASE_URL")

client = OpenAI(api_key=api_key, base_url=base_url)

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
    
    try:
        print(action.value)
        if(action.value not in [4,5]):
            chat_completion = client.chat.completions.create(
            model="google.gemini-3.8-flash", 
            messages=[{"role": "system", "content": "You are a friendly assistant humanoid robot, named Poppy. Create a short and friendly response to the following command. Max 15 words."},
            {"role": "user", "content": "" + action.name}])
        
            LLM_response = chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Error: {e}")

    
    if action == RobotAction.HELLO:
        print("In Hello Action")
        speaker_controller.speak(LLM_response)
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

    elif action == RobotAction.HOWAREU:
        print("In How Are You Action") 
        speaker_controller.speak(LLM_response)
        pass
    elif action == RobotAction.UNKNOWN_COMMAND:
        pass
    elif action == RobotAction.SILENCE_OR_ERROR:
        pass