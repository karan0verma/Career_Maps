import urllib.request
import re

content = urllib.request.urlopen('https://career.infosys.com/main.js').read().decode('utf-8', errors='ignore')
matches = re.findall(r'intapjbsrch[^"\'`\s\)]+', content)
print("Unique intapjbsrch references:")
for m in sorted(set(matches)):
    print("  •", m)
