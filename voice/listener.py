import speech_recognition as sr
from eva.utils.logger import get_logger
from eva.utils.helpers import fix_typos
from eva.utils.ui import ui_state

logger = get_logger("EVA.voice.listener")

# Initialize recognizer
recognizer = sr.Recognizer()

def listen_once() -> str | None:
    """Records one utterance, returns text or None on failure."""
    ui_state.status = "listening..."
    with sr.Microphone() as source:
        logger.info("Adjusting for ambient noise...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        logger.info("Listening...")
        try:
            audio = recognizer.listen(source)
            logger.info("Processing speech...")
            from eva.config import STT_ENGINE
            
            if STT_ENGINE == "google":
                text = recognizer.recognize_google(audio)
            else:
                text = recognizer.recognize_google(audio)
                
            text = fix_typos(text)
            logger.debug(f"User said: {text}")
            ui_state.status = "thinking..."
            return text
        except sr.UnknownValueError:
            logger.warning("Could not understand audio.")
            ui_state.status = "idle"
            return None
        except sr.RequestError as e:
            logger.error(f"Could not request results from STT service: {e}")
            ui_state.status = "idle"
            return None
        except Exception as e:
            logger.error(f"Error during listening: {e}")
            ui_state.status = "idle"
            return None

def listen_with_timeout(timeout: int = 5) -> str | None:
    """Records one utterance with a timeout, returns text or None on failure."""
    ui_state.status = "listening..."
    with sr.Microphone() as source:
        logger.info("Adjusting for ambient noise...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        logger.info(f"Listening (timeout={timeout}s)...")
        try:
            audio = recognizer.listen(source, timeout=timeout)
            logger.info("Processing speech...")
            from eva.config import STT_ENGINE
            
            if STT_ENGINE == "google":
                text = recognizer.recognize_google(audio)
            else:
                text = recognizer.recognize_google(audio)
                
            text = fix_typos(text)
            logger.debug(f"User said: {text}")
            ui_state.status = "thinking..."
            return text
        except sr.WaitTimeoutError:
            logger.warning("Listening timed out.")
            ui_state.status = "idle"
            return None
        except sr.UnknownValueError:
            logger.warning("Could not understand audio.")
            ui_state.status = "idle"
            return None
        except sr.RequestError as e:
            logger.error(f"Could not request results from STT service: {e}")
            ui_state.status = "idle"
            return None
        except Exception as e:
            logger.error(f"Error during listening: {e}")
            ui_state.status = "idle"
            return None

if __name__ == "__main__":
    text = listen_once()
    if text:
        print(f"Heard: {text}")
