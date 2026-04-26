from eva.utils.logger import get_logger
from eva.utils.helpers import extract_keywords, get_affirmation
from eva.memory.memory_store import MemoryStore
from eva.planner.task_planner import TaskPlanner
from eva.brain.router import route_prompt

# Actions
from eva.actions.system_actions import open_application, smart_project_creation
from eva.actions.browser import search_google
from eva.actions.documents import create_srs_document
from eva.actions.messaging import send_whatsapp_message

logger = get_logger("EVA.orchestrator.core")

class Orchestrator:
    def __init__(self):
        self.memory = MemoryStore()
        self.planner = TaskPlanner()
        self.state = {} # Holds conversational context
        logger.info("Orchestrator initialized with all subsystems.")

    def detect_intent(self, text: str) -> dict:
        """Returns {'intent': '...', 'entities': [...]} using hybrid matching."""
        text_lower = text.lower().strip()
        
        # 1. FAST RULE-BASED MATCHING (Strict)
        if text_lower.startswith("create project") or text_lower.startswith("new project"):
            return {"intent": "create_project", "entities": []}
            
        if text_lower.startswith("open ") or text_lower.startswith("launch "):
            app = text_lower.replace("open ", "").replace("launch ", "").strip()
            return {"intent": "open_app", "entities": [app]}
            
        if text_lower.startswith("search for ") or text_lower.startswith("google "):
            query = text_lower.replace("search for ", "").replace("google ", "").strip()
            return {"intent": "search_web", "entities": [query]}
            
        if "show me" in text_lower or "preview" in text_lower:
            return {"intent": "preview_doc", "entities": []}
            
        # 2. LLM JSON PARSING FOR NATURAL LANGUAGE (Fallback)
        from eva.brain.local_llm import ask_local_json
        system_prompt = (
            "You are an intent parser. Map the user's Hinglish/English command to the correct JSON format. "
            "Possible intents: 'play_music', 'open_app', 'create_document', 'send_message', 'set_reminder', 'remember', 'recall', 'general_chat'. "
            "Examples:\n"
            "'gaana bajado' -> {\"intent\": \"play_music\", \"entities\": [\"youtube\"]}\n"
            "'play some arijit singh' -> {\"intent\": \"play_music\", \"entities\": [\"arijit singh\"]}\n"
            "'whatsapp kholo' -> {\"intent\": \"open_app\", \"entities\": [\"whatsapp\"]}\n"
            "'send message to Prince mother that he is playing' -> {\"intent\": \"send_message\", \"entities\": [\"Prince mother\", \"he is playing\"]}\n"
            "'remind me to study' -> {\"intent\": \"set_reminder\", \"entities\": [\"study\"]}\n"
            "Respond ONLY with raw valid JSON."
        )
        
        try:
            logger.info("Using LLM for complex intent parsing...")
            result = ask_local_json(text, system_prompt=system_prompt)
            # Validate output
            if not isinstance(result, dict) or "intent" not in result:
                return {"intent": "general_chat", "entities": [text]}
            if "entities" not in result or not isinstance(result["entities"], list):
                result["entities"] = [text]
            return result
        except Exception as e:
            logger.error(f"LLM intent parsing failed: {e}")
            return {"intent": "general_chat", "entities": [text]}

    def extract_passive_memory(self, text: str):
        """Passively extracts and saves important structured events from general chat."""
        text_lower = text.lower()
        # Look for dates and tasks/exams
        time_kws = ["kal", "tomorrow", "aaj", "today", "parso"]
        task_kws = ["exam", "ca", "test", "assignment", "meeting", "class"]
        
        has_time = any(kw in text_lower for kw in time_kws)
        has_task = any(kw in text_lower for kw in task_kws)
        
        if has_time and has_task:
            self.memory.save_reminder(text, "soon")
            logger.info("Saved passive event to memory.")

    def handle_conversational_state(self, user_input: str) -> str:
        """Handles ongoing multi-step dialogues."""
        intent = self.state.get("intent")
        
        if intent == "create_document":
            if not self.state.get("topic"):
                self.state["topic"] = user_input
                return f"Got it. What kind of assignment/document is {user_input}? (e.g., SRS, report, essay)"
            elif not self.state.get("doc_type"):
                self.state["doc_type"] = user_input
                return "And roughly how many pages do you want it to be?"
            elif not self.state.get("pages"):
                self.state["pages"] = user_input
                # Execute
                topic = self.state["topic"]
                doc_type = self.state["doc_type"]
                pages = self.state["pages"]
                self.state = {} # Clear state
                
                if "srs" in doc_type.lower():
                    from eva.brain.local_llm import ask_local
                    logger.info("Generating long SRS content using local LLM...")
                    
                    # Generate real content instead of short stubs
                    system_prompt = "You are a senior technical writer. Write extremely detailed and lengthy professional documents."
                    prompt = f"Write a massive, highly detailed {pages}-page Software Requirements Specification for '{topic}'. Include extremely long paragraphs for Introduction, Scope, and Functional Requirements."
                    srs_text = ask_local(prompt, system_prompt=system_prompt)
                    
                    # Safely split generated content into sections
                    intro = srs_text[:2500] if len(srs_text) > 2500 else srs_text
                    scope = srs_text[2500:5000] if len(srs_text) > 2500 else "The project scope encompasses all features listed below."
                    reqs = [req for req in srs_text[5000:].split('\n') if req.strip()] if len(srs_text) > 5000 else ["User Authentication", "Database Management", "API Integration", "UI/UX Design", "Testing"]
                    
                    content = {
                        "introduction": intro,
                        "scope": scope,
                        "functional": reqs[:15],
                        "non_functional": ["High Performance Requirement", "Robust Security Policy", "Scalability Protocols", "High Availability"],
                        "architecture": "A highly scalable cloud-native microservices architecture."
                    }
                    path = create_srs_document(topic, content, preview=True)
                    return f"{get_affirmation()} {pages}-page SRS document ban gaya aur PDF bhi. Maine usko aapke screen par open kar diya hai!"
                else:
                    return f"{get_affirmation()} I can help you structure the {doc_type} for {topic} soon!"
                    
        elif intent == "create_project":
            if not self.state.get("project_name"):
                self.state["project_name"] = user_input
                name = user_input
                self.state = {}
                return smart_project_creation(name)
                
        self.state = {}
        return "Task cancelled."

    def process(self, user_input: str) -> str:
        """Main dispatch method."""
        if not user_input or not user_input.strip():
            return ""
            
        logger.info(f"Processing input: {user_input}")
        
        # Check if we are in an active conversation state
        if self.state.get("intent"):
            return self.handle_conversational_state(user_input)
        
        # Detect Intent
        intent_data = self.detect_intent(user_input)
        intent = intent_data["intent"]
        entities = intent_data["entities"]
        
        logger.info(f"Detected intent: {intent}")
        
        try:
            if intent == "create_project":
                self.state["intent"] = "create_project"
                return "Kya naam rakhna hai project ka?"
                
            elif intent == "open_app":
                if entities:
                    app = str(entities[0]).lower()
                    if "chatgpt" in app or "chat gpt" in app:
                        from eva.actions.browser import navigate_to
                        navigate_to("https://chatgpt.com")
                        return f"{get_affirmation()} ChatGPT khol diya aapke main browser mein!"
                    elif "youtube" in app:
                        from eva.actions.browser import navigate_to
                        navigate_to("https://youtube.com")
                        return f"{get_affirmation()} YouTube khol diya aapke main browser mein!"
                    elif "github" in app:
                        from eva.actions.browser import navigate_to
                        navigate_to("https://github.com")
                        return f"{get_affirmation()} GitHub khol diya!"
                    elif "whatsapp" in app:
                        from eva.actions.browser import navigate_to
                        navigate_to("https://web.whatsapp.com")
                        return f"{get_affirmation()} WhatsApp Web khol diya!"
                        
                    return open_application(app)
                else:
                    return "Kaunsi app kholu?"
                    
            elif intent == "play_music":
                from eva.actions.browser import navigate_to
                if entities and entities[0] and entities[0] != "youtube":
                    query = str(entities[0]).replace(" ", "+")
                    navigate_to(f"https://www.youtube.com/results?search_query={query}")
                    return f"{get_affirmation()} Playing {entities[0]} on YouTube."
                else:
                    navigate_to("https://music.youtube.com")
                    return f"{get_affirmation()} YouTube Music khol diya."
                    
            elif intent == "search_web":
                if entities:
                    return search_google(entities[0])
                else:
                    return "Kya search karu?"
                    
            elif intent == "create_document":
                # Start multi-step dialog
                self.state["intent"] = "create_document"
                return "What kind of portfolio or assignment do you want to build?"
                
            elif intent == "send_message":
                if entities and len(entities) >= 2:
                    contact = str(entities[0])
                    message = str(entities[1])
                    return send_whatsapp_message(contact, message)
                elif entities and len(entities) == 1:
                    # Fallback if LLM didn't split them perfectly
                    text = str(entities[0]).lower()
                    if "to " in text and " that " in text:
                        parts = text.split("to ", 1)[1]
                        contact, message = parts.split(" that ", 1)
                        return send_whatsapp_message(contact.strip(), message.strip())
                return "Message ka format samajh nahi aaya. Aise bole: 'Send message to [Name] that [Message]'"
                
            elif intent == "remember":
                text = entities[0]
                if "is " in text:
                    key, value = text.split("is ", 1)
                    key = key.replace("remember that", "").replace("remember my", "").strip()
                    self.memory.save_memory(key, value.strip())
                    return f"{get_affirmation()} I will remember {key} is {value.strip()}"
                else:
                    self.memory.save_memory("note", text)
                    return f"{get_affirmation()} Saved!"
                    
            elif intent == "recall":
                text = entities[0]
                if "what's my " in text:
                    key = text.split("what's my ")[1].strip("? ")
                elif "whats my " in text:
                    key = text.split("whats my ")[1].strip("? ")
                else:
                    key = extract_keywords(text)[0] if extract_keywords(text) else "note"
                    
                val = self.memory.get_memory(key)
                if val:
                    return f"It is: {val}"
                else:
                    return f"I don't remember anything about {key}."
                    
            elif intent == "set_reminder":
                self.memory.save_reminder(text, "soon")
                return f"{get_affirmation()} Reminder set!"
                
            elif intent == "preview_doc":
                return "You can say 'show me' right after generating a document to open it."
                
            elif intent == "general_chat":
                # Extract any structured context like exams before chatting
                self.extract_passive_memory(user_input)
                return route_prompt(user_input)
                
        except Exception as e:
            logger.error(f"Error handling intent {intent}: {e}")
            return f"Oops, error aaya. {e}"
            
        return "Samajh nahi aaya, thoda clear kahoge?"
