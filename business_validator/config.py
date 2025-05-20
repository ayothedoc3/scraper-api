"""
Configuration settings for the business validator package.
"""

import os

# API Keys
SCRAPERAPI_KEY = "57e9758e150311f9e07c9923e5731678"  # Replace with your ScraperAPI key

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
