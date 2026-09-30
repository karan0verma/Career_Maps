import requests
import urllib3
urllib3.disable_warnings()
from bs4 import BeautifulSoup

def scrape_kpmg():
    print("Scraping KPMG...")
    res = requests.get("https://kpmg.com/in/en/home/careers.html", verify=False)
    soup = BeautifulSoup(res.text, 'html.parser')
    links = soup.find_all('a', href=True)
    jobs = []
    for l in links:
        if '/job/' in l['href'].lower() or 'careers' in l['href'].lower():
            print(l['href'])

if __name__ == "__main__":
    scrape_kpmg()
