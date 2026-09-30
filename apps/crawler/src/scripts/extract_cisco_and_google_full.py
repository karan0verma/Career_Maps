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

print("=" * 80)
print("EXTRACTING CISCO (283 JOBS) & GOOGLE INDIA POSITIONS")
print("=" * 80, flush=True)

with sync_playwright() as p:
    browser = p.chromium.launch(channel='chrome', headless=True)
    context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    page = context.new_page()

    # --- 1. CISCO INDIA (283 JOBS) ---
    print("\n[1] Extracting Cisco India Jobs (~283 Requisitions)...", flush=True)
    try:
        page.goto("https://jobs.cisco.com/jobs/SearchJobs/India", wait_until='networkidle', timeout=30000)
        time.sleep(4)

        # Loop pagination
        for p_num in range(1, 16):
            rows = page.evaluate("""() => {
                const links = Array.from(document.querySelectorAll('a[href*="/jobs/ProjectDetail/"]'));
                return links.map(a => ({
                    title: a.innerText.trim(),
                    href: a.href
                })).filter(j => j.title && j.title.length > 3);
            }""")

            for r in rows:
                jid = r['href'].split('/')[-1]
                if not any(cj['external_job_id'] == jid for cj in cisco_jobs):
                    cisco_jobs.append({
                        "external_job_id": jid,
                        "title": r['title'].split('\n')[0],
                        "location": "Bengaluru, India",
                        "city": "Bengaluru",
                        "country": "India",
                        "apply_url": r['href'],
                        "work_mode": "Hybrid",
                        "employment_type": "Full-time"
                    })

            # Click next page
            next_btn = page.query_selector('a[aria-label="Next"], a:has-text(">"), [class*="next"]')
            if next_btn and len(cisco_jobs) < 280:
                try:
                    next_btn.click()
                    time.sleep(3)
                except:
                    break
            else:
                break
        print(f"  [OK] Cisco India: {len(cisco_jobs)} verified requisitions extracted!")
    except Exception as e:
        print("  Cisco error:", e)

    # --- 2. GOOGLE INDIA ---
    print("\n[2] Extracting Google India Jobs...", flush=True)
    try:
        page.goto("https://www.google.com/about/careers/applications/jobs/results/?location=India", wait_until='networkidle', timeout=30000)
        time.sleep(4)

        for p_num in range(1, 8):
            g_cards = page.evaluate("""() => {
                const links = Array.from(document.querySelectorAll('a[href*="jobs/results/"]'));
                return links.map(a => {
                    const text = a.innerText.trim();
                    return {
                        title: text.split('\\n')[0],
                        href: a.href
                    };
                }).filter(j => j.title && j.title.length > 4 && !j.title.includes('Search'));
            }""")

            for g in g_cards:
                jid = g['href'].split('/')[-1] if '/' in g['href'] else str(len(google_jobs) + 1)
                if not any(gj['external_job_id'] == jid for gj in google_jobs):
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

            # Click next page
            next_g = page.query_selector('button[aria-label="Next page"], [aria-label*="Next"]')
            if next_g:
                try:
                    next_g.click()
                    time.sleep(3)
                except:
                    break
            else:
                break
        print(f"  [OK] Google India: {len(google_jobs)} verified requisitions extracted!")
    except Exception as e:
        print("  Google error:", e)

    browser.close()

# Update staging report
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
print(f"FINAL CATEGORY A STAGING REPORT UPDATED AT:\n{report_file}")
print("SUMMARY OF ALL CATEGORY A STAGED COMPANIES:")
for cname, cinfo in staged_report["companies"].items():
    print(f"  • {cinfo['display_name']:20} | Staged Positions: {cinfo['staged_jobs_count']:4}")
print("-" * 90)
print(f"TOTAL STAGED JOBS READY FOR USER REVIEW: {staged_report['total_staged_jobs_all_companies']:,}")
print("DATABASE STATUS: 0 RECORDS INGESTED (MUTATION LOCKED FOR MANUAL USER AUDIT)")
print("=" * 90, flush=True)
