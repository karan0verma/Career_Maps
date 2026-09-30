import requests

def probe_phenom():
    url = "https://careers.cognizant.com/api/jobs"
    payload = {
        "from": 0,
        "size": 10,
        "location": ["India"]
    }
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    try:
        res = requests.post(url, json=payload, headers=headers, timeout=10)
        print("Status:", res.status_code)
        if res.status_code == 200:
            print(res.json().keys())
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    probe_phenom()
