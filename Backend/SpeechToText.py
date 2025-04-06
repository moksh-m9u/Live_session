import logging
import os
from groq import Groq
from dotenv import dotenv_values

# Load environment variables
env_values = dotenv_values(".env")
GroqAPIKey = env_values.get("GroqAPIKey")

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Directory setup
TempDirPath = "Data"
if not os.path.exists(TempDirPath):
    os.makedirs(TempDirPath)

def transcribe_with_groq(stt_model, audio_filepath, api_key=GroqAPIKey):
    """Transcribe the audio file using Groq's STT model."""
    try:
        client = Groq(api_key=api_key)
        with open(audio_filepath, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model=stt_model,
                file=audio_file,
                language="en"
            )
        logging.info(f"Transcription successful: {transcription.text}")
        return transcription.text
    except Exception as e:
        logging.error(f"Error during transcription: {e}")
        return f"Error during transcription: {e}"

def SpeechRecognition(audio_filepath):
    """Convert speech to text using Groq STT."""
    if not os.path.exists(audio_filepath):
        logging.error(f"Audio file not found at {audio_filepath}")
        return "Sorry, audio file not found."
    
    text = transcribe_with_groq("whisper-large-v3", audio_filepath)
    return text

if __name__ == "__main__":
    print(SpeechRecognition("Data/patient_voice_test.mp3"))