from bs4 import BeautifulSoup

with open("hsbc_dump.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), 'html.parser')
    
links = soup.find_all('a')
print(f"Total links: {len(links)}")
for a in links[:20]:
    print(a.get('href'), a.text.strip())
    
print("---")
# Look for anything containing 'job' in href
for a in links:
    href = a.get('href', '')
    if 'job' in href.lower() or 'role' in href.lower():
        print(href, a.text.strip())
