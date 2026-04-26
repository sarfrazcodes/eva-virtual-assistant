import pyttsx3
from eva.utils.logger import get_logger
from eva.utils.helpers import sanitize_for_tts
from eva.utils.ui import ui_state

logger = get_logger("EVA.voice.speaker")

# Initialize the pyttsx3 engine once at module level
engine = None

def _get_engine():
    global engine
    if engine is None:
        try:
            engine = pyttsx3.init()
            
            # Select Female Voice ("Zira" or fallback to any female)
            voices = engine.getProperty('voices')
            for voice in voices:
                voice_name = voice.name.lower()
                if "zira" in voice_name or "female" in voice_name:
                    engine.setProperty('voice', voice.id)
                    break
                    
            set_voice_properties(rate=170, volume=0.9)
        except Exception as e:
            logger.error(f"Failed to initialize TTS engine: {e}")
    return engine

def set_voice_properties(rate: int = 170, volume: float = 0.9):
    """Configure voice speed and volume."""
    global engine
    if engine is None:
        return
    try:
        engine.setProperty('rate', rate)
        engine.setProperty('volume', volume)
    except Exception as e:
        logger.warning(f"Could not set voice properties: {e}")

def speak(text: str) -> None:
    """Speaks text aloud, also prints it."""
    engine_instance = _get_engine()
    if not text:
        return
        
    print(f"\nEVA: {text}\n")
    logger.info(f"Speaking: {text}")
    
    # Update UI
    ui_state.status = "speaking..."
    
    if engine_instance is None:
        logger.error("TTS engine not available.")
        ui_state.status = "idle"
        return
        
    try:
        clean_text = sanitize_for_tts(text)
        if clean_text:
            engine_instance.say(clean_text)
            engine_instance.runAndWait()
    except Exception as e:
        logger.error(f"Error during TTS generation: {e}")
        
    ui_state.status = "idle"

def stop_speaking():
    """Interrupt current speech."""
    engine_instance = _get_engine()
    if engine_instance:
        try:
            engine_instance.stop()
        except Exception as e:
            logger.error(f"Error stopping speech: {e}")

if __name__ == "__main__":
    speak("Hello, this is a test of the EVA speaker module.")
