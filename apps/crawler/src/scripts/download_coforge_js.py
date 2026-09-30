import requests
import json
import re

url = 'https://careers.coforge.com/coforge/main.649dc485273b0131.js'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}

r = requests.get(url, headers=headers)
with open('coforge_main.js', 'w', encoding='utf-8') as f:
    f.write(r.text)

print(f"Saved coforge_main.js ({len(r.text)} chars)")

# Find all occurrences of http:// or https:// or /api/
matches = set(re.findall(r'https?://[a-zA-Z0-9_\-\.:/]+|/[a-zA-Z0-9_\-]+/[a-zA-Z0-9_\-\./]+', r.text))
for m in sorted(matches):
    m_lower = m.lower()
    if any(k in m_lower for k in ['job', 'career', 'search', 'api', 'opp', 'portal', 'opening', 'candidate', 'vacanc']):
        print("MATCH:", m)
