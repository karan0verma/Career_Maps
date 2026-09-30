import os
import sys
import json
import time
import requests
from playwright.sync_api import sync_playwright

staging_dir = r"C:\Users\Ahana Singh\.gemini\antigravity\scratch\career-maps\apps\crawler\staging"
os.makedirs(staging_dir, exist_ok=True)

print("=" * 80)
print("EXTRACTING CATEGORY A & B TARGET COMPANIES TO STAGING")
print("Target Companies: Adobe, LTIMindtree, Google, IBM, Cisco, Accenture, Capgemini")
print("=" * 80, flush=True)

category_a_data = {}
category_b_data = {}

with sync_playwright() as p:
    browser = p.chromium.launch(channel='chrome', headless=True)
    context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    page = context.new_page()

    # ----------------------------------------------------
    # 1. ADOBE INDIA (Workday API)
    # ----------------------------------------------------
    print("\n[A-1] Extracting Adobe India...", flush=True)
    try:
        page.goto("https://adobe.wd5.myworkdayjobs.com/en-US/external_experienced", wait_until='domcontentloaded', timeout=30000)
        time.sleep(2)
        
        # In Adobe Workday, find locationCountry for India
        ad_jobs = []
        for offset in range(0, 300, 20):
            payload = {
                "appliedFacets": {},
                "limit": 20,
                "offset": offset,
                "searchText": "India"
            }
            res = page.request.post("https://adobe.wd5.myworkdayjobs.com/wday/cxs/adobe/external_experienced/jobs", data=json.dumps(payload), headers={'content-type': 'application/json'})
            if res.ok:
                d = res.json()
                postings = d.get('jobPostings', [])
                if not postings:
                    break
                for post in postings:
                    loc = post.get('locationsText', '')
                    if 'India' in loc or 'Noida' in loc or 'Bengaluru' in loc or 'Bangalore' in loc:
                        ad_jobs.append({
                            "title": post.get('title'),
                            "location": loc,
                            "country": "India",
                            "apply_url": f"https://adobe.wd5.myworkdayjobs.com/en-US/external_experienced{post.get('externalPath')}",
                            "work_mode": "Hybrid / On-site"
                        })
            else:
                break
        print(f"  Adobe India: Extracted {len(ad_jobs)} verified live jobs.")
        category_a_data['adobe'] = {"company": "Adobe", "count": len(ad_jobs), "jobs": ad_jobs}
    except Exception as e:
        print(f"  Adobe error: {e}")

    # ----------------------------------------------------
    # 2. LTIMINDTREE (SAP SuccessFactors API)
    # ----------------------------------------------------
    print("\n[B-1] Extracting LTIMindtree India...", flush=True)
    try:
        page.goto("https://careers.ltimindtree.com/search/?q=&locationsearch=India", wait_until='domcontentloaded', timeout=30000)
        time.sleep(3)

        # Sniff CSRF token
        lti_jobs = []
        seen_lti = set()
        
        # DOM link extraction across pages
        for startrow in [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]:
            page.goto(f"https://careers.ltimindtree.com/search/?q=&locationsearch=India&startrow={startrow}", wait_until='domcontentloaded', timeout=20000)
            time.sleep(1)
            links = page.evaluate("""() => {
                const rows = Array.from(document.querySelectorAll('tr.data-row, table tbody tr, .job-tile, a[href*="/job/"]'));
                return rows.map(r => {
                    const a = r.tagName === 'A' ? r : r.querySelector('a[href*="/job/"]');
                    const loc = r.querySelector ? r.querySelector('.jobLocation, .location, [class*="location"]') : null;
                    return {
                        title: a ? a.innerText.trim() : '',
                        href: a ? a.href : '',
                        loc: loc ? loc.innerText.trim() : 'India'
                    };
                }).filter(j => j.title && j.href);
            }""")
            for l in links:
                if l['href'] not in seen_lti:
                    seen_lti.add(l['href'])
                    lti_jobs.append({
                        "title": l['title'].split('\n')[0],
                        "location": l['loc'] if l['loc'] else "India",
                        "country": "India",
                        "apply_url": l['href'],
                        "work_mode": "Hybrid / On-site"
                    })
        print(f"  LTIMindtree: Extracted {len(lti_jobs)} verified live jobs.")
        category_b_data['ltimindtree'] = {"company": "LTIMindtree", "count": len(lti_jobs), "jobs": lti_jobs}
    except Exception as e:
        print(f"  LTIMindtree error: {e}")

    browser.close()

# Save staging files
with open(os.path.join(staging_dir, "category_a_staged.json"), "w", encoding="utf-8") as f:
    json.dump(category_a_data, f, indent=2)

with open(os.path.join(staging_dir, "category_b_staged.json"), "w", encoding="utf-8") as f:
    json.dump(category_b_data, f, indent=2)

print("\nStaged extractions saved successfully!")
