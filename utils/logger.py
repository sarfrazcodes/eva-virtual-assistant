import logging
from pathlib import Path
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

class ColoredFormatter(logging.Formatter):
    """Custom formatter with color support for console output."""
    COLORS = {
        'DEBUG': Fore.BLUE,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.MAGENTA + Style.BRIGHT
    }

    def format(self, record):
        log_fmt = f"[{Fore.CYAN}%(asctime)s{Style.RESET_ALL}] [{Fore.MAGENTA}%(name)s{Style.RESET_ALL}] %(levelname)s: %(message)s"
        color = self.COLORS.get(record.levelname, '')
        log_fmt = log_fmt.replace('%(levelname)s', f"{color}%(levelname)s{Style.RESET_ALL}")
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)

def get_logger(name: str) -> logging.Logger:
    """Returns a configured logger with file and console handlers."""
    from eva.config import LOG_LEVEL, LOG_FILE
    
    logger = logging.getLogger(name)
    
    # Prevent adding handlers multiple times
    if logger.hasHandlers():
        return logger
        
    logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))
    
    # Ensure logs path exists
    log_path = Path(LOG_FILE)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # File Handler
    file_fmt = logging.Formatter(
        "[{asctime}] [{name}] {levelname}: {message}", 
        style='{', 
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler = logging.FileHandler(str(log_path), encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_fmt)
    
    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))
    console_handler.setFormatter(ColoredFormatter())
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Disable propagation to avoid double logging
    logger.propagate = False
    
    return logger
