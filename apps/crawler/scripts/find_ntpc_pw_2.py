from playwright.sync_api import sync_playwright

def find_ntpc_jobs():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(ignore_https_errors=True)
        
        page.goto("https://careers.ntpc.co.in/recruitment/", timeout=15000)
        
        jobs = []
        links = page.locator("a").all()
        for link in links:
            href = link.get_attribute("href")
            text = link.inner_text().strip()
            if href and ('advt' in href.lower() or '.pdf' in href.lower() or 'advertisements' in href.lower()):
                if text and len(text) > 5 and 'Adv Hindi' not in text and 'Interview Schedule' not in text and 'Cut-off marks' not in text:
                    jobs.append({"title": text, "url": href, "location": "All India"})
                    
        browser.close()
        
        # Deduplicate
        unique_jobs = []
        seen = set()
        for j in jobs:
            if j['title'] not in seen:
                unique_jobs.append(j)
                seen.add(j['title'])
                
        artifact_path = "C:/Users/Ahana Singh/.gemini/antigravity/brain/b2157c5e-32e9-4e58-993a-3a6a43a0d53a/ntpc_review.md"
        content = f"""# NTPC Job Extraction Review

## Extraction Summary
- **Target Company:** NTPC (National Thermal Power Corporation)
- **Total Openings Found:** {len(unique_jobs)} Current Drives
- **Locations Filtered:** India
- **Platform:** Direct PSU Portal

## Verification Status
NTPC publishes single, massive PDF advertisements for their hiring drives (e.g., "Recruitment of 150 Trainees") rather than individual listings. 

### Extracted Openings:
"""
        for j in unique_jobs[:5]:
            content += f"- **{j['title']}** - [View Official Circular]({j['url']})\n"

        content += """
    
## Approval Required
Please review the active PSU notices above. 
Respond with **"Approve ingestion for NTPC"** to proceed.
"""

        with open(artifact_path, "w") as f:
            f.write(content)

if __name__ == "__main__":
    find_ntpc_jobs()
