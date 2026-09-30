import requests
import json

url = "https://apply.careers.microsoft.com/api/pcsx/search"
params = {
    "domain": "microsoft.com",
    "start": 0,
    "limit": 10
}
resp = requests.get(url, params=params)
print(resp.status_code)
if resp.status_code == 200:
    data = resp.json()
    jobs = data.get("data", [])
    print(f"Found {len(jobs)} jobs")
    if jobs:
        print(json.dumps(jobs[0], indent=2))
