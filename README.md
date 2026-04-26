# EVA (Evolving Virtual Assistant) - V5 🚀

![EVA Virtual Assistant](https://img.shields.io/badge/Status-Active-brightgreen.svg) ![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg) ![AI Engine](https://img.shields.io/badge/AI-Ollama%20%7C%20OpenAI-purple.svg)

EVA is a highly advanced, persistent, and autonomous AI Virtual Assistant capable of executing complex natural language commands, automating browser tasks, generating documents, and managing conversational states using a cutting-edge Hybrid LLM Architecture.

## ✨ Core Features

*   **Hybrid AI Intent Engine:** Dynamically routes fast rule-based commands for zero-latency execution, while falling back to a structured JSON-based LLM parser (Local Ollama or Online OpenAI) for highly complex natural language requests.
*   **Persistent Browser Automation:** Built on top of Playwright, EVA operates using a persistent Chrome profile. This means she remembers all your logged-in accounts (Google, WhatsApp Web, YouTube) across reboots, providing a truly seamless daily-use experience.
*   **Autonomous Task Execution:**
    *   🎵 **Music & Media:** Instantly scrapes and auto-plays specific songs on YouTube using direct Video ID extraction.
    *   💬 **Smart Messaging:** Analyzes complex requests (e.g., *"Send a message to Mom that I am busy"*) to automatically locate the contact, draft the text on WhatsApp Web, and ask for voice confirmation before sending.
    *   📝 **Document Generation:** Employs advanced Prompt Engineering to dynamically generate extensive Software Requirements Specifications (SRS), saving them as both `.docx` and `.pdf` directly to your desktop.
*   **Persistent SQLite Memory:** EVA remembers context, facts, and user preferences across sessions using an embedded SQLite database.
*   **Voice Interactivity:** Features advanced Ambient Noise adjustment, Speech-to-Text (STT) processing, and a highly stable Hinglish/English Text-to-Speech (TTS) engine with word-merging sanitation logic for flawless pronunciation.
*   **Safe Shutdown Architecture:** Includes background non-blocking hotkey listeners (`Ctrl+Shift+X`) for instant, graceful shutdowns.

## 🧠 System Architecture

EVA is structured modularly to allow endless scalability:

*   `/actions/` - Core automation handlers (Browser, Documents, Messaging).
*   `/brain/` - The Intelligence Layer (Local vs. Online LLM Routing, JSON parsing).
*   `/memory/` - SQLite Persistent Store logic.
*   `/orchestrator/` - The Central Nervous System managing Intents and Conversational State.
*   `/voice/` - Asynchronous TTS/STT I/O.

## 🛠️ Setup & Installation

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/sarfrazcodes/eva-virtual-assistant.git
    cd eva-virtual-assistant
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    playwright install chromium
    ```

3.  **Environment Variables**
    Create a `.env` file in the root directory:
    ```env
    OPENAI_API_KEY=your_openai_api_key
    GEMINI_API_KEY=your_gemini_api_key
    ```

4.  **Configuration (`config.py`)**
    You can freely toggle `EVA_MODE` between `"offline"` (Ollama) and `"online"` (OpenAI) depending on your speed/privacy needs.

## 🚀 Running EVA

Simply run the main module from the root directory:

```bash
python -m main
```
*Note: A system passcode is required on boot for authorization.*

## 🤝 Contribution

This repository uses atomic, conventional commits. Feel free to fork, optimize the state tree, or expand the task planner!
