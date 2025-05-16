import requests
import openai
import time
import json
import os
import datetime
import re
from pathlib import Path
import math

# ========== CONFIG ==========
SCRAPER_API_KEY = '57e9758e150311f9e07c9923e5731678'
OPENAI_API_KEY = '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'

# Scoring weights
SCORE_WEIGHTS = {
    "pain_points": 0.35,      # 35% weight for pain points
    "excitement_signals": 0.30, # 30% weight for excitement signals
    "competitors": 0.20,      # 20% weight for competitors
    "keyword_relevance": 0.15  # 15% weight for keyword relevance
}

NUM_PAGES = 2  # how many pages per site to fetch
NUM_KEYWORDS = 5  # number of keywords to generate
SOURCES = {
    "Reddit": "https://www.reddit.com/search/?q={query}&page={page}",
    #"Quora": "https://www.quora.com/search?q={query}&page={page}",
    "ProductHunt": "https://www.producthunt.com/search?q={query}&page={page}",
    #"HackerNews": "https://hn.algolia.com/?q={query}&page={page}"
}
openai.api_key = OPENAI_API_KEY

# Base directory for logs
LOGS_DIR = Path("logs")

# ========== KEYWORD GENERATION ==========
def generate_keywords(business_idea, num_keywords=NUM_KEYWORDS):
    """
    Generate relevant keywords for a business idea using OpenAI
    
    Args:
        business_idea (str): The main business idea
        num_keywords (int): Number of keywords to generate
        
    Returns:
        list: List of generated keywords
    """
    print(f"Generating {num_keywords} keywords for: {business_idea}")
    
    prompt = f"""
For the business idea: "{business_idea}"

Generate {num_keywords} specific search keywords that would help validate this idea.
These should be phrases people might use when discussing pain points, needs, or solutions related to this idea.

ONLY return a valid JSON object with a 'keywords' array like this:
{{
    "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"]
}}
"""
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        reply = response.choices[0].message.content
        result = json.loads(reply)
        keywords = result.get("keywords", [])
        
        # Always include the original business idea as a keyword
        if business_idea not in keywords:
            keywords.append(business_idea)
            
        return keywords
    except Exception as e:
        print(f"Error generating keywords: {e}")
        # Return the original business idea as a fallback
        return [business_idea]

# ========== LOGGING SETUP ==========
def setup_master_log_directory(business_idea):
    """
    Create master directory for all keyword results
    
    Args:
        business_idea (str): The main business idea
        
    Returns:
        Path: Path to the master log directory
    """
    # Sanitize business idea for use as directory name
    safe_idea = re.sub(r'[^\w\s-]', '', business_idea).strip().replace(' ', '_').lower()
    
    # Truncate long names to a reasonable length (e.g., 30 characters)
    if len(safe_idea) > 30:
        safe_idea = safe_idea[:30]
    
    # Create timestamp for this run
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create master directory
    master_dir = LOGS_DIR / safe_idea / timestamp
    master_dir.mkdir(parents=True, exist_ok=True)
    
    return master_dir

def setup_keyword_log_directories(keyword, master_log_dir):
    """
    Set up log directories for a specific keyword
    
    Args:
        keyword (str): The keyword
        master_log_dir (Path): Path to the master log directory
        
    Returns:
        dict: Dictionary containing paths to different log directories
    """
    # Sanitize keyword for use as directory name
    safe_keyword = re.sub(r'[^\w\s-]', '', keyword).strip().replace(' ', '_').lower()
    
    # Truncate long keywords to a reasonable length
    if len(safe_keyword) > 30:
        safe_keyword = safe_keyword[:30]
    
    # Create keyword directory
    keyword_dir = master_log_dir / "keywords" / safe_keyword
    
    # Create subdirectories
    raw_dir = keyword_dir / "raw"
    analyzed_dir = keyword_dir / "analyzed"
    reports_dir = keyword_dir / "reports"
    
    # Create all directories
    for directory in [raw_dir, analyzed_dir, reports_dir]:
        directory.mkdir(parents=True, exist_ok=True)
    
    return {
        "keyword_dir": keyword_dir,
        "raw_dir": raw_dir,
        "analyzed_dir": analyzed_dir,
        "reports_dir": reports_dir
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
    
    try:
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
    except Exception as e:
        print(f"Exception while fetching {url}: {e}")
        return None

# ========== ANALYZER ==========
def analyze_text_with_openai(text, keyword, log_dirs=None, source_name=None, page_num=None):
    """
    Analyze text using OpenAI and optionally log the results
    
    Args:
        text (str): The text to analyze
        keyword (str): The keyword being researched
        log_dirs (dict, optional): Log directory paths
        source_name (str, optional): Name of the source being analyzed
        page_num (int, optional): Page number being analyzed
        
    Returns:
        dict: The analysis results
    """
    prompt = f"""
You are a business idea validator.  
Analyze the following text in the context of the keyword: "{keyword}"

Find:
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
                    "keyword": keyword,
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

def process_keyword(keyword, master_log_dir):
    """
    Process a single keyword through the scraping and analysis pipeline
    
    Args:
        keyword (str): The keyword to process
        master_log_dir (Path): Path to the master log directory
        
    Returns:
        dict: The keyword results
    """
    print(f"\n{'='*50}")
    print(f"Processing keyword: {keyword}")
    print(f"{'='*50}")
    
    # Set up logging directories for this keyword
    log_dirs = setup_keyword_log_directories(keyword, master_log_dir)
    
    # Save keyword metadata
    keyword_metadata = {
        "keyword": keyword,
        "timestamp": datetime.datetime.now().isoformat(),
        "sources": list(SOURCES.keys()),
        "pages_per_source": NUM_PAGES
    }
    metadata_path = log_dirs["keyword_dir"] / "keyword_metadata.json"
    save_to_file(keyword_metadata, metadata_path, is_json=True)
    
    all_page_results = []
    source_results = {}  # To track results by source

    for source_name, url_template in SOURCES.items():
        print(f"\nScraping {source_name} for '{keyword}'...")
        source_results[source_name] = []
        
        for page in range(1, NUM_PAGES + 1):
            url = url_template.format(query=keyword.replace(' ', '+'), page=page)
            page_text = fetch_page(url, log_dirs, source_name, page)
            
            if page_text:
                print(f"Analyzing {source_name} page {page} for '{keyword}'...")
                page_result = analyze_text_with_openai(page_text, keyword, log_dirs, source_name, page)
                all_page_results.append(page_result)
                source_results[source_name].append(page_result)
                time.sleep(1)  # be nice, avoid overloading OpenAI or ScraperAPI

    # Merge results for this keyword
    keyword_report = merge_results(all_page_results)
    
    # Save keyword report
    keyword_report_with_metadata = {
        "metadata": {
            "keyword": keyword,
            "timestamp": datetime.datetime.now().isoformat(),
            "sources": list(SOURCES.keys()),
            "pages_per_source": NUM_PAGES
        },
        "results": keyword_report,
        "source_results": source_results
    }
    
    report_path = log_dirs["reports_dir"] / "keyword_report.json"
    save_to_file(keyword_report_with_metadata, report_path, is_json=True)
    
    return keyword_report

def generate_aggregated_report(business_idea, keywords, all_keyword_results, master_log_dir):
    """
    Generate an aggregated report across all keywords
    
    Args:
        business_idea (str): The main business idea
        keywords (list): List of keywords used
        all_keyword_results (dict): Dictionary of results for each keyword
        master_log_dir (Path): Path to the master log directory
        
    Returns:
        dict: The aggregated report
    """
    print("\nGenerating aggregated report...")
    
    # Merge all keyword results
    aggregated_results = {
        "pain_points": [],
        "excitement_signals": [],
        "mentions_of_competitors": [],
        "notable_quotes": []
    }
    
    for keyword, results in all_keyword_results.items():
        for key in aggregated_results:
            aggregated_results[key].extend(results.get(key, []))
    
    # Deduplicate
    for key in aggregated_results:
        aggregated_results[key] = list(set(aggregated_results[key]))
    
    # Create final report
    final_report = {
        "metadata": {
            "business_idea": business_idea,
            "timestamp": datetime.datetime.now().isoformat(),
            "keywords": keywords,
            "sources": list(SOURCES.keys()),
            "pages_per_source": NUM_PAGES
        },
        "aggregated_results": aggregated_results,
        "keyword_results": all_keyword_results
    }
    
    # Save final report
    final_report_path = master_log_dir / "final_report.json"
    save_to_file(final_report, final_report_path, is_json=True)
    
    return final_report

# ========== SCORING AND SUMMARY ==========
def calculate_business_idea_scores(final_report):
    """
    Calculate scores for the business idea based on the validation results
    
    Args:
        final_report (dict): The final aggregated report
        
    Returns:
        dict: Dictionary containing various scores
    """
    print("\nCalculating business idea scores...")
    
    aggregated = final_report["aggregated_results"]
    keyword_results = final_report["keyword_results"]
    keywords = final_report["metadata"]["keywords"]
    
    # Count items in each category
    num_pain_points = len(aggregated["pain_points"])
    num_excitement = len(aggregated["excitement_signals"])
    num_competitors = len(aggregated["mentions_of_competitors"])
    
    # Calculate keyword relevance score
    keyword_relevance = 0
    for keyword in keywords:
        # Calculate how many results each keyword found
        results = keyword_results.get(keyword, {})
        keyword_pain = len(results.get("pain_points", []))
        keyword_excitement = len(results.get("excitement_signals", []))
        keyword_competitors = len(results.get("mentions_of_competitors", []))
        
        # A keyword is more relevant if it found more insights
        keyword_score = keyword_pain + keyword_excitement + keyword_competitors
        keyword_relevance += keyword_score
    
    # Normalize keyword relevance by the number of keywords
    if keywords:
        keyword_relevance = keyword_relevance / len(keywords)
    
    # Calculate individual scores (0-10 scale)
    # Pain points score (more is better, up to a point)
    pain_score = min(10, math.sqrt(num_pain_points) * 2.5)
    
    # Excitement signals score (more is better, up to a point)
    excitement_score = min(10, math.sqrt(num_excitement) * 2.5)
    
    # Competition score (moderate competition is ideal)
    if num_competitors == 0:
        competition_score = 3  # No competitors might mean no market
    elif num_competitors <= 3:
        competition_score = 7  # Few competitors is good
    elif num_competitors <= 7:
        competition_score = 10  # Moderate competition is ideal
    elif num_competitors <= 15:
        competition_score = 8  # More competition means established market
    else:
        competition_score = 6  # Too much competition can be challenging
    
    # Keyword relevance score (0-10)
    keyword_relevance_score = min(10, keyword_relevance)
    
    # Calculate overall viability score (0-100)
    overall_score = (
        pain_score * SCORE_WEIGHTS["pain_points"] * 10 +
        excitement_score * SCORE_WEIGHTS["excitement_signals"] * 10 +
        competition_score * SCORE_WEIGHTS["competitors"] * 10 +
        keyword_relevance_score * SCORE_WEIGHTS["keyword_relevance"] * 10
    )
    
    # Round scores to 1 decimal place
    pain_score = round(pain_score, 1)
    excitement_score = round(excitement_score, 1)
    competition_score = round(competition_score, 1)
    keyword_relevance_score = round(keyword_relevance_score, 1)
    overall_score = round(overall_score, 1)
    
    return {
        "market_pain_score": pain_score,
        "market_interest_score": excitement_score,
        "competition_score": competition_score,
        "keyword_relevance_score": keyword_relevance_score,
        "overall_viability_score": overall_score,
        "raw_counts": {
            "pain_points": num_pain_points,
            "excitement_signals": num_excitement,
            "competitors": num_competitors
        }
    }

def generate_executive_summary(final_report, scores):
    """
    Generate a concise executive summary of the business idea validation results
    
    Args:
        final_report (dict): The final aggregated report
        scores (dict): The calculated scores
        
    Returns:
        dict: The executive summary
    """
    print("\nGenerating executive summary...")
    
    business_idea = final_report["metadata"]["business_idea"]
    aggregated = final_report["aggregated_results"]
    
    # Get top pain points (up to 5)
    top_pain_points = aggregated["pain_points"][:min(5, len(aggregated["pain_points"]))]
    
    # Get top excitement signals (up to 5)
    top_excitement = aggregated["excitement_signals"][:min(5, len(aggregated["excitement_signals"]))]
    
    # Get top competitors (up to 5)
    top_competitors = aggregated["mentions_of_competitors"][:min(5, len(aggregated["mentions_of_competitors"]))]
    
    # Determine market validation status based on overall score
    overall_score = scores["overall_viability_score"]
    if overall_score >= 80:
        validation_status = "Strongly Validated"
        recommendation = "This business idea shows strong market validation. Consider proceeding with development and creating an MVP."
    elif overall_score >= 65:
        validation_status = "Validated"
        recommendation = "This business idea shows good market validation. Consider proceeding with caution, focusing on the identified pain points."
    elif overall_score >= 50:
        validation_status = "Partially Validated"
        recommendation = "This business idea shows moderate market validation. Consider refining the concept based on the identified pain points and excitement signals."
    elif overall_score >= 35:
        validation_status = "Weakly Validated"
        recommendation = "This business idea shows weak market validation. Consider pivoting or significantly refining the concept before proceeding."
    else:
        validation_status = "Not Validated"
        recommendation = "This business idea lacks sufficient market validation. Consider exploring alternative ideas or completely rethinking the approach."
    
    # Generate insights based on scores
    insights = []
    
    if scores["market_pain_score"] >= 7:
        insights.append("Strong pain points identified, indicating a clear market need.")
    elif scores["market_pain_score"] <= 3:
        insights.append("Few significant pain points identified, suggesting limited market need.")
    
    if scores["market_interest_score"] >= 7:
        insights.append("High market interest detected, indicating potential demand.")
    elif scores["market_interest_score"] <= 3:
        insights.append("Low market interest detected, suggesting limited demand.")
    
    if scores["competition_score"] >= 7:
        insights.append("Healthy competitive landscape, indicating a validated market.")
    elif scores["competition_score"] <= 3:
        insights.append("Limited competition may indicate an untapped market or lack of market viability.")
    
    if scores["keyword_relevance_score"] >= 7:
        insights.append("Keywords were highly relevant, providing good market insights.")
    elif scores["keyword_relevance_score"] <= 3:
        insights.append("Keywords had limited relevance, suggesting the need for refined market research.")
    
    # Create the executive summary
    summary = {
        "business_idea": business_idea,
        "validation_status": validation_status,
        "overall_score": overall_score,
        "top_pain_points": top_pain_points,
        "top_excitement_signals": top_excitement,
        "top_competitors": top_competitors,
        "key_insights": insights,
        "recommendation": recommendation
    }
    
    return summary

def display_results(final_report, master_log_dir):
    """
    Display the final results in the console
    
    Args:
        final_report (dict): The final aggregated report
        master_log_dir (Path): Path to the master log directory
    """
    print("\n" + "="*60)
    print("=== Enhanced Business Idea Validation Report ===")
    print("="*60)
    
    print(f"\nBusiness Idea: {final_report['metadata']['business_idea']}")
    print(f"Keywords Used: {', '.join(final_report['metadata']['keywords'])}")
    
    aggregated = final_report["aggregated_results"]
    
    print("\n--- Aggregated Results ---\n")
    
    if aggregated["pain_points"]:
        print(f"Pain Points:\n - " + "\n - ".join(aggregated["pain_points"]))
    else:
        print("Pain Points: None found")
        
    if aggregated["excitement_signals"]:
        print(f"\nExcitement Signals:\n - " + "\n - ".join(aggregated["excitement_signals"]))
    else:
        print("\nExcitement Signals: None found")
        
    if aggregated["mentions_of_competitors"]:
        print(f"\nMentions of Competitors:\n - " + "\n - ".join(aggregated["mentions_of_competitors"]))
    else:
        print("\nMentions of Competitors: None found")
        
    if aggregated["notable_quotes"]:
        print(f"\nNotable Quotes:\n - " + "\n - ".join(aggregated["notable_quotes"]))
    else:
        print("\nNotable Quotes: None found")
    
    print("\n--- Results by Keyword ---")
    for keyword, results in final_report["keyword_results"].items():
        print(f"\n  {keyword}:")
        for key, items in results.items():
            if items:
                print(f"    {key.replace('_', ' ').title()}: {len(items)} items")
            else:
                print(f"    {key.replace('_', ' ').title()}: None found")
    
    # Calculate scores
    scores = calculate_business_idea_scores(final_report)
    
    # Generate executive summary
    summary = generate_executive_summary(final_report, scores)
    
    # Display scores
    print("\n" + "="*60)
    print("=== BUSINESS IDEA SCORECARD ===")
    print("="*60)
    
    print(f"\nMarket Pain Score: {scores['market_pain_score']}/10")
    print(f"Market Interest Score: {scores['market_interest_score']}/10")
    print(f"Competition Score: {scores['competition_score']}/10")
    print(f"Keyword Relevance Score: {scores['keyword_relevance_score']}/10")
    print(f"\nOVERALL VIABILITY SCORE: {scores['overall_viability_score']}/100")
    
    # Display executive summary
    print("\n" + "="*60)
    print("=== EXECUTIVE SUMMARY ===")
    print("="*60)
    
    print(f"\nValidation Status: {summary['validation_status']} ({summary['overall_score']}/100)")
    
    print("\nTop Pain Points:")
    for point in summary["top_pain_points"]:
        print(f" - {point}")
    
    print("\nTop Excitement Signals:")
    for signal in summary["top_excitement_signals"]:
        print(f" - {signal}")
    
    print("\nKey Competitors:")
    for competitor in summary["top_competitors"]:
        print(f" - {competitor}")
    
    print("\nKey Insights:")
    for insight in summary["key_insights"]:
        print(f" - {insight}")
    
    print(f"\nRecommendation: {summary['recommendation']}")
    
    # Save summary and scores to file
    summary_with_scores = {
        "scores": scores,
        "executive_summary": summary
    }
    summary_path = master_log_dir / "executive_summary.json"
    save_to_file(summary_with_scores, summary_path, is_json=True)
    
    print(f"\nFull JSON report saved to: {master_log_dir / 'final_report.json'}")
    print(f"Executive summary saved to: {summary_path}")

# ========== MAIN ==========
def main():
    """Main function to run the enhanced business idea validator"""
    business_idea = input("Enter your business idea: ")
    
    # Set up master logging directory
    master_log_dir = setup_master_log_directory(business_idea)
    print(f"Logs will be saved to: {master_log_dir}")
    
    # Generate keywords
    keywords = generate_keywords(business_idea)
    print(f"Generated keywords: {keywords}")
    
    # Save keywords metadata
    keywords_metadata = {
        "business_idea": business_idea,
        "timestamp": datetime.datetime.now().isoformat(),
        "keywords": keywords
    }
    metadata_path = master_log_dir / "keywords_metadata.json"
    save_to_file(keywords_metadata, metadata_path, is_json=True)
    
    # Process each keyword
    all_keyword_results = {}
    for keyword in keywords:
        keyword_results = process_keyword(keyword, master_log_dir)
        all_keyword_results[keyword] = keyword_results
    
    # Generate aggregated report
    final_report = generate_aggregated_report(business_idea, keywords, all_keyword_results, master_log_dir)
    
    # Display results with scores and executive summary
    display_results(final_report, master_log_dir)

if __name__ == "__main__":
    main()
