import requests
import base64
import wave
import os
from dotenv import load_dotenv
load_dotenv()
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
def text_to_speech_sarvam(text, target_language_code, api_key=SARVAM_API_KEY, speaker="neel", model="bulbul:v1", pitch=0, pace=1.0, loudness=1.0, chunk_size=500):
    url = "https://api.sarvam.ai/text-to-speech"
    headers = {
        "Content-Type": "application/json",
        "api-subscription-key": api_key
    }
    
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    print(f"Total chunks: {len(chunks)}")
    
    for i, chunk in enumerate(chunks):
        payload = {
            "inputs": [chunk],
            "target_language_code": target_language_code,
            "speaker": speaker,
            "model": model,
            "pitch": pitch,
            "pace": pace,
            "loudness": loudness,
            "enable_preprocessing": True,
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            audio = response.json().get("audios", [None])[0]
            if audio:
                audio = base64.b64decode(audio)
                with wave.open(f"output{i}.wav", "wb") as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(22050)
                    wav_file.writeframes(audio)
                print(f"Audio file {i} saved successfully as 'output{i}.wav'!")
            else:
                print(f"No audio data received for chunk {i}.")
        else:
            print(f"Error for chunk {i}: {response.status_code}")
            print(response.json())
