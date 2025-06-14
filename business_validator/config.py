"""
Configuration settings for the business validator package.
"""

import os

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# API Keys
SCRAPERAPI_KEY = os.getenv("SCRAPERAPI_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def validate_api_keys():
    """Validate that required API keys are set."""
    if not SCRAPERAPI_KEY:
        raise ValueError("SCRAPERAPI_KEY environment variable not set")
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY environment variable not set")

# HackerNews Configuration
MAX_PAGES_PER_KEYWORD_HN = 3  # Number of pages to scrape per keyword on HN
HN_DELAY = 1  # Seconds to wait between HN requests

# Reddit Configuration  
MAX_PAGES_PER_KEYWORD_REDDIT = 3  # Number of pages to scrape per keyword on Reddit
MAX_POSTS_TO_ANALYZE = 20  # Maximum posts to scrape comments for per keyword
MAX_COMMENTS_PER_POST = 10  # Maximum top comments to analyze per post
REDDIT_DELAY = 2  # Seconds to wait between Reddit requests (longer due to more complexity)

# Logging and Checkpoint Configuration
DATA_DIR = "validation_data"
LOG_DIR = "logs"
CHECKPOINT_INTERVAL = 5  # Save checkpoints every N items when processing lists
