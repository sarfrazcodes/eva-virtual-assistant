import tkinter as tk
import threading
from eva.utils.logger import get_logger

logger = get_logger("EVA.utils.ui")

class UIState:
    """Shared state to communicate between backend and UI without blocking."""
    def __init__(self):
        self.status = "INITIALIZING..."
        self.is_active = True
        
ui_state = UIState()

class FloatingBotUI:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(True) # Borderless
        self.root.attributes("-topmost", True)
        
        # Position bottom right
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        self.root.geometry(f"250x95+{screen_width-270}+{screen_height-170}")
        self.root.configure(bg='#020617') # Very dark blue
        self.root.attributes('-alpha', 0.95)
        
        # Make it draggable
        self.root.bind("<ButtonPress-1>", self.start_move)
        self.root.bind("<ButtonRelease-1>", self.stop_move)
        self.root.bind("<B1-Motion>", self.do_move)
        
        # Outer Glowing Frame Simulation
        self.frame = tk.Frame(self.root, bg="#1E293B", bd=2, relief="flat")
        self.frame.pack(fill="both", expand=True, padx=4, pady=4)
        
        # Inner Frame
        self.inner = tk.Frame(self.frame, bg="#0F172A")
        self.inner.pack(fill="both", expand=True)
        
        # UI Elements
        self.robot_face = tk.Label(self.inner, text="✨ E V A ✨", fg="#38BDF8", bg="#0F172A", font=("Segoe UI", 15, "bold"))
        self.robot_face.pack(pady=(12,2))
        
        self.status_label = tk.Label(self.inner, text="● SLEEPING", fg="#94A3B8", bg="#0F172A", font=("Segoe UI", 9, "bold"))
        self.status_label.pack(pady=(0,10))
        
        self.x = 0
        self.y = 0
        
        # Periodic UI update
        self.update_ui()

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = None
        self.y = None

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")
        
    def update_ui(self):
        if not ui_state.is_active:
            self.root.destroy()
            return
            
        current = str(ui_state.status).lower()
        
        # Dynamic Status styling logic
        if "listen" in current:
            self.status_label.config(text="🎙️ LISTENING...", fg="#34D399") # Green
            self.frame.config(bg="#10B981") # Green Glow border
        elif "think" in current:
            self.status_label.config(text="⚙️ THINKING...", fg="#FBBF24") # Yellow
            self.frame.config(bg="#F59E0B")
        elif "speak" in current:
            self.status_label.config(text="💬 SPEAKING...", fg="#F472B6") # Pink
            self.frame.config(bg="#EC4899")
        elif "idle" in current:
            self.status_label.config(text="💤 SLEEPING (SAY WAKE UP)", fg="#94A3B8")
            self.frame.config(bg="#334155")
        else:
            self.status_label.config(text=current.upper(), fg="#38BDF8")
            self.frame.config(bg="#0EA5E9")
            
        self.root.after(200, self.update_ui)

def run_ui():
    try:
        root = tk.Tk()
        app = FloatingBotUI(root)
        root.mainloop()
    except Exception as e:
        logger.error(f"UI failed: {e}")

def start_ui_thread():
    t = threading.Thread(target=run_ui, daemon=True)
    t.start()
    return t
