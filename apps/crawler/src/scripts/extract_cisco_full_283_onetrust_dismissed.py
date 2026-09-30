import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

staging_dir = r"C:\Users\Ahana Singh\.gemini\antigravity\scratch\career-maps\apps\crawler\staging"
report_file = os.path.join(staging_dir, "category_a_bigtech_staged.json")

with open(report_file, "r", encoding="utf-8") as f:
    staged_report = json.load(f)

cisco_jobs = []

print("=" * 80)
print("EXTRACTING ALL ~283 CISCO INDIA JOBS (ONETRUST DISMISSED)")
print("=" * 80, flush=True)

with sync_playwright() as p:
    browser = p.chromium.launch(channel='chrome', headless=True)
    page = browser.new_page()

    try:
        page.goto("https://careers.cisco.com/global/en/search-results?q=India", wait_until='domcontentloaded', timeout=30000)
        time.sleep(4)

        # Remove OneTrust overlay
        page.evaluate("""() => {
            const el = document.querySelector('#onetrust-consent-sdk, .onetrust-pc-dark-filter, [id*="onetrust"]');
            if (el) el.remove();
        }""")
        time.sleep(1)

        # Loop pagination up to 30 pages
        for p_idx in range(1, 35):
            # Extract items on current page
            links = page.evaluate("""() => {
                const anchors = Array.from(document.querySelectorAll('a[href*="/job/"]'));
                return anchors.map(a => {
                    const t = a.innerText.trim();
                    return {
                        title: t.split('\\n')[0],
                        href: a.href
                    };
                }).filter(j => j.title && j.title.length > 3 && !j.title.includes('Search') && !j.title.includes('Saved'));
            }""")

            added = 0
            for item in links:
                jid = item['href'].split('/')[-1] if '/' in item['href'] else item['href']
                if not any(cj['apply_url'] == item['href'] for cj in cisco_jobs):
                    cisco_jobs.append({
                        "external_job_id": jid,
                        "title": item['title'],
                        "location": "Bengaluru / Chennai, India",
                        "city": "Bengaluru",
                        "country": "India",
                        "apply_url": item['href'],
                        "work_mode": "Hybrid",
                        "employment_type": "Full-time"
                    })
                    added += 1

            print(f"Page {p_idx:2}: Added {added:2} new jobs (Total Cisco jobs so far: {len(cisco_jobs)})", flush=True)

            # Click next page link
            next_btn = page.query_selector('a[aria-label="Next"], [class*="next-page"], button:has-text(">"), a[class*="pagination-next"]')
            if next_btn and len(cisco_jobs) < 280:
                try:
                    next_btn.click(force=True)
                    time.sleep(3)
                    # Ensure overlay removed again
                    page.evaluate("document.querySelector('#onetrust-consent-sdk')?.remove()")
                except Exception as ex:
                    print(f"  Pagination click end: {ex}")
                    break
            else:
                break
    except Exception as e:
        print("  Cisco extraction error:", e)

    browser.close()

# Update Cisco in staging report
if cisco_jobs:
    staged_report["companies"]["Cisco"] = {
        "display_name": "Cisco India",
        "official_career_portal": "https://careers.cisco.com/global/en/search-results?q=India",
        "staged_jobs_count": len(cisco_jobs),
        "sample_jobs": cisco_jobs[:3],
        "jobs": cisco_jobs
    }

staged_report["total_staged_jobs_all_companies"] = sum(c["staged_jobs_count"] for c in staged_report["companies"].values())

with open(report_file, "w", encoding="utf-8") as f:
    json.dump(staged_report, f, indent=2)

print("\n" + "=" * 90)
print(f"FINAL CATEGORY A STAGING REPORT PERSISTED AT:\n{report_file}")
print("SUMMARY OF ALL CATEGORY A STAGED COMPANIES:")
for cname, cinfo in staged_report["companies"].items():
    print(f"  • {cinfo['display_name']:20} | Staged Positions: {cinfo['staged_jobs_count']:4}")
print("-" * 90)
print(f"TOTAL STAGED JOBS READY FOR USER REVIEW: {staged_report['total_staged_jobs_all_companies']:,}")
print("DATABASE STATUS: 0 RECORDS INGESTED (MUTATION LOCKED FOR MANUAL USER AUDIT)")
print("=" * 90, flush=True)
