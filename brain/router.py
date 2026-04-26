from eva.config import EVA_MODE, ASK_BEFORE_ONLINE
from eva.brain.local_llm import ask_local
from eva.brain.online_llm import ask_openai, ask_gemini
from eva.utils.logger import get_logger
from eva.utils.helpers import confirm
from eva.voice.speaker import speak

logger = get_logger("EVA.brain.router")

def classify_complexity(prompt: str) -> str:
    """Returns 'simple' | 'complex' based on prompt length and keywords."""
    complex_keywords = ["write a script", "summarize this long text", "explain in detail", "analyze", "code", "architecture"]
    
    if len(prompt.split()) > 30:
        return "complex"
        
    prompt_lower = prompt.lower()
    for kw in complex_keywords:
        if kw in prompt_lower:
            return "complex"
            
    return "simple"

def ask_permission_to_go_online() -> bool:
    """Prints/speaks a permission request, waits for yes/no input."""
    msg = "Yaar, iske liye internet chahiye. Use karoon?"
    speak(msg)
    return confirm("Use internet?")

def route_prompt(prompt: str, task_type: str = "general") -> str:
    """Decides whether to use local or online LLM based on task complexity and current mode."""
    system_prompt = (
        "You are EVA, a smart, friendly, slightly playful female personal AI assistant for Sarfraz. "
        "STRICT RULES: You MUST ALWAYS act as a female. Never use masculine words like 'bhai' or 'bro'. "
        "Keep responses EXACTLY 1-2 lines maximum. DO NOT over-explain. DO NOT break words into individual letters. "
        "Use short Hinglish + English responses. Keep it natural. "
        "Allowed examples: 'done Sarfraz', 'all set', 'ready hai, check kar lo'. "
        "If the user is sad, respond softly."
    )
    
    if EVA_MODE == "offline":
        logger.info("Routing to offline LLM (Mode: offline)")
        return ask_local(prompt, system_prompt)
        
    elif EVA_MODE == "hybrid":
        complexity = classify_complexity(prompt)
        logger.info(f"Hybrid Mode: Detected complexity '{complexity}'")
        
        if complexity == "simple":
            return ask_local(prompt, system_prompt)
        else:
            if ASK_BEFORE_ONLINE:
                if not ask_permission_to_go_online():
                    # Fallback to local if denied
                    return ask_local(prompt, system_prompt)
            # Proceed online
            try:
                return ask_openai(prompt, system_prompt)
            except ValueError:
                return "API key missing for online LLM."
                
    elif EVA_MODE == "online":
        logger.info("Routing to online LLM (Mode: online)")
        try:
            return ask_openai(prompt, system_prompt)
        except ValueError:
            return "API key missing for online LLM."
            
    return "Invalid EVA_MODE configuration."

if __name__ == "__main__":
    print(route_prompt("Translate 'Hello' to French."))
