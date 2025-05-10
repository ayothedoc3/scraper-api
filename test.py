import requests
import openai
import time
import json

# ========== CONFIG ==========
SCRAPER_API_KEY = '57e9758e150311f9e07c9923e5731678'
OPENAI_API_KEY = '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'

NUM_PAGES = 2  # how many pages per site to fetch
SOURCES = {
    "Reddit": "https://www.reddit.com/search/?q={query}&page={page}",
}
openai.api_key = OPENAI_API_KEY

# ========== FETCHER ==========
def fetch_page(url):
    params = {
        'api_key': SCRAPER_API_KEY,
        'url': url,
        'output_format': 'text'
    }
    response = requests.get('https://api.scraperapi.com/', params=params)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Error fetching {url}: {response.status_code}")
        return None

# ========== ANALYZER ==========
def analyze_text_with_openai(text, business_idea):
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
        # Parse and return JSON
        return json.loads(reply)
    except Exception as e:
        print("Error during OpenAI analysis:", e)
        return {
            "pain_points": [],
            "excitement_signals": [],
            "mentions_of_competitors": [],
            "notable_quotes": []
        }

# ========== MERGER ==========
def merge_results(all_results):
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
    idea = input("Enter your business idea keyword: ")
    all_page_results = []

    for source_name, url_template in SOURCES.items():
        print(f"\nScraping {source_name}...")
        for page in range(1, NUM_PAGES + 1):
            url = url_template.format(query=idea.replace(' ', '+'), page=page)
            page_text = fetch_page(url)
            if page_text:
                print(f"Analyzing {source_name} page {page}...")
                page_result = analyze_text_with_openai(page_text, idea)
                all_page_results.append(page_result)
                time.sleep(1)  # be nice, avoid overloading OpenAI or ScraperAPI

    final_report = merge_results(all_page_results)

    # ========== FINAL OUTPUT ==========
    print("\n=== Business Idea Validation Report ===\n")
    print(f"Pain Points:\n - " + "\n - ".join(final_report["pain_points"]))
    print(f"\nExcitement Signals:\n - " + "\n - ".join(final_report["excitement_signals"]))
    print(f"\nMentions of Competitors:\n - " + "\n - ".join(final_report["mentions_of_competitors"]))
    print(f"\nNotable Quotes:\n - " + "\n - ".join(final_report["notable_quotes"]))

if __name__ == "__main__":
    main()
