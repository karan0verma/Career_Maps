import re

with open("wipro_rendered.html", "r", encoding="utf-8") as f:
    content = f.read()

links = re.findall(r'href="([^"]*/job/[^"]*)"', content)
print(f"Found {len(links)} /job/ links:")
for link in list(set(links))[:5]:
    print(link)
    
if not links:
    # try any links that look like jobs
    all_links = re.findall(r'href="([^"]*)"', content)
    job_links = [l for l in all_links if "job" in l.lower() and "search" not in l.lower()]
    print(f"Found {len(job_links)} fallback job links:")
    for link in list(set(job_links))[:5]:
        print(link)
