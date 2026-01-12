"""
AI Engine - Google Gemini integration for text generation.
"""

import os
import logging
import google.generativeai as genai

# Configure logging
logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY", ""))

# Initialize model
model = genai.GenerativeModel("gemini-2.0-flash")


async def generate_response(user_message: str) -> str:
    """
    Generate a response using Google Gemini.
    
    Args:
        user_message: The user's input message.
        
    Returns:
        Generated response text.
    """
    try:
        system_prompt = """You are a helpful, friendly AI assistant in a Telegram bot.
Be concise but informative. Use emojis occasionally to be engaging.
Keep responses under 500 words unless the user asks for detailed explanations."""

        response = await model.generate_content_async(
            f"{system_prompt}\n\nUser: {user_message}",
            generation_config=genai.GenerationConfig(
                temperature=0.7,
                max_output_tokens=1024,
            )
        )
        
        return response.text
        
    except Exception as e:
        logger.error(f"Gemini error: {e}")
        return f"❌ Sorry, I encountered an error: {str(e)}"
