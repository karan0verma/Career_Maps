import requests
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/html, */*'
}

print("Testing Cisco India Endpoint...", flush=True)
url_cisco = "https://jobs.cisco.com/api/jobs?location=India&limit=100"
try:
    res = requests.get(url_cisco, headers=headers, timeout=10)
    print("Cisco Status:", res.status_code)
    if res.ok:
        print("Cisco Keys:", res.json().keys())
except Exception as e:
    print("Cisco error:", e)

print("\nTesting Google India Endpoint...", flush=True)
url_google = "https://careers.google.com/api/v3/search/?distance=50&location=India&page=1&page_size=100"
try:
    res = requests.get(url_google, headers=headers, timeout=10)
    print("Google Status:", res.status_code)
    if res.ok:
        print("Google Jobs Count:", len(res.json().get('jobs', [])))
        print("Sample Google Job:", res.json().get('jobs', [])[0].get('title') if res.json().get('jobs') else None)
except Exception as e:
    print("Google error:", e)
