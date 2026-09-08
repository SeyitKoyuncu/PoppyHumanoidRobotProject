import sys
import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from pypot.creatures import PoppyTorso

load_dotenv()

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "../../"))
sys.path.append(root_dir)


from src.Controllers.VoiceController import VoiceController, RobotAction
from src.Controllers.SpeakerController import SpeakerController
from src.Movements.WaveHand import WaveMotion

# from src.Movements.WaveHand import wave_hand_function
# from src.Movements.SitDown import sit_down_function

api_key = os.getenv("API_KEY")
base_url = os.getenv("BASE_URL")
client = OpenAI(api_key=api_key, base_url=base_url)

voice_controller = VoiceController()
speaker_controller = SpeakerController()

poppy = None
wave_hand_motion_action = None  

SYSTEM_PROMPT = "You are a friendly assistant humanoid robot, named Poppy. You can perform actions based on voice commands."

while True:

    text = voice_controller.listen_and_get_text()

    if not text or text.strip() == "":
        print("No text received. Please try again.")
        continue
    try:
        chat_completion = client.chat.completions.create(
            model="google.gemini-3.8-flash",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ]
        )
        response_content = chat_completion.choices[0].message.content
        response_json = json.loads(response_content)
        robot_speech = response_json.get("response", "I didn't understand that.")
        action = response_json.get("action", RobotAction.UNKNOWN_COMMAND)
        speaker_controller.speak(robot_speech)
        if text == RobotAction.HELLO:
            print("In Hello Action")
            speaker_controller.speak(response_content)
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

    except json.JSONDecodeError:
        print(f"ERROR: The LLM sent something outside of JSON format. Raw data: {response_content}")
        speaker_controller.speak("There was a problem processing the response.")
        
    except Exception as e:
        print(f"An error occurred: {e}")
