import sqlite3
import os
from pathlib import Path
from eva.config import MEMORY_DB_PATH
from eva.utils.logger import get_logger

logger = get_logger("EVA.memory.memory_store")

class MemoryStore:
    def __init__(self, db_path: str = MEMORY_DB_PATH):
        self.db_path = db_path
        self._init_db()
        self.initialize_user_memory()

    def _init_db(self):
        """Creates DB and tables if they don't exist."""
        path = Path(self.db_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS memories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        key TEXT UNIQUE NOT NULL,
                        value TEXT NOT NULL,
                        category TEXT DEFAULT 'general',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                ''')
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS reminders (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        text TEXT NOT NULL,
                        remind_at TEXT NOT NULL,
                        triggered INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                ''')
                conn.commit()
                logger.info("Memory database initialized.")
        except Exception as e:
            logger.error(f"Error initializing memory DB: {e}")

    def initialize_user_memory(self):
        """Preloads fixed personal memory data on startup."""
        if self.get_memory("name") == "Sarfraz":
            return
            
        initial_data = {
            "name": "Sarfraz",
            "full_name": "Mohd Sarfraz Saifi",
            "nickname": "Saif",
            "location": "Mussoorie, Uttarakhand, India",
            "education": "B.Tech CSE (AI & ML)",
            "university": "Lovely Professional University",
            "year": "1st year (almost completed)",
            "started_year": "2025",
            "skills_focus": "C++, DSA, AI/ML basics, Full stack development (learning phase)",
            "goals": "build a personal AI assistant (EVA), become strong in development + AI, create real-world projects, eventually launch EVA as a product, maintain 9+ cgpa",
            "preferences": "language: Hinglish, likes short responses, prefers practical learning over theory",
            "behavior_notes": "often experiments with systems, sometimes overthinks architecture, wants step-by-step structured guidance"
        }
        
        for k, v in initial_data.items():
            self.save_memory(k, v, category="user_profile")
        logger.info("Personal memory initialized.")

    def save_memory(self, key: str, value: str, category: str = "general") -> None:
        """Saves a key-value memory."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Insert or replace
                cursor.execute('''
                    INSERT INTO memories (key, value, category, updated_at) 
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(key) DO UPDATE SET 
                    value=excluded.value, 
                    category=excluded.category, 
                    updated_at=CURRENT_TIMESTAMP
                ''', (key.lower(), value, category))
                conn.commit()
                logger.info(f"Saved memory: {key} -> {value}")
        except Exception as e:
            logger.error(f"Error saving memory: {e}")

    def get_memory(self, key: str) -> str | None:
        """Retrieves memory by key."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT value FROM memories WHERE key = ?', (key.lower(),))
                row = cursor.fetchone()
                return row[0] if row else None
        except Exception as e:
            logger.error(f"Error getting memory '{key}': {e}")
            return None

    def get_all_by_category(self, category: str) -> list[dict]:
        """Returns all memories in a given category."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM memories WHERE category = ?', (category,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting category '{category}': {e}")
            return []

    def delete_memory(self, key: str) -> None:
        """Deletes a memory by key."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM memories WHERE key = ?', (key.lower(),))
                conn.commit()
                logger.info(f"Deleted memory: {key}")
        except Exception as e:
            logger.error(f"Error deleting memory '{key}': {e}")

    def save_reminder(self, text: str, remind_at: str) -> None:
        """Stores reminder with datetime string."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO reminders (text, remind_at) VALUES (?, ?)
                ''', (text, remind_at))
                conn.commit()
                logger.info(f"Saved reminder: '{text}' at {remind_at}")
        except Exception as e:
            logger.error(f"Error saving reminder: {e}")

    def get_pending_reminders(self) -> list[dict]:
        """Returns reminders not yet triggered."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM reminders WHERE triggered = 0")
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting pending reminders: {e}")
            return []

if __name__ == "__main__":
    store = MemoryStore("eva/memory/test.db")
    store.save_memory("name", "Arjun")
    print("Memory:", store.get_memory("name"))
    store.delete_memory("name")
