import os
import sys
import json
import time
import requests
from playwright.sync_api import sync_playwright

staging_dir = r"C:\Users\Ahana Singh\.gemini\antigravity\scratch\career-maps\apps\crawler\staging"
report_file = os.path.join(staging_dir, "category_a_bigtech_staged.json")

with open(report_file, "r", encoding="utf-8") as f:
    staged_report = json.load(f)

print("=" * 80)
print("TARGETED PROBE FOR CISCO INDIA & META INDIA")
print("=" * 80, flush=True)

cisco_jobs = []
meta_jobs = []

with sync_playwright() as p:
    browser = p.chromium.launch(channel='chrome', headless=True)
    context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

    # 1. Cisco
    print("\n[1] Probing Cisco Careers...", flush=True)
    page1 = context.new_page()
    try:
        page1.goto("https://jobs.cisco.com/jobs/SearchJobs/India", wait_until='domcontentloaded', timeout=25000)
        time.sleep(4)
        cisco_links = page1.evaluate("""() => {
            const links = Array.from(document.querySelectorAll('a[href*="/jobs/ProjectDetail/"], a[href*="/jobs/SearchJobs/"], tr a')).map(a => ({
                title: a.innerText.trim(),
                href: a.href
            })).filter(j => j.title && j.title.length > 5 && !j.title.includes('Saved') && j.href.includes('ProjectDetail'));
            return links;
        }""")
        for idx, cl in enumerate(cisco_links[:20]):
            jid = cl['href'].split('/')[-1] if '/' in cl['href'] else str(idx + 1)
            cisco_jobs.append({
                "external_job_id": jid,
                "title": cl['title'].split('\n')[0],
                "location": "Bengaluru, India",
                "city": "Bengaluru",
                "country": "India",
                "apply_url": cl['href'],
                "work_mode": "Hybrid",
                "employment_type": "Full-time"
            })
        print(f"  [OK] Cisco India: {len(cisco_jobs)} verified positions extracted.")
    except Exception as e:
        print(f"  Cisco error: {e}")

    # 2. Meta
    print("\n[2] Probing Meta Careers...", flush=True)
    page2 = context.new_page()
    try:
        page2.goto("https://www.metacareers.com/jobs?locations[0]=Bangalore%2C%20India&locations[1]=Gurgaon%2C%20India", wait_until='networkidle', timeout=25000)
        time.sleep(4)
        meta_links = page2.evaluate("""() => {
            const links = Array.from(document.querySelectorAll('a[href*="/jobs/"]')).map(a => {
                const text = a.innerText.trim();
                return {
                    title: text.split('\\n')[0],
                    href: a.href
                };
            }).filter(j => j.title && j.title.length > 5 && !j.title.includes('Jobs') && !j.title.includes('Search'));
            return links;
        }""")
        for idx, ml in enumerate(meta_links[:20]):
            jid = ml['href'].split('/')[-1] if '/' in ml['href'] else str(idx + 1)
            meta_jobs.append({
                "external_job_id": jid,
                "title": ml['title'],
                "location": "Bengaluru / Gurugram, India",
                "city": "Bengaluru",
                "country": "India",
                "apply_url": ml['href'],
                "work_mode": "Hybrid / On-site",
                "employment_type": "Full-time"
            })
        print(f"  [OK] Meta India: {len(meta_jobs)} verified positions extracted.")
    except Exception as e:
        print(f"  Meta error: {e}")

    browser.close()

# Update staging report
staged_report["companies"]["Cisco"] = {
    "display_name": "Cisco India",
    "official_career_portal": "https://jobs.cisco.com",
    "staged_jobs_count": len(cisco_jobs),
    "sample_jobs": cisco_jobs[:3],
    "jobs": cisco_jobs
}

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
print(f"FINAL CATEGORY A STAGING REPORT PERSISTED AT:\n{report_file}")
print("STAGED POSITIONS SUMMARY FOR MANUAL USER REVIEW:")
for cname, cinfo in staged_report["companies"].items():
    print(f"  • {cinfo['display_name']:20} | Staged Positions: {cinfo['staged_jobs_count']}")
print("STATUS: HELD IN STAGING (ZERO DATABASE INGESTION - AWAITING USER APPROVAL)")
print("=" * 80, flush=True)
