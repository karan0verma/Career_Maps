import urllib.request
import re

content = urllib.request.urlopen("https://career.infosys.com/main.js").read().decode('utf-8', errors='ignore')

idx = content.find("JobdescriptionComponent")
snippet = content[idx:idx+10000]

# find all queryParams references inside this component
matches = re.findall(r'queryParams[^\.\,\;]+', snippet)
print("queryParams in JobdescriptionComponent:")
for m in set(matches):
    print(" ", m)

# find ngOnInit inside this component
init_matches = re.findall(r'ngOnInit\(\)[^{]+{[^}]+}', snippet)
print("\nngOnInit in JobdescriptionComponent:")
for im in init_matches:
    print(" ", im[:500])
