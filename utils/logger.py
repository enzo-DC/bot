"""
Configuration du système de logging
"""
import logging
import sys
from pathlib import Path
from colorlog import ColoredFormatter

def setup_logger(name: str = "telegram_bot", log_level: str = "INFO") -> logging.Logger:
    """
    Configure un logger avec couleurs et formatage propre
    
    Args:
        name: Nom du logger
        log_level: Niveau de log
        
    Returns:
        Logger configuré
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    if logger.handlers:
        return logger
    
    # Handler console avec couleurs
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    
    # Format avec couleurs
    console_formatter = ColoredFormatter(
        "%(log_color)s%(asctime)s - %(levelname)s%(reset)s - %(message)s",
        datefmt="%H:%M:%S",
        log_colors={'DEBUG': 'cyan', 'INFO': 'green', 'WARNING': 'yellow', 'ERROR': 'red'}
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Handler fichier (logs/)
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    file_handler = logging.FileHandler(log_dir / "bot.log", encoding="utf-8")
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(file_handler)
    
    return logger

logger = setup_logger()