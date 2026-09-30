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
google_jobs = []

with sync_playwright() as p:
    browser = p.chromium.launch(channel='chrome', headless=True)
    page = browser.new_page()

    # Cisco
    print("Debug Cisco DOM...", flush=True)
    try:
        page.goto("https://jobs.cisco.com/jobs/SearchJobs/India", wait_until='load', timeout=30000)
        time.sleep(5)
        # Check if iframe exists
        iframes = page.frames
        print("Cisco frames count:", len(iframes))
        
        for frame in iframes:
            try:
                links = frame.evaluate("""() => Array.from(document.querySelectorAll('a')).map(a => ({ title: a.innerText.trim(), href: a.href })).filter(j => j.title && j.href.includes('jobs'))""")
                if links:
                    print(f"Frame {frame.url} found {len(links)} job links!")
                    for idx, l in enumerate(links):
                        jid = l['href'].split('/')[-1] if '/' in l['href'] else str(idx + 1)
                        if not any(cj['external_job_id'] == jid for cj in cisco_jobs):
                            cisco_jobs.append({
                                "external_job_id": jid,
                                "title": l['title'].split('\n')[0],
                                "location": "Bengaluru, India",
                                "city": "Bengaluru",
                                "country": "India",
                                "apply_url": l['href'],
                                "work_mode": "Hybrid",
                                "employment_type": "Full-time"
                            })
            except:
                pass
    except Exception as e:
        print("Cisco err:", e)

    # Google
    print("Debug Google DOM...", flush=True)
    try:
        page.goto("https://www.google.com/about/careers/applications/jobs/results/?location=India", wait_until='load', timeout=30000)
        time.sleep(5)
        g_links = page.evaluate("""() => {
            const anchors = Array.from(document.querySelectorAll('a'));
            return anchors.map(a => ({ title: a.innerText.trim(), href: a.href })).filter(j => j.href.includes('jobs/results') || (j.title && j.title.length > 5 && !j.title.includes('Search')));
        }""")
        print("Google links count:", len(g_links))
        for idx, g in enumerate(g_links):
            jid = g['href'].split('/')[-1] if '/' in g['href'] else str(idx + 1)
            if not any(gj['external_job_id'] == jid for gj in google_jobs):
                google_jobs.append({
                    "external_job_id": jid,
                    "title": g['title'].split('\n')[0],
                    "location": "Bengaluru / Hyderabad, India",
                    "city": "Bengaluru",
                    "country": "India",
                    "apply_url": g['href'],
                    "work_mode": "On-site / Hybrid",
                    "employment_type": "Full-time"
                })
    except Exception as e:
        print("Google err:", e)

    browser.close()

if cisco_jobs:
    staged_report["companies"]["Cisco"] = {
        "display_name": "Cisco India",
        "official_career_portal": "https://jobs.cisco.com/jobs/SearchJobs/India",
        "staged_jobs_count": len(cisco_jobs),
        "sample_jobs": cisco_jobs[:3],
        "jobs": cisco_jobs
    }

if google_jobs:
    staged_report["companies"]["Google"] = {
        "display_name": "Google India",
        "official_career_portal": "https://careers.google.com/jobs/results/?location=India",
        "staged_jobs_count": len(google_jobs),
        "sample_jobs": google_jobs[:3],
        "jobs": google_jobs
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
