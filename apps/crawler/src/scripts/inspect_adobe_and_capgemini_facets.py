import os
import sys
import json
import time
import requests
from playwright.sync_api import sync_playwright

print("=" * 80)
print("INSPECTING OFFICIAL ADOBE WORKDAY & CAPGEMINI UI FACETS")
print("=" * 80, flush=True)

# ----------------------------------------------------
# 1. ADOBE WORKDAY OFFICIAL JOB FAMILIES
# ----------------------------------------------------
print("\n[1] Inspecting Adobe Workday Job Family Facets for India...", flush=True)
try:
    url = "https://adobe.wd5.myworkdayjobs.com/wday/cxs/adobe/external_experienced/jobs"
    payload = {
        "appliedFacets": {},
        "limit": 1,
        "offset": 0,
        "searchText": "India"
    }
    res = requests.post(url, json=payload, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
    if res.ok:
        d = res.json()
        print(f"Total Adobe India Search Results: {d.get('total')}")
        facets = d.get('facets', [])
        for facet in facets:
            facet_id = facet.get('facetParameter')
            vals = facet.get('values', [])
            if any(f in str(facet_id).lower() for f in ['jobfamily', 'job_family', 'category', 'department', 'team']):
                print(f"\nAdobe Facet: {facet_id} ({len(vals)} categories):")
                for v in vals[:15]:
                    print(f"  • {v.get('descriptor')}: {v.get('count')} jobs (ID: {v.get('id')})")
except Exception as e:
    print(f"Adobe facet err: {e}")

# ----------------------------------------------------
# 2. CAPGEMINI UI LOCATION COUNTS
# ----------------------------------------------------
print("\n[2] Inspecting Capgemini India UI Location Facets...", flush=True)
try:
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        page = browser.new_page()
        page.goto("https://www.capgemini.com/in-en/careers/job-search/?country_code=in-en", wait_until='networkidle', timeout=30000)
        time.sleep(3)

        # Get Capgemini location facet values from the DOM / API
        cap_facets = page.evaluate("""() => {
            const locSelect = document.querySelector('select[name*="location"], select[id*="location"], [data-filter="location"]');
            const options = locSelect ? Array.from(locSelect.options).map(o => ({ text: o.text.trim(), val: o.value })) : [];
            
            const totalText = document.querySelector('[class*="results-count"], [class*="total"], h2, h3')?.innerText || '';
            
            return {
                options,
                totalText
            };
        }""")
        print("Capgemini UI Dropdown Options:", json.dumps(cap_facets['options'][:20], indent=2))

        # Also let's test direct search for Hyderabad
        page.goto("https://www.capgemini.com/in-en/careers/job-search/?country_code=in-en&location=Hyderabad", wait_until='networkidle', timeout=20000)
        time.sleep(2)
        hyd_count = page.evaluate("""() => {
            const cards = Array.from(document.querySelectorAll('a[href*="/job-search/"]')).filter(a => a.querySelector('h3, h2, div'));
            const text = document.body.innerText;
            const match = text.match(/(\\d+)\\s*(?:jobs|results|positions|openings)/i);
            return {
                cardsOnPage: cards.length,
                matchedText: match ? match[0] : 'No match found'
            };
        }""")
        print(f"Capgemini Hyderabad UI Search Result: {hyd_count}")

        browser.close()
except Exception as e:
    print(f"Capgemini UI err: {e}")

print("\n" + "=" * 80)
