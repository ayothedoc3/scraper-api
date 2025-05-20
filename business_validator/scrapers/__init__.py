"""
Scraper modules for fetching data from various platforms.
"""

from business_validator.scrapers.hackernews import scrape_hackernews, parse_hn_markdown
from business_validator.scrapers.reddit import (
    scrape_reddit_search, 
    parse_reddit_search_markdown,
    scrape_reddit_post_comments,
    parse_reddit_comments_markdown
)

__all__ = [
    'scrape_hackernews',
    'parse_hn_markdown',
    'scrape_reddit_search',
    'parse_reddit_search_markdown',
    'scrape_reddit_post_comments',
    'parse_reddit_comments_markdown'
]
