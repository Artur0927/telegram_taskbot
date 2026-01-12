import os
import requests

API_KEY = "AIzaSyCTGjefsqV7LXgQm-ZXhUqmLkRnV6EFnO8"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={API_KEY}"

data = {
    "contents": [{
        "parts": [{"text": "Hello, are you working?"}]
    }]
}

print(f"Testing API Key: {API_KEY[:10]}...")
response = requests.post(URL, json=data)

if response.status_code == 200:
    print("✅ SUCCESS! API Key is working.")
    print("Response:", response.json()['candidates'][0]['content']['parts'][0]['text'])
else:
    print(f"❌ FAILED! Status Code: {response.status_code}")
    print("Error:", response.text)
