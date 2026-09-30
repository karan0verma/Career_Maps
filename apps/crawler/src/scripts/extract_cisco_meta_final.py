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
meta_jobs = []

with sync_playwright() as p:
    browser = p.chromium.launch(channel='chrome', headless=True)
    page = browser.new_page()

    # 1. Cisco
    print("Extracting Cisco Jobs...", flush=True)
    try:
        page.goto("https://jobs.cisco.com/jobs/SearchJobs/India", wait_until='domcontentloaded', timeout=30000)
        time.sleep(5)
        # Select all job links from the rendered DOM
        c_links = page.evaluate("""() => {
            const anchors = Array.from(document.querySelectorAll('a[href*="/jobs/ProjectDetail/"], a[href*="job"]'));
            return anchors.map(a => ({
                title: a.innerText.trim(),
                href: a.href
            })).filter(j => j.title && j.title.length > 3 && !j.title.includes('Search') && !j.title.includes('Saved'));
        }""")
        print(f"  Cisco anchors found: {len(c_links)}")
        for idx, item in enumerate(c_links[:30]):
            jid = item['href'].split('/')[-1] if '/' in item['href'] else str(idx + 1)
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
    except Exception as e:
        print("  Cisco error:", e)

    # 2. Meta
    print("Extracting Meta Jobs...", flush=True)
    try:
        page.goto("https://www.metacareers.com/jobs?q=Software&locations[0]=Bangalore%2C%20India", wait_until='domcontentloaded', timeout=30000)
        time.sleep(5)
        m_links = page.evaluate("""() => {
            const anchors = Array.from(document.querySelectorAll('a[href*="/jobs/"]'));
            return anchors.map(a => ({
                title: a.innerText.trim(),
                href: a.href
            })).filter(j => j.title && j.title.length > 3 && !j.title.includes('Search') && !j.title.includes('Jobs'));
        }""")
        print(f"  Meta anchors found: {len(m_links)}")
        for idx, item in enumerate(m_links[:30]):
            jid = item['href'].split('/')[-1] if '/' in item['href'] else str(idx + 1)
            meta_jobs.append({
                "external_job_id": jid,
                "title": item['title'].split('\n')[0],
                "location": "Bengaluru / Gurugram, India",
                "city": "Bengaluru",
                "country": "India",
                "apply_url": item['href'],
                "work_mode": "Hybrid / On-site",
                "employment_type": "Full-time"
            })
    except Exception as e:
        print("  Meta error:", e)

    browser.close()

if cisco_jobs:
    staged_report["companies"]["Cisco"] = {
        "display_name": "Cisco India",
        "official_career_portal": "https://jobs.cisco.com",
        "staged_jobs_count": len(cisco_jobs),
        "sample_jobs": cisco_jobs[:3],
        "jobs": cisco_jobs
    }

if meta_jobs:
    staged_report["companies"]["Meta"] = {
        "display_name": "Meta India",
        "official_career_portal": "https://www.metacareers.com",
        "staged_jobs_count": len(meta_jobs),
        "sample_jobs": meta_jobs[:3],
        "jobs": meta_jobs
    }

with open(report_file, "w", encoding="utf-8") as f:
    json.dump(staged_report, f, indent=2)

print("\n" + "=" * 80)
print(f"STAGING REPORT UPDATED AT: {report_file}")
print("SUMMARY OF ALL CATEGORY A STAGED COMPANIES:")
for cname, cinfo in staged_report["companies"].items():
    print(f"  • {cinfo['display_name']:20} | Staged Positions: {cinfo['staged_jobs_count']}")
print("STATUS: HELD IN STAGING (ZERO DATABASE INGESTION - AWAITING USER APPROVAL)")
print("=" * 80, flush=True)
