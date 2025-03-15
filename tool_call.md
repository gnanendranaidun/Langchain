# Sarvam AI Tool Calling Service API Documentation

## Overview

The Sarvam AI Tool Calling Service provides several endpoints for text-to-speech (TTS), speech-to-text (STT), transliteration, and text analytics. This API is built using FastAPI and allows users to interact with various AI services.

## Base URL

The base URL for the API is `http://<your-server-address>/`.

## Endpoints

### 1. Text-to-Speech (TTS)

- **Endpoint:** `/tts/`
- **Method:** `POST`
- **Description:** Converts text to speech using Sarvam AI's TTS API.

#### Request Body

```json
{
    "text": "Your text here",
    "target_language_code": "en-IN",
    "speaker": "neel",
    "model": "bulbul:v1",
    "pitch": 0,
    "pace": 1.0,
    "loudness": 1.0
}
```

#### Example Request

```bash
curl -X POST "http://<your-server-address>/tts/" -H "Content-Type: application/json" -d '{"text": "Hello, world!", "target_language_code": "en-IN"}'
```

#### Response

```json
{
    "status": "success",
    "message": "Audio generated successfully",
    "files": ["output0.wav"]
}
```

### 2. Speech-to-Text (STT)

- **Endpoint:** `/stt/`
- **Method:** `POST`
- **Description:** Converts speech to text using Sarvam AI's STT API.

#### Request Body

- **File:** Upload the audio file.
- **Query Parameter:** `language_code` (optional, default is `en-IN`).

#### Example Request

```bash
curl -X POST "http://<your-server-address>/stt/?language_code=en-IN" -F "file=@path_to_your_audio_file.wav"
```

#### Response

```json
{
    "status": "success",
    "transcription": "Transcribed text here"
}
```

### 3. Transliteration

- **Endpoint:** `/transliterate/`
- **Method:** `POST`
- **Description:** Transliterate text from one script to another using Sarvam AI's Transliteration API.

#### Request Body

```json
{
    "text": "Your text here",
    "source_language_code": "source_lang_code",
    "target_language_code": "target_lang_code"
}
```

#### Example Request

```bash
curl -X POST "http://<your-server-address>/transliterate/" -H "Content-Type: application/json" -d '{"text": "Hello", "source_language_code": "en", "target_language_code": "hi"}'
```

#### Response

```json
{
    "status": "success",
    "result": "Transliterated text here"
}
```

### 4. Text Analytics

- **Endpoint:** `/text_analytics/`
- **Method:** `POST`
- **Description:** Perform text analytics using Sarvam AI's Text Analytics API.

#### Request Body

```json
{
    "context": "Your context here",
    "question": "Your question here"
}
```

#### Example Request

```bash
curl -X POST "http://<your-server-address>/text_analytics/" -H "Content-Type: application/json" -d '{"context": "Some context", "question": "What is this about?"}'
```

#### Response

```json
{
    "status": "success",
    "result": "Analytics result here"
}
```

### 5. Get Generated Audio Files

- **Endpoint:** `/audio/{filename}`
- **Method:** `GET`
- **Description:** Retrieve a generated audio file.

#### Example Request

```bash
curl -X GET "http://<your-server-address>/audio/output0.wav"
```

#### Response

- Returns the audio file if it exists, otherwise a 404 error.

## Home Endpoint

- **Endpoint:** `/`
- **Method:** `GET`
- **Description:** Returns a welcome message.

#### Example Request

```bash
curl -X GET "http://<your-server-address>/"
```

#### Response

```json
{
    "message": "Welcome to the Sarvam AI Tool Calling Service!"
}
```

## Error Handling

In case of errors, the API will return a response with a status code and a detail message. For example:

```json
{
    "status": "error",
    "message": "Failed to generate audio files"
}
```

## Conclusion

This API provides a simple interface to leverage Sarvam AI's capabilities for TTS, STT, transliteration, and text analytics. Make sure to handle errors appropriately and validate inputs as needed.