import urllib.request
import json

cities = ['Bengaluru', 'Bangalore', 'Hyderabad', 'Chennai', 'Pune', 'Gurgaon', 'Delhi', 'Mumbai']

print("=" * 70)
print("AMAZON INDIA CITY-WISE LIVE JOBS QUERY")
print("=" * 70)

for c in cities:
    url = f"https://www.amazon.jobs/en/search.json?country=IND&city={c}&offset=0&result_limit=1"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        res = urllib.request.urlopen(req)
        d = json.loads(res.read().decode())
        print(f"  • Amazon in {c:12}: {d.get('hits')} live jobs")
    except Exception as e:
        print(f"  • {c}: Error {e}")
