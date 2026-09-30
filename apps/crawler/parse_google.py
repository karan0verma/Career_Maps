from bs4 import BeautifulSoup
import json

def parse():
    with open("google_jobs.html", "r", encoding="utf-8") as f:
        html = f.read()
        
    soup = BeautifulSoup(html, 'html.parser')
    
    # Try to find common job item classes
    # Looking for a tag that looks like a title, usually <h2> or <h3>
    headers = soup.find_all(['h2', 'h3'])
    for h in headers:
        print(f"Header: {h.name}, text: {h.get_text(strip=True)}, class: {h.get('class')}")
        parent = h.find_parent('li') or h.find_parent('div')
        if parent:
            print(f"  Parent: {parent.name}, class: {parent.get('class')}")
            links = parent.find_all('a')
            for link in links:
                print(f"    Link: {link.get('href')}")
            
if __name__ == "__main__":
    parse()
