import requests
import json
from eva.config import OLLAMA_BASE_URL, OLLAMA_MODEL
from eva.utils.logger import get_logger

logger = get_logger("EVA.brain.local_llm")

def ask_local(prompt: str, system_prompt: str = None) -> str:
    """POST to Ollama /api/generate, return response text."""
    url = f"{OLLAMA_BASE_URL}/api/generate"
    
    if system_prompt is None:
        system_prompt = "You are EVA, an AI assistant. Keep responses helpful, concise, and friendly."
        
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "system": system_prompt,
        "stream": False,
        "keep_alive": "5m"
    }
    
    logger.debug(f"Sending prompt to local {OLLAMA_MODEL}: {prompt[:50]}...")
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "")
    except requests.exceptions.RequestException as e:
        logger.error(f"Local LLM connection error: {e}")
        return "Local LLM connect nahi ho raha hai. Is Ollama running?"
    except Exception as e:
        logger.error(f"Unexpected error in local LLM: {e}")
        return "Error occurred while talking to local LLM."

def ask_local_json(prompt: str, system_prompt: str = None) -> dict:
    """Forces local LLM to return strict JSON and parses it safely."""
    url = f"{OLLAMA_BASE_URL}/api/generate"
    
    if system_prompt is None:
        system_prompt = "You are an intent parser. Return ONLY valid JSON."
        
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "system": system_prompt,
        "stream": False,
        "format": "json",
        "keep_alive": "5m"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        text = data.get("response", "{}")
        return json.loads(text)
    except json.JSONDecodeError:
        logger.error("Failed to decode JSON from LLM")
        return {"intent": "general_chat", "entities": [prompt]}
    except Exception as e:
        logger.error(f"Local LLM JSON error: {e}")
        return {"intent": "general_chat", "entities": [prompt]}

def is_ollama_running() -> bool:
    """Check if Ollama server is reachable."""
    try:
        response = requests.get(OLLAMA_BASE_URL, timeout=3)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def list_available_models() -> list[str]:
    """Query available local models."""
    url = f"{OLLAMA_BASE_URL}/api/tags"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        models = [m["name"] for m in response.json().get("models", [])]
        return models
    except Exception as e:
        logger.error(f"Failed to fetch models from Ollama: {e}")
        return []

if __name__ == "__main__":
    if is_ollama_running():
        print("Models:", list_available_models())
        print("Response:", ask_local("Who are you?", system_prompt="You are EVA."))
    else:
        print("Ollama is not running.")
