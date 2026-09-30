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

print("Extracting Cisco India via Playwright pagination click...", flush=True)

with sync_playwright() as p:
    browser = p.chromium.launch(channel='chrome', headless=True)
    page = browser.new_page()

    try:
        page.goto("https://jobs.cisco.com/jobs/SearchJobs/India", wait_until='networkidle', timeout=30000)
        time.sleep(4)

        for p_idx in range(1, 20):
            # Extract links on current page
            links = page.evaluate("""() => {
                const anchors = Array.from(document.querySelectorAll('a[href*="/jobs/ProjectDetail/"]'));
                return anchors.map(a => ({
                    title: a.innerText.trim(),
                    href: a.href
                })).filter(j => j.title && j.title.length > 3);
            }""")

            added_on_page = 0
            for item in links:
                jid = item['href'].split('/')[-1]
                if not any(cj['apply_url'] == item['href'] for cj in cisco_jobs):
                    cisco_jobs.append({
                        "external_job_id": jid,
                        "title": item['title'].split('\n')[0],
                        "location": "Bengaluru, India",
                        "city": "Bengaluru",
                        "country": "India",
                        "apply_url": item['href'],
                        "work_mode": "Hybrid",
                        "employment_type": "Full-time"
                    })
                    added_on_page += 1

            print(f"Page {p_idx}: Extracted {added_on_page} new jobs. Total Cisco jobs so far: {len(cisco_jobs)}", flush=True)

            # Try clicking page number (e.g. "2", "3", "4"...) or Next button
            page_btn = page.query_selector(f'a:has-text("{p_idx + 1}"), button:has-text("{p_idx + 1}")')
            if not page_btn:
                page_btn = page.query_selector('a[title*="Next"], a:has-text(">"), a:has-text("Next")')

            if page_btn and added_on_page > 0:
                try:
                    page_btn.click()
                    time.sleep(3)
                except Exception as ex:
                    print(f"Click page {p_idx + 1} err:", ex)
                    break
            else:
                break
    except Exception as e:
        print("Cisco pagination error:", e)

    browser.close()

if cisco_jobs:
    staged_report["companies"]["Cisco"] = {
        "display_name": "Cisco India",
        "official_career_portal": "https://jobs.cisco.com/jobs/SearchJobs/India",
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
