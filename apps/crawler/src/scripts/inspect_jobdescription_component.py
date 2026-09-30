import urllib.request
import re

content = urllib.request.urlopen("https://career.infosys.com/main.js").read().decode('utf-8', errors='ignore')

# Search for JobdescriptionComponent code block
idx = content.find("JobdescriptionComponent")
if idx != -1:
    snippet = content[idx-500:idx+2500]
    print("--- JobdescriptionComponent Snippet ---")
    print(snippet)
else:
    print("Not found directly, searching referenceCode...")
    matches = [m.start() for m in re.finditer(r'jobReferenceCode', content)]
    for m in matches[:5]:
        print("\n--- Match ---")
        print(content[m-200:m+500])
