import os
import sys
import json
import requests

url = "https://adobe.wd5.myworkdayjobs.com/wday/cxs/adobe/external_experienced/jobs"
# Fetch jobs with facets for jobFamily
payload = {
    "appliedFacets": {},
    "limit": 20,
    "offset": 0,
    "searchText": "India"
}
headers = {'User-Agent': 'Mozilla/5.0'}
res = requests.post(url, json=payload, headers=headers, timeout=10)
if res.ok:
    d = res.json()
    postings = d.get('jobPostings', [])
    print(f"Total postings in batch: {len(postings)}")
