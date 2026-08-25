import pyttsx3

class SpeakerController:
    def __init__(self, rate: int = 150, volume: float = 1.0):
        # Initialize pyttsx3 (Offline TTS Engine)
        self.engine = pyttsx3.init()
        
        # Voice rate and volume settings
        self.engine.setProperty('rate', rate) 
        self.engine.setProperty('volume', volume)
        
        # Optional: List available system voices (male/female) and select one
        # voices = self.engine.getProperty('voices')
        # self.engine.setProperty('voice', voices[1].id) # Typically 0 is male, 1 is female

    def speak(self, text: str):
        """
        Converts the received text to speech and plays it through the speaker.
        In the future, a more advanced AI model (such as Expressive TTS or 
        Zero-Shot Voice Cloning) can be seamlessly integrated here.
        """
        print(f"Robot says: '{text}'")
        self.engine.say(text)
        self.engine.runAndWait()