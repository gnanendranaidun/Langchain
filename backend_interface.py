from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, Optional, List
import os
import asyncio
import tempfile
import shutil
from TTS import text_to_speech_sarvam
from STT import transcribe_audio
from Text_analytics import analyze
from Transliteration import transliterate


app = FastAPI()

class TextInput(BaseModel):
    text: str
    language_code: str = "en-IN"

class TransliterationInput(BaseModel):
    text: str
    source_language_code: str
    target_language_code: str
    
class TextAnalyticsInput(BaseModel):
    context: str
    question: str

class TTSInput(BaseModel):
    text: str
    target_language_code: str = "en-IN"
    speaker: str = "neel"
    model: str = "bulbul:v1"
    pitch: float = 0
    pace: float = 1.0
    loudness: float = 1.0

@app.post("/tts/")
async def text_to_speech(input: TTSInput):
    """Convert text to speech using Sarvam AI's TTS API."""
    try:
        # Call the TTS function
        text_to_speech_sarvam(
            text=input.text,
            target_language_code=input.target_language_code,
            speaker=input.speaker,
            model=input.model,
            pitch=input.pitch,
            pace=input.pace,
            loudness=input.loudness
        )
        
        # Return the path to the first output file
        # Note: This assumes the TTS function creates files named output0.wav, output1.wav, etc.
        if os.path.exists("output0.wav"):
            return {"status": "success", "message": "Audio generated successfully", "files": ["output0.wav"]}
        else:
            return {"status": "error", "message": "Failed to generate audio files"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS processing error: {str(e)}")

@app.post("/stt/")
async def speech_to_text(file: UploadFile = File(...), language_code: str = "en-IN"):
    """Convert speech to text using Sarvam AI's STT API."""
    try:
        # Save the uploaded file temporarily
        temp_file_path = f"temp_{file.filename}"
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process the audio file
        transcription = await transcribe_audio(temp_file_path, language_code)
        
        # Clean up the temporary file
        os.remove(temp_file_path)
        
        return {"status": "success", "transcription": transcription}
    except Exception as e:
        # Clean up in case of error
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(status_code=500, detail=f"STT processing error: {str(e)}")

@app.post("/transliterate/")
async def transliterate_text(input: TransliterationInput):
    """Transliterate text from one script to another using Sarvam AI's Transliteration API."""
    try:
        result = transliterate(
            input_text=input.text,
            source_language_code=input.source_language_code,
            target_language_code=input.target_language_code
        )
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transliteration error: {str(e)}")

@app.post("/text_analytics/")
async def text_analytics(input: TextAnalyticsInput):
    """Perform text analytics using Sarvam AI's Text Analytics API."""
    try:
        result = analyze(context=input.context, question=input.question)
        return {"status": "success", "result": result.json() if hasattr(result, 'json') else result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text analytics error: {str(e)}")

@app.get("/")
def home():
    return {"message": "Welcome to the Sarvam AI Tool Calling Service!"}

# Endpoint to get generated audio files
@app.get("/audio/{filename}")
async def get_audio(filename: str):
    """Get a generated audio file."""
    if os.path.exists(filename):
        return FileResponse(filename)
    raise HTTPException(status_code=404, detail="Audio file not found")
