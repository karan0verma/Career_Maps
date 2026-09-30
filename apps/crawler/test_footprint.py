import requests
import re
from bs4 import BeautifulSoup

URLS = [
    "https://careers.airbnb.com",
    "https://www.figma.com/careers",
    "https://careers.doordash.com",
    "https://about.gitlab.com/jobs/",
]

for url in URLS:
    try:
        resp = requests.get(url, timeout=10)
        html = resp.text
        
        print(f"\nChecking {url}")
        
        # Look for script src="...greenhouse.io/embed/job_board/js?for=TOKEN"
        match = re.search(r'for=([^"\'&]+)', html)
        if "greenhouse.io/embed" in html and match:
            print(f"Found embedded board token: {match.group(1)}")
            continue
            
        # Look for iframe src
        iframe = re.search(r'boards\.greenhouse\.io/([^/"\']+)', html)
        if iframe:
            print(f"Found iframe board token: {iframe.group(1)}")
            continue
            
        # Look for direct links to boards.greenhouse.io
        links = re.findall(r'boards\.greenhouse\.io/([^/"\']+)', html)
        if links:
            print(f"Found links with board token: {set(links)}")
            continue
            
        # Look for boards-api.greenhouse.io calls
        api_call = re.search(r'boards-api\.greenhouse\.io/v1/boards/([^/"\']+)', html)
        if api_call:
            print(f"Found API call with board token: {api_call.group(1)}")
            continue

        print("No obvious Greenhouse footprint found directly on the main careers page HTML.")
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
