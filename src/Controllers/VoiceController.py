import speech_recognition as sr
from enum import Enum
from typing import Optional

class RobotAction(Enum):
    HELLO = 1
    SIT_DOWN = 2
    STAND_UP = 3
    UNKNOWN_COMMAND = 4
    SILENCE_OR_ERROR = 5

class VoiceController:
    def __init__(self, target_mic_name: str = "USB PnP Sound Device"): 
        self.recognizer = sr.Recognizer()
        
        print("--- Available Microphone Devices ---")
        mic_names = sr.Microphone.list_microphone_names()
        
        device_index = self._find_microphone_index(target_mic_name, mic_names)
        
        if device_index is not None:
            print(f"Target microphone containing '{target_mic_name}' found at index {device_index}.")
            self.microphone = sr.Microphone(device_index=device_index)
        else:
            print(f"Target microphone '{target_mic_name}' not found. Falling back to default...")
            self.microphone = sr.Microphone()

        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)

    def _match_intent(self, transcribed_text: str) -> RobotAction:
        text = transcribed_text.lower().strip()

        hello_keywords = ["hello", "hi", "hey", "greetings"]
        sit_keywords = ["sit", "sit down", "take a seat"]
        stand_keywords = ["stand", "stand up", "get up"]

        if any(keyword in text for keyword in hello_keywords):
            return RobotAction.HELLO
        
        if any(keyword in text for keyword in sit_keywords):
            return RobotAction.SIT_DOWN
            
        if any(keyword in text for keyword in stand_keywords):
            return RobotAction.STAND_UP

        return RobotAction.UNKNOWN_COMMAND

    def _find_microphone_index(self, target_name: str, mic_names: list) -> Optional[int]:
        for index, name in enumerate(mic_names):
            if target_name.lower() in name.lower():
                return index
        return None

    def listen_and_get_action(self) -> RobotAction:
        try:
            print("Listening for command...")
            with self.microphone as source:
                audio_data = self.recognizer.listen(
                    source, 
                    timeout=5, 
                    phrase_time_limit=5
                )
            
            transcribed_text = self.recognizer.recognize_google(audio_data)
            print(f"Transcribed: {transcribed_text}")
            return self._match_intent(transcribed_text)

        except sr.WaitTimeoutError:
            return RobotAction.SILENCE_OR_ERROR
        except sr.UnknownValueError:
            return RobotAction.UNKNOWN_COMMAND
        except sr.RequestError:
            return RobotAction.SILENCE_OR_ERROR
        except Exception:
            return RobotAction.SILENCE_OR_ERROR