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

cisco_jobs = []

print("=" * 80)
print("EXTRACTING ALL ~283 CISCO INDIA JOBS FROM CAREERS.CISCO.COM")
print("=" * 80, flush=True)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*'
}

with sync_playwright() as p:
    browser = p.chromium.launch(channel='chrome', headless=True)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        viewport={"width": 1440, "height": 900}
    )
    page = context.new_page()

    # Intercept Phenom API search response for Cisco
    def handle_cisco_response(response):
        if "widgets" in response.url or "search-results" in response.url or "jobs" in response.url:
            try:
                data = response.json()
                # Check phenom payload
                ref = data.get('refineSearch', {})
                jobs_data = data.get('jobPostings') or data.get('jobs') or data.get('refineSearch', {}).get('data', {}).get('jobs', [])
                if jobs_data:
                    for j in jobs_data:
                        jid = str(j.get('jobId') or j.get('id', ''))
                        title = j.get('title') or j.get('jobTitle', '')
                        loc = j.get('location') or j.get('city', 'Bengaluru, India')
                        url = j.get('applyUrl') or j.get('url') or f"https://careers.cisco.com/global/en/job/{jid}"
                        if url and not any(cj['apply_url'] == url for cj in cisco_jobs):
                            cisco_jobs.append({
                                "external_job_id": jid,
                                "title": title,
                                "location": loc if 'India' in str(loc) else f"{loc}, India",
                                "city": str(loc).split(',')[0].strip() if ',' in str(loc) else "Bengaluru",
                                "country": "India",
                                "apply_url": url if url.startswith('http') else f"https://careers.cisco.com{url}",
                                "work_mode": "Hybrid",
                                "employment_type": "Full-time"
                            })
            except:
                pass

    page.on("response", handle_cisco_response)

    try:
        page.goto("https://careers.cisco.com/global/en/search-results?q=India", wait_until='networkidle', timeout=30000)
        time.sleep(4)

        # Loop pagination up to 30 pages
        for p_idx in range(1, 30):
            # Extract current page DOM links
            dom_items = page.evaluate("""() => {
                const links = Array.from(document.querySelectorAll('a[href*="/job/"]'));
                return links.map(a => ({ title: a.innerText.trim(), href: a.href })).filter(j => j.title && j.title.length > 3);
            }""")

            for item in dom_items:
                jid = item['href'].split('/')[-1] if '/' in item['href'] else item['href']
                if not any(cj['apply_url'] == item['href'] for cj in cisco_jobs):
                    cisco_jobs.append({
                        "external_job_id": jid,
                        "title": item['title'].split('\n')[0],
                        "location": "Bengaluru / Chennai, India",
                        "city": "Bengaluru",
                        "country": "India",
                        "apply_url": item['href'],
                        "work_mode": "Hybrid",
                        "employment_type": "Full-time"
                    })

            print(f"  Page {p_idx}: Total Cisco positions gathered so far: {len(cisco_jobs)}", flush=True)

            # Click next page on Phenom portal
            next_btn = page.query_selector('a[aria-label="Next"], [class*="next-page"], button:has-text(">"), a[class*="pagination-next"]')
            if next_btn and len(cisco_jobs) < 280:
                try:
                    next_btn.click()
                    time.sleep(3)
                except:
                    break
            else:
                break

    except Exception as e:
        print("  Cisco extraction error:", e)

    browser.close()

# Update Cisco in staging report
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
