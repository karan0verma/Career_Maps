import urllib.request
import re

content = urllib.request.urlopen("https://career.infosys.com/main.js").read().decode('utf-8', errors='ignore')

# find all Angular routes defined in main.js
routes = re.findall(r'path:\s*["\']([^"\']+)["\']\s*,\s*loadComponent:[^}]+', content)
print("All registered Angular routes on career.infosys.com:")
for r in routes:
    print("  • /" + r)

# Also check router.navigate calls
nav_calls = re.findall(r'navigate\(\[[^\]]+\][^\)]*\)', content)
print("\nSample navigate calls:")
for n in set(nav_calls[:15]):
    print("  ->", n)
