"""
Configuration for Phomemo PM-241-BT label printer
Wider canvas to fit larger text
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PRINTER_NAME = "PM-241-BT"
DPI = 300

# Wider to accommodate larger text
LABEL_WIDTH_PIXELS = 350   # Increased from 280
LABEL_HEIGHT_PIXELS = 380

DEFAULT_MARGINS_PIXELS = 10

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CLAUDE_MODEL = "claude-sonnet-4-5-20250929"

TEMP_IMAGE_DIR = Path("/tmp/label_images")
TEMP_IMAGE_DIR.mkdir(exist_ok=True)

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
