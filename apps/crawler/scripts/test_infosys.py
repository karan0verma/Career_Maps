import requests
from bs4 import BeautifulSoup

def test_infosys():
    url = "https://career.infosys.com/joblist"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        res = requests.get(url, headers=headers, timeout=10)
        print("Status:", res.status_code)
        print("URL:", res.url)
        print("Content snippet:", res.text[:500])
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test_infosys()
