import urllib.request
import json

url = "https://www.amazon.jobs/en/search.json?country=IND&facets[]=location&facets[]=business_category&facets[]=category&offset=0&result_limit=1"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
res = urllib.request.urlopen(req)
data = json.loads(res.read().decode())

print("Amazon Facets Available:", list(data.get('facets', {}).keys()))
locs = data.get('facets', {}).get('location_facet', [])
print("\nAmazon Location Breakdown:")
blr_total = 0
for item in locs:
    title = item.get('title', item.get('name', ''))
    count = item.get('count', 0)
    print(f"  • {title}: {count} jobs")
    if 'bengaluru' in title.lower() or 'bangalore' in title.lower():
        blr_total += count

print(f"\n==> EXACT TOTAL AMAZON JOBS IN BENGALURU: {blr_total}")
