import re

with open("wipro.html", "r", encoding="utf-8") as f:
    content = f.read()

# Find job links
links = re.findall(r'href="([^"]*/job/[^"]*)"', content)
print(f"Found {len(links)} /job/ links:")
for link in set(links):
    print(link)
