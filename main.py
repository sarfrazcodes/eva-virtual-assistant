import sys
import time
import threading
from eva.utils.logger import get_logger
from eva.voice.listener import listen_once, recognizer
from eva.voice.speaker import speak
from eva.orchestrator.core import Orchestrator
from eva.utils.ui import start_ui_thread, ui_state
import speech_recognition as sr

logger = get_logger("EVA.main")

shutdown_event = threading.Event()
wake_event = threading.Event()

def hotkey_listener():
    """Listens for Ctrl+Shift+X to safely shutdown without relying solely on 'keyboard'."""
    try:
        import keyboard
        def on_exit():
            if not shutdown_event.is_set():
                logger.warning("Safe Stop Triggered via Hotkey! Attempting graceful shutdown...")
                shutdown_event.set()
                
                # Force exit after 1 second if graceful shutdown gets stuck on microphone
                def force_kill():
                    import time, os
                    time.sleep(1.5)
                    os._exit(0)
                threading.Thread(target=force_kill, daemon=True).start()
                
        keyboard.add_hotkey('ctrl+shift+x', on_exit)
        # Keep thread alive to listen
        keyboard.wait('ctrl+shift+x')
    except ImportError:
        logger.warning("Keyboard module not installed. Hotkey stop unavailable. Use Ctrl+C.")

def background_audio_callback(recognizer_instance, audio):
    """Callback for background listener."""
    if shutdown_event.is_set():
        return
    try:
        from eva.config import STT_ENGINE
        if STT_ENGINE == "google":
            text = recognizer_instance.recognize_google(audio).lower()
        else:
            text = recognizer_instance.recognize_google(audio).lower()
            
        if "wake up" in text or "eva" in text or "wake" in text:
            logger.info("Wake word detected!")
            wake_event.set()
    except sr.UnknownValueError:
        pass
    except Exception as e:
        logger.error(f"Background listen error: {e}")

def main():
    logger.info("Booting EVA Assistant...")
    
    # 1. Start UI
    start_ui_thread()
    
    # 2. Login Security
    print("\n" + "="*50)
    ui_state.status = "waiting for passcode..."
    passcode = input("Enter System Passcode: ").strip()
    if passcode != "753383":
        logger.critical("Access Denied. Incorrect Passcode.")
        sys.exit(1)
        
    ui_state.status = "initializing system..."
    
    # 3. Init Hotkey
    hotkey_thread = threading.Thread(target=hotkey_listener, daemon=True)
    hotkey_thread.start()
    
    try:
        orchestrator = Orchestrator()
    except Exception as e:
        logger.critical(f"Failed to initialize orchestrator: {e}")
        sys.exit(1)
        
    speak("Namaste! EVA system is now online. I am ready.")
    
    # Start Background Listener
    mic = sr.Microphone()
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
    stop_listening = recognizer.listen_in_background(mic, background_audio_callback)
    
    logger.info("Background listening active. Say 'wake up' to wake.")
    ui_state.status = "idle"
    
    # Auto-trigger first interaction immediately upon boot
    wake_event.set()
    
    while not shutdown_event.is_set():
        try:
            # Wait for wake word or keyboard interrupt
            while not wake_event.is_set() and not shutdown_event.is_set():
                time.sleep(0.5)
                
            if shutdown_event.is_set():
                break
                
            wake_event.clear()
            speak("Yes?") # Greet on initial wake
            
            # Start continuous listening session
            session_active = True
            
            while session_active and not shutdown_event.is_set():
                ui_state.status = "listening..."
                print("\n" + "="*50)
                
                user_input = listen_once()
                
                if not user_input:
                    speak("Can you repeat please?")
                    ui_state.status = "listening..."
                    user_input = listen_once()
                    
                    if not user_input:
                        speak("I couldn't hear anything. Going back to sleep.")
                        session_active = False
                        ui_state.status = "idle"
                        break
                
                user_input_lower = user_input.lower()
                if "go sleep" in user_input_lower or "sleep" in user_input_lower or "stop listening" in user_input_lower:
                    speak("Okay, sleeping now. Just say wake up if you need me.")
                    session_active = False
                    ui_state.status = "idle"
                    break
                
                response = orchestrator.process(user_input)
                speak(response)
                # The loop continues immediately to listen again
            
        except KeyboardInterrupt:
            print("\n")
            try:
                choice = input("Type command (t) or exit (e)? [t/e]: ").strip().lower()
                if choice == 'e' or choice == 'exit':
                    speak("Shutting down. See you later!")
                    shutdown_event.set()
                elif choice == 't':
                    user_input = input("Enter command: ").strip()
                    if user_input:
                        response = orchestrator.process(user_input)
                        speak(response)
                        ui_state.status = "idle"
            except KeyboardInterrupt:
                speak("Shutting down. See you later!")
                shutdown_event.set()
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            speak("Sorry, there was an error in the system.")
            ui_state.status = "idle"
            
    # Cleanup
    stop_listening(wait_for_stop=False)
    ui_state.is_active = False

if __name__ == "__main__":
    main()
