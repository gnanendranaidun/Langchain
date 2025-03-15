import requests
import os
from dotenv import load_dotenv
load_dotenv()
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")

url = "https://api.sarvam.ai/text-analytics"
def analyze(context,question):
    payload = f"text={context}&questions={question}"
    headers = {
        "api-subscription-key": SARVAM_API_KEY,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.request("POST", url, data=payload, headers=headers)

    return response

