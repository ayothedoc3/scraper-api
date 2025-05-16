import requests
from bs4 import BeautifulSoup

# Method 1: Basic requests + BeautifulSoup
def fetch_basic(url):
    print("=== Basic Fetch ===")
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        content = '\n'.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
        return content
    except Exception as e:
        print(f"Basic fetch error: {e}")
        return None

# Method 2: Using ScraperAPI
def fetch_page(url):
    print("=== ScraperAPI Fetch ===")
    SCRAPER_API_KEY = '57e9758e150311f9e07c9923e5731678'
    params = {
        'api_key': SCRAPER_API_KEY,
        'url': url,
        'output_format': 'text'
    }
    
    try:
        response = requests.get('https://api.scraperapi.com/', params=params)
        
        if response.status_code == 200:
            content = response.text
            return content
        else:
            print(f"Error fetching {url}: {response.status_code}")
            return None
    except Exception as e:
        print(f"Exception while fetching {url}: {e}")
        return None

# Compare both methods
url = "https://neilpatel.com"

print("Fetching content using both methods...\n")

# Get content from both methods
basic_content = fetch_basic(url)
api_content = fetch_page(url)

# Compare results
print("\n=== COMPARISON ===")
print(f"Basic fetch content length: {len(basic_content) if basic_content else 0}")
print(f"ScraperAPI content length: {len(api_content) if api_content else 0}")

# Show first 200 characters of each
if basic_content:
    print(f"\nBasic fetch preview:\n{basic_content[:200]}...")
    
if api_content:
    print(f"\nScraperAPI preview:\n{api_content[:200]}...")



