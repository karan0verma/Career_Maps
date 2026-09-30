import re
import json

with open("wipro.html", "r", encoding="utf-8") as f:
    content = f.read()

# Look for jobs JSON in script tags
pattern = re.compile(r'phapp\.ddo\s*=\s*(\{.*?\});', re.DOTALL)
match = pattern.search(content)
if match:
    print("Found phapp.ddo!")
    print(match.group(1)[:500])
else:
    # Look for another common one
    print("Searching for RMK jobs...")
    lines = [line for line in content.split('\n') if 'job' in line.lower() and '{' in line]
    print(f"Found {len(lines)} potential lines")
