import urllib.request
from bs4 import BeautifulSoup

url = "https://careers.wipro.com/search/?createNewAlert=false&q=&locationsearch=India"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
req = urllib.request.Request(url, headers=headers)
html = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')
soup = BeautifulSoup(html, 'html.parser')

links = soup.find_all('a', href=lambda h: h and '/job/' in h)
print(f"Found {len(links)} job links with '/job/':")
for l in links[:10]:
    print("  •", l.get_text(strip=True), "->", l.get('href'))

# Also check table or list items
tables = soup.find_all('table')
print(f"Tables: {len(tables)}")
for t in tables:
    print("  Table classes/id:", t.get('class'), t.get('id'), "Rows:", len(t.find_all('tr')))
