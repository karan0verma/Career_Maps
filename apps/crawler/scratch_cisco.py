import requests
import json

url = "https://careers.cisco.com/widgets"
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Origin": "https://careers.cisco.com",
    "Referer": "https://careers.cisco.com/global/en/search-results?q=India",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
payload = {
    "lang": "en_global",
    "deviceType": "desktop",
    "country": "global",
    "pageName": "search-results",
    "ddoKey": "eagerLoadRefineSearchSession",
    "sortBy": "",
    "subsearch": "",
    "from": 0,
    "jobs": True,
    "counts": True,
    "all_fields": ["category", "country", "city", "state", "type"],
    "size": 50,
    "clearAll": False,
    "jdsource": "facets",
    "isSliderEnable": False,
    "pageId": "page1",
    "siteType": "external",
    "keywords": "India",
    "global": True,
    "selected_fields": {"country": ["India"]}
}
res = requests.post(url, headers=headers, json=payload)
print(res.status_code)
if res.ok:
    data = res.json()
    jobs = data.get("refineSearch", {}).get("data", {}).get("jobs", [])
    print(f"Found {len(jobs)} jobs for Cisco")
    if jobs:
        print(jobs[0].get("title"), jobs[0].get("city"), jobs[0].get("jobId"))
else:
    print(res.text)
