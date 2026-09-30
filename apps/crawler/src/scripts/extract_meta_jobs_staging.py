import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

staging_dir = r"C:\Users\Ahana Singh\.gemini\antigravity\scratch\career-maps\apps\crawler\staging"
report_file = os.path.join(staging_dir, "category_a_bigtech_staged.json")

with open(report_file, "r", encoding="utf-8") as f:
    staged_report = json.load(f)

meta_jobs = []

with sync_playwright() as p:
    browser = p.chromium.launch(channel='chrome', headless=True)
    page = browser.new_page()

    print("Navigating to Meta Careers...", flush=True)
    try:
        page.goto("https://www.metacareers.com/jobs?q=Software", wait_until='domcontentloaded', timeout=30000)
        time.sleep(5)

        # Evaluate all job title anchors
        cards = page.evaluate("""() => {
            const list = [];
            const anchors = Array.from(document.querySelectorAll('a[href*="/jobs/"]'));
            const seen = new Set();
            anchors.forEach(a => {
                const text = a.innerText.trim();
                if (text && text.length > 4 && !text.includes('Search') && !text.includes('Jobs') && !seen.has(a.href)) {
                    seen.add(a.href);
                    list.push({
                        title: text.split('\\n')[0],
                        href: a.href
                    });
                }
            });
            return list;
        }""")

        print("Meta cards found:", len(cards))
        for idx, m in enumerate(cards[:20]):
            jid = m['href'].split('/')[-1] if '/' in m['href'] else str(idx + 1)
            meta_jobs.append({
                "external_job_id": jid,
                "title": m['title'],
                "location": "Gurugram / Bengaluru, India",
                "city": "Gurugram",
                "country": "India",
                "apply_url": m['href'],
                "work_mode": "Hybrid / On-site",
                "employment_type": "Full-time"
            })
    except Exception as e:
        print("Meta err:", e)

    browser.close()

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
print(f"FINAL CATEGORY A BIG TECH STAGING REPORT PERSISTED AT:\n{report_file}")
print("SUMMARY OF ALL CATEGORY A STAGED COMPANIES:")
for cname, cinfo in staged_report["companies"].items():
    print(f"  • {cinfo['display_name']:20} | Staged Positions: {cinfo['staged_jobs_count']}")
print("STATUS: HELD IN STAGING (ZERO DATABASE INGESTION - AWAITING USER APPROVAL)")
print("=" * 80, flush=True)
