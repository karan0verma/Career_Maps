import os
import sys
import json
import urllib.request

def test_recruiting():
    url = "https://careers.wipro.com/services/recruiting/v1/jobs"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Referer': 'https://careers.wipro.com/search/',
        'Origin': 'https://careers.wipro.com'
    }

    print("Testing GET:", url)
    try:
        req = urllib.request.Request(url, headers=headers)
        res = urllib.request.urlopen(req)
        data = json.loads(res.read().decode())
        print("GET Status:", res.status)
        print("Response Type:", type(data))
        if isinstance(data, dict):
            print("Keys:", list(data.keys()))
            for k in data.keys():
                if isinstance(data[k], list):
                    print(f"  '{k}' count: {len(data[k])}")
                    if len(data[k]) > 0:
                        print("  Sample:", json.dumps(data[k][0], indent=2))
        elif isinstance(data, list):
            print("List count:", len(data))
            if len(data) > 0:
                print("Sample:", json.dumps(data[0], indent=2))
    except Exception as e:
        print("GET Error:", e)

if __name__ == "__main__":
    test_recruiting()
