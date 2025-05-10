import requests
import openai
import time
import json
import os
import datetime
import re
from pathlib import Path

# ========== CONFIG ==========
SCRAPER_API_KEY = '57e9758e150311f9e07c9923e5731678'
OPENAI_API_KEY = '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'

NUM_PAGES = 2  # how many pages per site to fetch
SOURCES = {
    "Reddit": "https://www.reddit.com/search/?q={query}&page={page}",
    #"Quora": "https://www.quora.com/search?q={query}&page={page}",
    "ProductHunt": "https://www.producthunt.com/search?q={query}&page={page}",
    #"HackerNews": "https://hn.algolia.com/?q={query}&page={page}"
}
openai.api_key = OPENAI_API_KEY

# Base directory for logs
LOGS_DIR = Path("logs")

# ========== LOGGING SETUP ==========
def setup_log_directories(query):
    """
    Create the directory structure for logging
    
    Args:
        query (str): The business idea query
        
    Returns:
        dict: Dictionary containing paths to different log directories
    """
    # Sanitize query for use as directory name
    safe_query = re.sub(r'[^\w\s-]', '', query).strip().replace(' ', '_').lower()
    
    # Create timestamp for this run
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create base query directory
    query_dir = LOGS_DIR / safe_query / timestamp
    
    # Create subdirectories
    raw_dir = query_dir / "raw"
    analyzed_dir = query_dir / "analyzed"
    reports_dir = query_dir / "reports"
    
    # Create all directories
    for directory in [raw_dir, analyzed_dir, reports_dir]:
        directory.mkdir(parents=True, exist_ok=True)
    
    return {
        "query_dir": query_dir,
        "raw_dir": raw_dir,
        "analyzed_dir": analyzed_dir,
        "reports_dir": reports_dir,
        "timestamp": timestamp
    }

def save_to_file(content, file_path, is_json=False):
    """
    Save content to a file
    
    Args:
        content: The content to save
        file_path (Path): The path to save the file to
        is_json (bool): Whether the content is JSON and should be formatted
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            if is_json:
                json.dump(content, f, indent=2, ensure_ascii=False)
            else:
                f.write(content)
        print(f"Saved: {file_path}")
    except Exception as e:
        print(f"Error saving to {file_path}: {e}")

# ========== FETCHER ==========
def fetch_page(url, log_dirs=None, source_name=None, page_num=None):
    """
    Fetch a page from a URL and optionally log the raw content
    
    Args:
        url (str): The URL to fetch
        log_dirs (dict, optional): Log directory paths
        source_name (str, optional): Name of the source being fetched
        page_num (int, optional): Page number being fetched
        
    Returns:
        str: The page content or None if there was an error
    """
    params = {
        'api_key': SCRAPER_API_KEY,
        'url': url,
        'output_format': 'text'
    }
    
    response = requests.get('https://api.scraperapi.com/', params=params)
    
    if response.status_code == 200:
        content = response.text
        
        # Log raw content if logging is enabled
        if log_dirs and source_name and page_num is not None:
            file_name = f"{source_name}_page{page_num}.txt"
            file_path = log_dirs["raw_dir"] / file_name
            save_to_file(content, file_path)
            
        return content
    else:
        print(f"Error fetching {url}: {response.status_code}")
        return None

# ========== ANALYZER ==========
def analyze_text_with_openai(text, business_idea, log_dirs=None, source_name=None, page_num=None):
    """
    Analyze text using OpenAI and optionally log the results
    
    Args:
        text (str): The text to analyze
        business_idea (str): The business idea being researched
        log_dirs (dict, optional): Log directory paths
        source_name (str, optional): Name of the source being analyzed
        page_num (int, optional): Page number being analyzed
        
    Returns:
        dict: The analysis results
    """
    prompt = f"""
You are a business idea validator.  
Analyze the following text and find:

1. Pain points people mention
2. Excitement signals (desires, positive needs)
3. Competitors mentioned
4. Notable quotes (max 2 short quotes)

ONLY return a valid JSON like this:

{{
    "pain_points": [],
    "excitement_signals": [],
    "mentions_of_competitors": [],
    "notable_quotes": []
}}

Text to analyze:
{text}
"""

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        reply = response.choices[0].message.content
        result = json.loads(reply)
        
        # Log analyzed results if logging is enabled
        if log_dirs and source_name and page_num is not None:
            file_name = f"{source_name}_page{page_num}.json"
            file_path = log_dirs["analyzed_dir"] / file_name
            
            # Add metadata to the logged result
            log_result = {
                "metadata": {
                    "source": source_name,
                    "page": page_num,
                    "business_idea": business_idea,
                    "timestamp": datetime.datetime.now().isoformat()
                },
                "analysis": result
            }
            
            save_to_file(log_result, file_path, is_json=True)
            
        return result
    except Exception as e:
        print(f"Error during OpenAI analysis: {e}")
        return {
            "pain_points": [],
            "excitement_signals": [],
            "mentions_of_competitors": [],
            "notable_quotes": []
        }

# ========== MERGER ==========
def merge_results(all_results):
    """
    Merge multiple analysis results into a single report
    
    Args:
        all_results (list): List of analysis results to merge
        
    Returns:
        dict: The merged results
    """
    final = {
        "pain_points": [],
        "excitement_signals": [],
        "mentions_of_competitors": [],
        "notable_quotes": []
    }
    
    for res in all_results:
        final["pain_points"] += res.get("pain_points", [])
        final["excitement_signals"] += res.get("excitement_signals", [])
        final["mentions_of_competitors"] += res.get("mentions_of_competitors", [])
        final["notable_quotes"] += res.get("notable_quotes", [])
    
    # Deduplicate
    for key in final:
        final[key] = list(set(final[key]))
    
    return final

# ========== MAIN ==========
def main():
    """Main function to run the business idea validator"""
    idea = input("Enter your business idea keyword: ")
    
    # Set up logging directories
    log_dirs = setup_log_directories(idea)
    print(f"Logs will be saved to: {log_dirs['query_dir']}")
    
    # Save search metadata
    search_metadata = {
        "business_idea": idea,
        "timestamp": datetime.datetime.now().isoformat(),
        "sources": list(SOURCES.keys()),
        "pages_per_source": NUM_PAGES
    }
    metadata_path = log_dirs["query_dir"] / "search_metadata.json"
    save_to_file(search_metadata, metadata_path, is_json=True)
    
    all_page_results = []
    source_results = {}  # To track results by source

    for source_name, url_template in SOURCES.items():
        print(f"\nScraping {source_name}...")
        source_results[source_name] = []
        
        for page in range(1, NUM_PAGES + 1):
            url = url_template.format(query=idea.replace(' ', '+'), page=page)
            page_text = fetch_page(url, log_dirs, source_name, page)
            
            if page_text:
                print(f"Analyzing {source_name} page {page}...")
                page_result = analyze_text_with_openai(page_text, idea, log_dirs, source_name, page)
                all_page_results.append(page_result)
                source_results[source_name].append(page_result)
                time.sleep(1)  # be nice, avoid overloading OpenAI or ScraperAPI

    # Merge all results
    final_report = merge_results(all_page_results)
    
    # Save the final report as JSON
    final_report_with_metadata = {
        "metadata": {
            "business_idea": idea,
            "timestamp": datetime.datetime.now().isoformat(),
            "sources": list(SOURCES.keys()),
            "pages_per_source": NUM_PAGES
        },
        "results": final_report,
        "source_results": source_results
    }
    
    final_report_path = log_dirs["reports_dir"] / "final_report.json"
    save_to_file(final_report_with_metadata, final_report_path, is_json=True)
    print(f"Final report saved to: {final_report_path}")

    # ========== CONSOLE OUTPUT ==========
    print("\n=== Business Idea Validation Report ===\n")
    print(f"Pain Points:\n - " + "\n - ".join(final_report["pain_points"]))
    print(f"\nExcitement Signals:\n - " + "\n - ".join(final_report["excitement_signals"]))
    print(f"\nMentions of Competitors:\n - " + "\n - ".join(final_report["mentions_of_competitors"]))
    print(f"\nNotable Quotes:\n - " + "\n - ".join(final_report["notable_quotes"]))
    print(f"\nFull JSON report saved to: {final_report_path}")

if __name__ == "__main__":
    main()
