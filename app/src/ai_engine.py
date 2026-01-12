import os
import logging
import json
import aiohttp

logger = logging.getLogger(__name__)

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "")
GPT_HOST = "openai80.p.rapidapi.com"

async def generate_response(user_message: str) -> str:
    """
    Generate a chat response using GPT via RapidAPI (Async).
    """
    if not RAPIDAPI_KEY:
        return "⚠️ I can't think right now (Missing RAPIDAPI_KEY)."

    url = f"https://{GPT_HOST}/chat/completions"
    
    payload = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": "You are a helpful Telegram bot assistant."},
            {"role": "user", "content": user_message}
        ]
    }
    
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": GPT_HOST,
        "Content-Type": "application/json"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status != 200:
                    logger.error(f"GPT Error: {response.status}")
                    return "Sorry, my brain is offline."
                
                data = await response.json()
                return data['choices'][0]['message']['content']
    except Exception as e:
        logger.error(f"GPT error: {e}")
        return "Sorry, I'm having trouble connecting to my AI brain."

async def extract_job_params(user_message: str) -> dict:
    """
    Analyze text to extract job role and location.
    Returns dict: {'role': str, 'location': str, 'is_job_request': bool}
    """
    if not RAPIDAPI_KEY:
        return {"is_job_request": False}

    url = f"https://{GPT_HOST}/chat/completions"
    
    system_prompt = """
    Analyze the user's message. If they are looking for a job, extract the 'role' and 'location'.
    Return a JSON object with keys: 'is_job_request' (bool), 'role' (str), 'location' (str).
    If location is missing, default to 'Remote'.
    Example: "Find me python jobs in London" -> {"is_job_request": true, "role": "Python Developer", "location": "London"}
    Example: "Hello there" -> {"is_job_request": false}
    """

    payload = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "response_format": {"type": "json_object"}
    }
    
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": GPT_HOST,
        "Content-Type": "application/json"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status != 200:
                    return {"is_job_request": False}
                
                data = await response.json()
                content = data['choices'][0]['message']['content']
                return json.loads(content)
    except Exception as e:
        logger.error(f"Extraction error: {e}")
        return {"is_job_request": False}
