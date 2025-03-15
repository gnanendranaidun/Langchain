import requests
import os
from dotenv import load_dotenv
url = "https://api.sarvam.ai/transliterate"
load_dotenv()
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
def transliterate(input_text, source_language_code, target_language_code):
    payload = {
        "spoken_form": False,
        "input": input_text,
        "source_language_code": source_language_code,
        "target_language_code": target_language_code,
        "spoken_form_numerals_language": "english"
    }
    headers = {
        "api-subscription-key": SARVAM_API_KEY,
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)
    return response.json()