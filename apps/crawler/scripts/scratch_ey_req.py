import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}
url = "https://careers.ey.com/ey/search/?createNewAlert=false&q=&locationsearch=India"
res = requests.get(url, headers=headers)
print(res.status_code)
soup = BeautifulSoup(res.text, 'html.parser')
rows = soup.select('tr.data-row')
print(f"Found {len(rows)} data rows")
