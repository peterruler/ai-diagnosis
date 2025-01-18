from dotenv import load_dotenv
import openai
import os

# Load environment variables
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
openai.api_key = api_key  # Use the key from .env file

audio_file = open("temp_audio.mp3", "rb")
transcription = openai.Audio.transcribe(
    model="whisper-1", 
    file=audio_file,
)

print(transcription['text'])