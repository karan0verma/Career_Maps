import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

def inspect_ms():
    print("=" * 80)
    print("INSPECTING MICROSOFT JOBS SCHEMA & URL STRUCTURE")
    print("=" * 80, flush=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        page = context.new_page()

        page.goto('https://jobs.careers.microsoft.com/global/en/search?lc=India', wait_until='networkidle', timeout=30000)
        time.sleep(2)

        res = page.request.get("https://apply.careers.microsoft.com/api/pcsx/search?domain=microsoft.com&query=&location=India&start=0&num=10")
        data = res.json()
        positions = data.get('data', {}).get('positions', [])
        
        print(f"Fetched {len(positions)} sample Microsoft positions:")
        for idx, pos in enumerate(positions[:3]):
            print(f"\n--- Position {idx+1} ---")
            print("Keys:", list(pos.keys()))
            print("ID:", pos.get('id'))
            print("Name:", pos.get('name'))
            print("Location:", pos.get('location'))
            print("Locations list:", pos.get('locations'))
            print("Work Site / Flexibility:", pos.get('work_site'), pos.get('work_site_flexibility'), pos.get('work_location_option'))
            print("Job ID / Requisition ID:", pos.get('job_id'), pos.get('requisition_id'), pos.get('display_job_id'))
            print("Posting URL / Canonical URL:", pos.get('url'), pos.get('canonical_url'), pos.get('apply_url'))
            
            # Print all non-empty fields in this position
            print("\nAll Fields:")
            for k, v in pos.items():
                if v and not isinstance(v, (dict, list)) and len(str(v)) < 150:
                    print(f"  {k}: {v}")

        # Also let's inspect the DOM of a Microsoft job card on the search page
        dom_jobs = page.evaluate("""() => {
            const cards = Array.from(document.querySelectorAll('div[role="listitem"], a[href*="/job/"], a[href*="/share/"]'));
            return cards.map(c => ({
                text: c.innerText ? c.innerText.slice(0, 100).replace(/\\n/g, ' ') : '',
                href: c.href || c.querySelector('a')?.href || ''
            }));
        }""")
        print("\n--- DOM Job Card Hrefs from live search page ---")
        for dj in dom_jobs[:5]:
            print("  DOM Job:", dj)

        browser.close()

if __name__ == "__main__":
    inspect_ms()
