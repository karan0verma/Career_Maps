import urllib.request
import json

url = "https://www.amazon.jobs/en/search.json?country=IND&offset=0&result_limit=1"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
res = urllib.request.urlopen(req)
data = json.loads(res.read().decode())

print("Facet keys:", list(data.get('facets', {}).keys()))
for k, v in data.get('facets', {}).items():
    print(f"\n--- Facet: {k} (type: {type(v)}, len: {len(v)}) ---")
    if isinstance(v, dict):
        for sub_k, sub_v in list(v.items())[:10]:
            print(f"  {sub_k}: {sub_v}")
    elif isinstance(v, list) and v:
        print("  Sample item:", v[0])
