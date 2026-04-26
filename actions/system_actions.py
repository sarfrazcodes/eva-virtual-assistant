import subprocess
import os
import psutil
from pathlib import Path
from eva.utils.logger import get_logger
from eva.utils.helpers import get_affirmation
from eva.utils.logger import get_logger

logger = get_logger("EVA.actions.system")

APP_MAP = {
    "chrome": "C:/Program Files/Google/Chrome/Application/chrome.exe",
    "vscode": f"C:/Users/{os.getenv('USERNAME')}/AppData/Local/Programs/Microsoft VS Code/Code.exe",
    "notepad": "notepad.exe",
    "explorer": "explorer.exe",
    "terminal": "wt.exe",
}

def open_application(app_name: str) -> str:
    """Opens an application using subprocess."""
    app_name = app_name.lower().strip()
    
    # Try finding in map
    for key, path in APP_MAP.items():
        if key in app_name:
            try:
                subprocess.Popen(path, shell=True)
                logger.info(f"Opened {key} via map path.")
                return f"{key.title()} opened!"
            except Exception as e:
                logger.error(f"Failed to open {key}: {e}")
                
    # Fallback to direct call
    try:
        # Try using windows start which searches PATH and known apps
        os.system(f'start "" "{app_name}"')
        return f"Trying to open {app_name}."
    except Exception as e:
        return f"{app_name} open nahi hua. Error: {e}"

def smart_project_creation(project_name: str) -> str:
    """Creates a basic HTML/CSS project folder on desktop and opens VS Code."""
    try:
        profile = Path(os.environ['USERPROFILE'])
        desktop = profile / 'OneDrive' / 'Desktop'
        if not desktop.exists():
            desktop = profile / 'Desktop'
            
        project_path = desktop / project_name
        project_path.mkdir(parents=True, exist_ok=True)
        
        # Create basic files
        with open(project_path / 'index.html', 'w') as f:
            f.write("<!DOCTYPE html>\n<html>\n<head><title>New Project</title><link rel='stylesheet' href='style.css'></head>\n<body><h1>Hello World</h1></body>\n</html>")
        with open(project_path / 'style.css', 'w') as f:
            f.write("body { font-family: Arial, sans-serif; background: #f0f0f0; }")
            
        # Open in VS Code
        subprocess.Popen(f'code "{project_path}"', shell=True)
        return f"{get_affirmation()} {project_name} project is ready and opened in VS Code!"
    except Exception as e:
        logger.error(f"Smart project creation failed: {e}")
        return "Project banate waqt error aaya."

def run_command(command: str) -> tuple[str, str]:
    """Runs shell command, returns (stdout, stderr)."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        logger.error(f"Error running command: {e}")
        return "", str(e)

def create_file(filepath: str, content: str = "") -> str:
    """Creates file with optional content."""
    try:
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"File {path.name} create ho gayi."
    except Exception as e:
        logger.error(f"File create error: {e}")
        return f"File banate waqt error aaya: {e}"

def create_folder(folderpath: str) -> str:
    """Creates directory recursively."""
    try:
        path = Path(folderpath)
        path.mkdir(parents=True, exist_ok=True)
        return f"Folder {path.name} ban gaya."
    except Exception as e:
        logger.error(f"Folder create error: {e}")
        return f"Folder banate waqt error: {e}"

def list_files(directory: str) -> list[str]:
    """Lists files in a directory."""
    try:
        path = Path(directory)
        if not path.is_dir():
            return []
        return [f.name for f in path.iterdir() if f.is_file()]
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        return []

def get_system_info() -> dict:
    """Returns CPU, RAM, disk usage using psutil."""
    try:
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        return {
            "cpu_usage": cpu,
            "ram_usage": ram,
            "disk_usage": disk
        }
    except Exception as e:
        logger.error(f"System info error: {e}")
        return {}
