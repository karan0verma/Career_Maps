import requests
from bs4 import BeautifulSoup
import re
import urllib3
urllib3.disable_warnings()

targets = [
    "https://www.tcs.com/careers",
    "https://www.globallogic.com/careers/",
    "https://www.ukg.com/careers",
    "https://www.delhivery.com/careers",
    "https://www.pinelabs.com/careers"
]

def check():
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})
    
    for url in targets:
        print(f"Checking {url}")
        try:
            resp = session.get(url, verify=False, timeout=10)
            text = resp.text.lower()
            
            ats_keywords = [
                'icims', 'taleo', 'brassring', 'avature', 'smartrecruiters', 
                'workday', 'successfactors', 'myworkdayjobs', 'jobvite', 
                'workable', 'breezy', 'recruitee', 'eightfold', 'darwinbox',
                'oraclecloud', 'peoplesoft', 'silkroad', 'pageuppeople'
            ]
            
            found = []
            for kw in ats_keywords:
                if kw in text:
                    found.append(kw)
                    
            print(f"  Keywords found: {found}")
            
            # extract outbound links
            soup = BeautifulSoup(resp.text, 'html.parser')
            links = set()
            for a in soup.find_all('a', href=True):
                href = a['href']
                if 'http' in href and not any(x in href for x in ['tcs.com', 'globallogic.com', 'ukg.com', 'delhivery.com', 'pinelabs.com', 'linkedin', 'facebook', 'twitter', 'instagram', 'youtube']):
                    links.add(href)
                    
            print("  Outbound links:")
            for l in list(links)[:10]:
                print(f"    {l}")
        except Exception as e:
            print(f"  Error: {e}")
            
if __name__ == "__main__":
    check()
