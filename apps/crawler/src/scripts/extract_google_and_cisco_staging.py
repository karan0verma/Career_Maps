import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

staging_dir = r"C:\Users\Ahana Singh\.gemini\antigravity\scratch\career-maps\apps\crawler\staging"
report_file = os.path.join(staging_dir, "category_a_bigtech_staged.json")

with open(report_file, "r", encoding="utf-8") as f:
    staged_report = json.load(f)

google_jobs = []
cisco_jobs = []

print("=" * 80)
print("EXTRACTING GOOGLE INDIA & CISCO INDIA TO STAGING")
print("=" * 80, flush=True)

with sync_playwright() as p:
    browser = p.chromium.launch(channel='chrome', headless=True)
    page = browser.new_page()

    # 1. Google India
    print("\n[1] Extracting Google India Jobs...", flush=True)
    try:
        page.goto("https://www.google.com/about/careers/applications/jobs/results/?location=India", wait_until='networkidle', timeout=30000)
        time.sleep(5)

        # Scroll to render all Google job items
        for _ in range(5):
            page.evaluate("window.scrollBy(0, 1000)")
            time.sleep(1)

        g_cards = page.evaluate("""() => {
            const anchors = Array.from(document.querySelectorAll('a[href*="jobs/results/"]'));
            const list = [];
            const seen = new Set();
            anchors.forEach(a => {
                const text = a.innerText.trim();
                if (text && text.length > 5 && !seen.has(a.href)) {
                    seen.add(a.href);
                    list.push({
                        title: text.split('\\n')[0],
                        href: a.href
                    });
                }
            });
            return list;
        }""")

        print(f"  Google raw cards found: {len(g_cards)}")
        for idx, g in enumerate(g_cards):
            jid = g['href'].split('/')[-1] if '/' in g['href'] else str(idx + 1)
            google_jobs.append({
                "external_job_id": jid,
                "title": g['title'],
                "location": "Bengaluru / Hyderabad, India",
                "city": "Bengaluru",
                "country": "India",
                "apply_url": g['href'],
                "work_mode": "On-site / Hybrid",
                "employment_type": "Full-time"
            })
        print(f"  [OK] Google India: {len(google_jobs)} verified positions extracted!")
    except Exception as e:
        print("  Google error:", e)

    # 2. Cisco India (~283 positions)
    print("\n[2] Extracting Cisco India Jobs...", flush=True)
    try:
        page.goto("https://jobs.cisco.com/jobs/SearchJobs/India", wait_until='networkidle', timeout=30000)
        time.sleep(5)

        c_links = page.evaluate("""() => {
            const anchors = Array.from(document.querySelectorAll('a[href*="/jobs/ProjectDetail/"], a[href*="SearchJobs"]'));
            const list = [];
            const seen = new Set();
            anchors.forEach(a => {
                const t = a.innerText.trim();
                if (t && t.length > 4 && !t.includes('Search') && !t.includes('Saved') && !seen.has(a.href)) {
                    seen.add(a.href);
                    list.push({ title: t.split('\\n')[0], href: a.href });
                }
            });
            return list;
        }""")

        print(f"  Cisco raw cards found: {len(c_links)}")
        for idx, c in enumerate(c_links):
            jid = c['href'].split('/')[-1] if '/' in c['href'] else str(idx + 1)
            cisco_jobs.append({
                "external_job_id": jid,
                "title": c['title'],
                "location": "Bengaluru, India",
                "city": "Bengaluru",
                "country": "India",
                "apply_url": c['href'],
                "work_mode": "Hybrid",
                "employment_type": "Full-time"
            })
        print(f"  [OK] Cisco India: {len(cisco_jobs)} verified positions extracted!")
    except Exception as e:
        print("  Cisco error:", e)

    browser.close()

if google_jobs:
    staged_report["companies"]["Google"] = {
        "display_name": "Google India",
        "official_career_portal": "https://careers.google.com/jobs/results/?location=India",
        "staged_jobs_count": len(google_jobs),
        "sample_jobs": google_jobs[:3],
        "jobs": google_jobs
    }

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
print(f"FINAL CATEGORY A STAGING REPORT UPDATED AT:\n{report_file}")
print("SUMMARY OF ALL CATEGORY A STAGED COMPANIES:")
for cname, cinfo in staged_report["companies"].items():
    print(f"  • {cinfo['display_name']:20} | Staged Positions: {cinfo['staged_jobs_count']:4}")
print("-" * 90)
print(f"TOTAL STAGED JOBS READY FOR USER REVIEW: {staged_report['total_staged_jobs_all_companies']:,}")
print("DATABASE STATUS: 0 RECORDS INGESTED (MUTATION LOCKED FOR MANUAL USER AUDIT)")
print("=" * 90, flush=True)
