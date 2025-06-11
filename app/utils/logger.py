import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Create logs directory if it doesn't exist
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE_PATH = LOG_DIR / "app.log"

# Define formatter
formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] [%(name)s] [%(filename)s:%(lineno)d] - %(message)s"
)

# File handler with rotation (5MB per file, keep last 5)
file_handler = RotatingFileHandler(LOG_FILE_PATH, maxBytes=5_000_000, backupCount=5)
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)

# Console handler (for dev/debugging)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.DEBUG)

# Create root logger
logger = logging.getLogger("trackify")
logger.setLevel(logging.DEBUG)

# Avoid duplicate logs
if not logger.hasHandlers():
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
