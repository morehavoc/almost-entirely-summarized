import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL = "claude-3-opus-20240229"  # or other available Claude models

# Blog Processing Configuration
MAX_POSTS_IN_SUMMARY = 20
OUTPUT_FORMAT = "markdown"  # markdown or html
DATE_RANGE_FILTER_ENABLED = False
START_DATE = "2025-01-01"
END_DATE = None  # None means today

# Storage Configuration
DATA_DIR = "data"
OUTPUT_DIR = "output"
URL_FILE = os.path.join(DATA_DIR, "urls.txt")
STORAGE_FILE = os.path.join(DATA_DIR, "blog_data.json")

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
