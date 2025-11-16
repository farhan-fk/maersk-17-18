from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)

speech_file_path = "shipment_notification.mp3"

response = client.audio.speech.create(
    model="gpt-4o-mini-tts",  # or "tts-1" depending on what your account has
    voice="alloy",            # choose a voice: alloy, nova, echo, etc.
    input="Your container MAEU1234567 has arrived at Mumbai Port and is ready for pickup."
)

# Easiest way: let the SDK stream directly to file
response.stream_to_file(speech_file_path)

print(f"Saved audio to {speech_file_path}")
