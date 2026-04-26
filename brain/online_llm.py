import os
import requests
from openai import OpenAI
from eva.config import OPENAI_API_KEY, OPENAI_MODEL, GEMINI_API_KEY
from eva.utils.logger import get_logger

logger = get_logger("EVA.brain.online_llm")

def ask_openai(prompt: str, system_prompt: str = None) -> str:
    """Send prompt to OpenAI."""
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is not set.")
        
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    if system_prompt is None:
        system_prompt = "You are EVA, an AI assistant. Keep responses helpful, concise, and friendly."
        
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]
    
    logger.debug(f"Sending prompt to OpenAI {OPENAI_MODEL}...")
    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"OpenAI error: {e}")
        return f"OpenAI error: {str(e)}"

def ask_gemini(prompt: str) -> str:
    """Send prompt to Gemini using REST API."""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set.")
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    logger.debug("Sending prompt to Gemini...")
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return f"Gemini API error: {str(e)}"

if __name__ == "__main__":
    # Test requires keys
    if OPENAI_API_KEY:
        print("OpenAI say:", ask_openai("Hello, are you there?"))
    if GEMINI_API_KEY:
        print("Gemini say:", ask_gemini("Hello, are you there?"))
