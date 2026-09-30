import requests
from bs4 import BeautifulSoup

def test_ey_custom():
    url = "https://careers.ey.com/ey/search/?q=&locationsearch=India&startrow=0"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    res = requests.get(url, headers=headers)
    print("Status:", res.status_code)
    
    soup = BeautifulSoup(res.text, 'html.parser')
    jobs = soup.find_all('tr', class_='data-row')
    print("Found jobs in HTML:", len(jobs))
    
    if jobs:
        title = jobs[0].find('span', class_='jobTitle')
        loc = jobs[0].find('span', class_='jobLocation')
        if title:
            a = title.find('a')
            print("Job:", a.text.strip(), "| URL:", a.get('href') if a else None)
        if loc:
            print("Location:", loc.text.strip())

if __name__ == "__main__":
    test_ey_custom()
