import string
import re
from datetime import datetime
import random

def clean_text(text: str) -> str:
    """Strip punctuation, lowercase, and normalize whitespace."""
    if not text:
        return ""
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    return " ".join(text.split())

def extract_keywords(text: str, top_n: int = 5) -> list[str]:
    """Simple keyword extraction without NLTK."""
    stop_words = {"a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for", "is", "are", "am", "was", "were", "be", "been", "this", "that", "it", "of", "with", "my", "your"}
    words = clean_text(text).split()
    keywords = [w for w in words if w not in stop_words]
    # Filter unique but maintain some order of frequency context (very basic)
    seen = set()
    result = []
    for w in keywords:
        if w not in seen:
            seen.add(w)
            result.append(w)
    return result[:top_n]

def confirm(question: str) -> bool:
    """CLI yes/no prompt."""
    while True:
        resp = input(f"{question} [y/n]: ").strip().lower()
        if resp in ['y', 'yes', 'haan']:
            return True
        if resp in ['n', 'no', 'nahi']:
            return False
        print("Please answer y or n.")

def format_response(text: str, style: str = "hinglish") -> str:
    """Add personality tone to responses. 
    (In real use, LLM takes care of this via prompt. 
    Here it just strips and prepares text)."""
    return text.strip()

def get_current_datetime() -> dict:
    """Returns dict with date, time, day, month, year."""
    now = datetime.now()
    return {
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%I:%M %p"),
        "day": now.strftime("%A"),
        "month": now.strftime("%B"),
        "year": str(now.year)
    }

def safe_filename(name: str) -> str:
    """Converts any string to a valid filename."""
    return re.sub(r'[^a-zA-Z0-9_\-]', '_', name).strip('_')

def sanitize_for_tts(text: str) -> str:
    """Removes emojis, special characters, and unreadable punctuation for TTS."""
    if not text: return ""
    
    # Remove emojis
    text = re.sub(r'[\U00010000-\U0010ffff]', '', text)
    text = re.sub(r'[*#@~^|\[\]\{\}]', '', text)
    
    # Fix broken spaced words (e.g. "a a p" -> "aap")
    while re.search(r'\b([a-zA-Z])\s+([a-zA-Z])\b', text):
        text = re.sub(r'\b([a-zA-Z])\s+([a-zA-Z])\b', r'\1\2', text)
        
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def get_affirmation() -> str:
    """Returns a randomized, strict female persona affirmation."""
    options = [
        "done Sarfraz",
        "all set",
        "ready hai, check kar lo",
        "ho gaya",
        "perfect, done"
    ]
    return random.choice(options)

def fix_typos(text: str) -> str:
    """Handles common typos in speech or text."""
    replacements = {
        "opn": "open",
        "chrom": "chrome",
        "chat gpt": "chatgpt"
    }
    words = text.split()
    fixed = [replacements.get(w.lower(), w) for w in words]
    return " ".join(fixed)

if __name__ == "__main__":
    # Internal Tests
    print("Clean Test:", clean_text("Hello, World!!   This is EVA!"))
    print("Keywords:", extract_keywords("Hello, World!! This is EVA and I am a software!"))
    print("Time:", get_current_datetime())
    print("Safe Filename:", safe_filename("My File: Name/Version 1.0!"))
