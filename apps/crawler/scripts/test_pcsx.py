import requests

def test_api():
    url = "https://careers.cognizant.com/api/pcsx/search"
    params = {
        "domain": "cognizant.com",
        "start": 0,
        "limit": 50
    }
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    try:
        res = requests.get(url, params=params, headers=headers)
        print("Status:", res.status_code)
        if res.status_code == 200:
            data = res.json()
            print("Jobs:", len(data.get('data', [])))
            print(data['data'][0]['reqId'])
        else:
            print(res.text[:500])
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test_api()
