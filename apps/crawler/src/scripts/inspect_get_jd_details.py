import urllib.request
import re

content = urllib.request.urlopen("https://career.infosys.com/main.js").read().decode('utf-8', errors='ignore')

matches = [m.start() for m in re.finditer(r'getJobDescriptionDetails', content)]
for m in matches[:5]:
    print("\n--- getJobDescriptionDetails snippet ---")
    print(content[m-100:m+400])
