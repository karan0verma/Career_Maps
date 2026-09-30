import requests
import json

url = "https://pwc.wd3.myworkdayjobs.com/wday/cxs/pwc/Global_Careers/jobs"
payload = {
    "appliedFacets": {"Location_Country": ["bc33aa31523742cb80ce0af4f21689c5"]}, # Typical Workday facet for India, but let's try without facets first and search 'India'
    "limit": 20,
    "offset": 0,
    "searchText": "India"
}
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0"
}
response = requests.post(url, json=payload, headers=headers)
print(response.status_code)
if response.ok:
    data = response.json()
    print(f"Total: {data.get('total')}")
    for item in data.get('jobPostings', [])[:3]:
        print(item['title'], item['externalPath'])
