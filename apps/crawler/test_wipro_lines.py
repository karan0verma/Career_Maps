import json

with open("wipro.html", "r", encoding="utf-8") as f:
    content = f.read()

lines = [line.strip() for line in content.split('\n') if 'job' in line.lower() and '{' in line.lower()]
for line in lines[:5]:
    print(line[:200])
