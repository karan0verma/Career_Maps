import requests
from bs4 import BeautifulSoup

def test_ey():
    url = "https://careers.ey.com/ey/job/search"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    try:
        res = requests.get(url, headers=headers)
        print("Status:", res.status_code)
        if res.status_code == 200:
            print("Content snippet:", res.text[:500])
            # Check for common ATS signatures
            if "SuccessFactors" in res.text or "jobs2web" in res.text:
                print("ATS Detected: SuccessFactors / Jobs2Web")
            elif "taleo" in res.text:
                print("ATS Detected: Taleo")
            elif "eightfold" in res.text:
                print("ATS Detected: Eightfold")
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test_ey()
