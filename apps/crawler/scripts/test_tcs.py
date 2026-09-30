import requests

def test_tcs():
    url = "https://ibegin.tcs.com/iBegin/jobs/search"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    try:
        res2 = requests.get(url, headers=headers, timeout=10)
        print("HTML Status:", res2.status_code)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test_tcs()
