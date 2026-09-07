import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("API_KEY")
base_url = os.getenv("BASE_URL")
# Client initialisieren
client = OpenAI(api_key=api_key, base_url=base_url)
try:
    # Chat-Anfrage senden
 chat_completion = client.chat.completions.create(
 model="google.gemini-3.8-flash", # Wählen Sie hier das passende Modell
 messages=[{"role": "system", "content": "You are a friendly assistant humanoid robot, named Poppy."},
 {"role": "user", "content": "Hello,wie geht  es dir?"}
    ] # oder "speech" je nach gewünschter Modalität

    )
 # Antwort ausgeben
 print(chat_completion.choices[0].message.content)
except Exception as e:
    print(f"Ein Fehler ist aufgetreten: {e}")