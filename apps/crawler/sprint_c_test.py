import requests
import json
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*'
}

def test_eightfold():
    print("\n--- Eightfold AI ---")
    url = "https://micron.eightfold.ai/api/apply/v2/jobs"
    try:
        resp = requests.get(url, params={"domain": "micron.com", "start": 0, "num": 10}, headers=headers, timeout=10)
        print("Status:", resp.status_code)
        if resp.status_code == 200:
            data = resp.json()
            if 'positions' in data:
                print("Found positions!")
                if len(data['positions']) > 0:
                    print("First position keys:", data['positions'][0].keys())
    except Exception as e:
        print(e)

def test_zoho():
    print("\n--- Zoho Recruit ---")
    try:
        html_resp = requests.get("https://zohocorp.zohorecruit.com/jobs/Careers", headers=headers, timeout=10)
        print("HTML Status:", html_resp.status_code)
        soup = BeautifulSoup(html_resp.text, 'html.parser')
        scripts = soup.find_all('script')
        for i, s in enumerate(scripts):
            if s.string and '{' in s.string:
                print(f"Script {i} contains JSON-like content of length {len(s.string)}")
                if len(s.string) > 1000:
                    print(s.string[:200])
                    
    except Exception as e:
        print(e)

test_eightfold()
test_zoho()
