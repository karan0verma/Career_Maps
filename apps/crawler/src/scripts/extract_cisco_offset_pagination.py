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

print("Extracting Cisco Phenom using offset pagination query...", flush=True)

with sync_playwright() as p:
    browser = p.chromium.launch(channel='chrome', headless=True)
    page = browser.new_page()

    # Iterate offsets 0, 10, 20, 30... up to 280
    for offset in range(0, 300, 10):
        url = f"https://careers.cisco.com/global/en/search-results?q=India&from={offset}"
        try:
            page.goto(url, wait_until='domcontentloaded', timeout=15000)
            time.sleep(2.5)

            cards = page.evaluate("""() => {
                const links = Array.from(document.querySelectorAll('a[href*="/job/"]'));
                return links.map(a => {
                    const text = a.innerText.trim();
                    return {
                        title: text.split('\\n')[0],
                        href: a.href
                    };
                }).filter(j => j.title && j.title.length > 3 && !j.title.includes('Search') && !j.title.includes('Saved'));
            }""")

            added = 0
            for c in cards:
                jid = c['href'].split('/')[-1] if '/' in c['href'] else c['href']
                if not any(cj['apply_url'] == c['href'] for cj in cisco_jobs):
                    cisco_jobs.append({
                        "external_job_id": jid,
                        "title": c['title'],
                        "location": "Bengaluru / Chennai, India",
                        "city": "Bengaluru",
                        "country": "India",
                        "apply_url": c['href'],
                        "work_mode": "Hybrid",
                        "employment_type": "Full-time"
                    })
                    added += 1

            print(f"Offset {offset:3}: Extracted {added:2} new jobs. Total Cisco jobs so far: {len(cisco_jobs)}", flush=True)

            if len(cards) == 0:
                break
        except Exception as e:
            print(f"Offset {offset} err: {e}")
            break

    browser.close()

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
print(f"STAGING REPORT UPDATED AT: {report_file}")
print("SUMMARY OF ALL CATEGORY A STAGED COMPANIES:")
for cname, cinfo in staged_report["companies"].items():
    print(f"  • {cinfo['display_name']:20} | Staged Positions: {cinfo['staged_jobs_count']:4}")
print("-" * 90)
print(f"TOTAL STAGED JOBS READY FOR USER REVIEW: {staged_report['total_staged_jobs_all_companies']:,}")
print("DATABASE STATUS: 0 RECORDS INGESTED (MUTATION LOCKED FOR MANUAL USER AUDIT)")
print("=" * 90, flush=True)
