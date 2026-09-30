import requests
import json

url = "https://pwc.wd3.myworkdayjobs.com/wday/cxs/pwc/Global_Careers/jobs"
payload = {
    "appliedFacets": {},
    "limit": 20,
    "offset": 0,
    "searchText": "India"
}
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

try:
    res = requests.post(url, json=payload, headers=headers)
    print(res.status_code)
    data = res.json()
    print(f"Total jobs: {data.get('total')}")
    for item in data.get('jobPostings', [])[:3]:
        print(item['title'], item['externalPath'])
except Exception as e:
    print(e)
