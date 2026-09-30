import os
import sys
import json
import requests

url = "https://adobe.wd5.myworkdayjobs.com/wday/cxs/adobe/external_experienced/jobs"
payload = {
    "appliedFacets": {},
    "limit": 1,
    "offset": 0,
    "searchText": "India"
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
}

res = requests.post(url, json=payload, headers=headers, timeout=10)
if res.ok:
    d = res.json()
    facets = d.get('facets', [])
    print("=" * 80)
    print("ALL ADOBE CAREER SITE TEAMS / JOB FAMILIES (WORKDAY FACETS):")
    print("=" * 80)
    for f in facets:
        print(f"\nFacet Parameter: {f.get('facetParameter')}")
        for v in f.get('values', []):
            print(f"  • Team / Category: {v.get('descriptor'):40} | Active Jobs: {v.get('count')}")
else:
    print(f"Failed to fetch Adobe facets: {res.status_code}")
