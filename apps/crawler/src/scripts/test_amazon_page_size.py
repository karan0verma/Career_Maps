import urllib.request
import json

url = "https://www.amazon.jobs/en/search.json?country=IND&result_limit=100&offset=0"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
res = urllib.request.urlopen(req)
d = json.loads(res.read().decode())
print("Jobs returned with result_limit=100:", len(d.get('jobs', [])))
