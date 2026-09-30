import requests
from bs4 import BeautifulSoup
import re
import json

def fetch_ntpc():
    url = "https://careers.ntpc.co.in/recruitment/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"}
    import urllib3
    urllib3.disable_warnings()
    
    try:
        res = requests.get(url, headers=headers, verify=False, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        jobs = []
        # Find table rows inside the main content
        rows = soup.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) > 0:
                text = row.text.strip().replace('\n', ' ')
                
                # Check for advertisement links
                advt_link = row.find('a', href=re.compile(r'adv', re.IGNORECASE))
                pdf_link = row.find('a', href=re.compile(r'\.pdf', re.IGNORECASE))
                apply_link = row.find('a', href=re.compile(r'apply', re.IGNORECASE))
                
                target_link = advt_link or pdf_link or apply_link
                if target_link:
                    href = target_link.get('href')
                    if not href.startswith('http'):
                        href = url.rstrip('/') + '/' + href.lstrip('/')
                        
                    # Clean up title (get first column or bold text)
                    title = ""
                    b_tag = row.find('b')
                    if b_tag:
                        title = b_tag.text.strip()
                    elif len(cols) >= 2:
                        title = cols[1].text.strip()
                    else:
                        title = text[:80]
                        
                    title = title.replace('\r', '').replace('\n', '').strip()
                    if len(title) > 5 and title not in [j['title'] for j in jobs]:
                        jobs.append({
                            "title": title,
                            "location": "All India",
                            "url": href.strip()
                        })
                        
        print(f"Extracted {len(jobs)} NTPC notices.")
        
        # Filter generic ones
        filtered = [j for j in jobs if 'detailed adv' in j['title'].lower() or 'empanelment' in j['title'].lower() or 'recruitment' in j['title'].lower() or 'advertisement' in j['title'].lower()]
        if not filtered and jobs:
            filtered = jobs
            
        # Write review artifact
        artifact_path = "C:/Users/Ahana Singh/.gemini/antigravity/brain/b2157c5e-32e9-4e58-993a-3a6a43a0d53a/ntpc_review.md"
        content = f"""# NTPC Job Extraction Review

## Extraction Summary
- **Target Company:** NTPC (National Thermal Power Corporation)
- **Total Openings Found:** {len(filtered)}
- **Locations Filtered:** India
- **Platform:** Direct PSU PHP Portal

## Verification Status
NTPC publishes single, massive PDF advertisements for their hiring drives (e.g., "Recruitment of Executive Trainees"). 

### Extracted Openings (Sample):
"""
        for j in filtered[:5]:
            content += f"- **{j['title']}** - [View Notice]({j['url']})\n"

        content += """
    
## Approval Required
Please review the notices above. Do you want to ingest these PSU notices into the database? 
Respond with **"Approve ingestion for NTPC"** to proceed.
"""

        with open(artifact_path, "w") as f:
            f.write(content)
        
        print("Artifact generated.")
        
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    fetch_ntpc()
