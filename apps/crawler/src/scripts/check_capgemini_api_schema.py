import requests
import json

headers = {'User-Agent': 'Mozilla/5.0'}
res = requests.get("https://cg-jobstream-api.azurewebsites.net/api/job-search?page=1&size=3&country_code=in-en", headers=headers, timeout=10)
if res.ok:
    data = res.json()
    print("Capgemini API response keys:", data.keys())
    for item in data.get('data', []):
        print("\n" + "=" * 60)
        print(f"Title: {item.get('title')}")
        print(f"ID: {item.get('id')}")
        print(f"Job ID: {item.get('job_id')}")
        print(f"Slug: {item.get('slug')}")
        print(f"Country Code: {item.get('country_code')}")
        print(f"Direct Apply / URL fields:")
        for k, v in item.items():
            if any(w in k.lower() for w in ['url', 'link', 'path', 'href', 'apply']):
                print(f"  {k} : {v}")
        print(f"Full Item Keys: {list(item.keys())}")
