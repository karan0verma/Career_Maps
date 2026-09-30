import requests
import re

js_url = 'https://careers.coforge.com/coforge/main.649dc485273b0131.js'
r = requests.get(js_url)
print(f"Downloaded main.js ({len(r.text)} bytes)")

# Find string literals containing http or api
urls = set(re.findall(r'["\'](https?://[^"\']+|/[^"\']+)["\']', r.text))
print(f"Found {len(urls)} string literal URLs/paths:")
for u in sorted(urls):
    u_lower = u.lower()
    if any(k in u_lower for k in ['job', 'career', 'search', 'api', 'opp', 'portal', 'opening', 'list', 'vacanc', 'requisition']):
        print("  - Candidate:", u)
