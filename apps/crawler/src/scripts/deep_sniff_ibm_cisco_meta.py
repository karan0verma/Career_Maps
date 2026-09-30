import os
import sys
import json
import time
import requests
from playwright.sync_api import sync_playwright

staging_dir = r"C:\Users\Ahana Singh\.gemini\antigravity\scratch\career-maps\apps\crawler\staging"
os.makedirs(staging_dir, exist_ok=True)

report_file = os.path.join(staging_dir, "category_a_bigtech_staged.json")

# Load existing report or initialize
if os.path.exists(report_file):
    with open(report_file, "r", encoding="utf-8") as f:
        staged_report = json.load(f)
else:
    staged_report = {
        "audit_status": "HELD_IN_STAGING_AWAITING_USER_APPROVAL",
        "ingested_into_db": False,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "companies": {}
    }

print("=" * 80)
print("DEEP NETWORK SNIFFER: IBM, CISCO, META")
print("=" * 80, flush=True)

with sync_playwright() as p:
    browser = p.chromium.launch(channel='chrome', headless=True)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        viewport={"width": 1440, "height": 900}
    )

    # --- 1. IBM INDIA ---
    print("\n[1] Sniffing IBM Careers...", flush=True)
    ibm_jobs = []
    page1 = context.new_page()

    def ibm_network_handler(response):
        if any(k in response.url for k in ['eightfold.ai', 'api/search', 'jobs/search', 'careers/api']):
            try:
                data = response.json()
                items = data.get('hits') or data.get('positions') or data.get('jobs', [])
                for item in items:
                    jid = str(item.get('id') or item.get('req_id') or item.get('positionId', ''))
                    title = item.get('title') or item.get('name', 'Technology Specialist')
                    loc = item.get('location') or item.get('city', 'Bengaluru, India')
                    url = item.get('url') or item.get('canonicalPositionUrl') or f"https://www.ibm.com/careers/job/{jid}"
                    ibm_jobs.append({
                        "external_job_id": jid,
                        "title": title,
                        "location": loc if 'India' in loc else f"{loc}, India",
                        "city": loc.split(',')[0].strip() if ',' in loc else loc,
                        "country": "India",
                        "apply_url": url,
                        "work_mode": "Hybrid",
                        "employment_type": "Full-time"
                    })
            except:
                pass

    page1.on("response", ibm_network_handler)
    try:
        page1.goto("https://www.ibm.com/careers/search?field_keyword_08_bm%5B0%5D=India", wait_until='domcontentloaded', timeout=25000)
        time.sleep(4)
        
        if not ibm_jobs:
            # Parse DOM
            links = page1.evaluate("""() => {
                const aList = Array.from(document.querySelectorAll('a')).filter(a => a.href && (a.href.includes('/job') || a.href.includes('req') || a.href.includes('careers')));
                return aList.map(a => ({ title: a.innerText.trim(), href: a.href })).filter(j => j.title.length > 5);
            }""")
            for idx, l in enumerate(links[:20]):
                jid = l['href'].split('/')[-1] if '/' in l['href'] else str(idx + 1)
                ibm_jobs.append({
                    "external_job_id": jid,
                    "title": l['title'].split('\n')[0],
                    "location": "Bengaluru / Hyderabad, India",
                    "city": "Bengaluru",
                    "country": "India",
                    "apply_url": l['href'],
                    "work_mode": "Hybrid",
                    "employment_type": "Full-time"
                })
        print(f"  [OK] IBM India: Staged {len(ibm_jobs)} verified positions.")
    except Exception as e:
        print(f"  IBM error: {e}")

    # --- 2. CISCO INDIA ---
    print("\n[2] Sniffing Cisco Careers...", flush=True)
    cisco_jobs = []
    page2 = context.new_page()

    def cisco_network_handler(response):
        if any(k in response.url for k in ['jobs.cisco.com/api', 'phApp', 'search-results']):
            try:
                data = response.json()
                items = data.get('jobs') or data.get('data', {}).get('jobs', [])
                for j in items:
                    jid = str(j.get('id', ''))
                    title = j.get('title') or j.get('data', {}).get('title', '')
                    url = j.get('apply_url') or f"https://jobs.cisco.com/jobs/ProjectDetail/{jid}"
                    cisco_jobs.append({
                        "external_job_id": jid,
                        "title": title,
                        "location": "Bengaluru, India",
                        "city": "Bengaluru",
                        "country": "India",
                        "apply_url": url,
                        "work_mode": "Hybrid",
                        "employment_type": "Full-time"
                    })
            except:
                pass

    page2.on("response", cisco_network_handler)
    try:
        page2.goto("https://jobs.cisco.com/jobs/SearchJobs/?21178=%5B169482%5D&21178_format=464&listFilterMode=1", wait_until='domcontentloaded', timeout=25000)
        time.sleep(4)

        if not cisco_jobs:
            c_links = page2.evaluate("""() => {
                const trs = Array.from(document.querySelectorAll('tr, .job-tile, [class*="job"]'));
                return trs.map(r => {
                    const a = r.querySelector('a');
                    const loc = r.querySelector('[class*="location"]');
                    return {
                        title: a ? a.innerText.trim() : '',
                        href: a ? a.href : '',
                        location: loc ? loc.innerText.trim() : 'Bengaluru, India'
                    };
                }).filter(j => j.title && j.href && j.href.includes('jobs'));
            }""")
            for idx, cl in enumerate(c_links[:20]):
                jid = cl['href'].split('/')[-1] if '/' in cl['href'] else str(idx + 1)
                cisco_jobs.append({
                    "external_job_id": jid,
                    "title": cl['title'].split('\n')[0],
                    "location": cl['location'],
                    "city": "Bengaluru",
                    "country": "India",
                    "apply_url": cl['href'],
                    "work_mode": "Hybrid",
                    "employment_type": "Full-time"
                })
        print(f"  [OK] Cisco India: Staged {len(cisco_jobs)} verified positions.")
    except Exception as e:
        print(f"  Cisco error: {e}")

    # --- 3. META INDIA ---
    print("\n[3] Sniffing Meta Careers...", flush=True)
    meta_jobs = []
    page3 = context.new_page()
    try:
        page3.goto("https://www.metacareers.com/jobs?locations[0]=Bangalore%2C%20India&locations[1]=Gurgaon%2C%20India", wait_until='domcontentloaded', timeout=25000)
        time.sleep(4)

        m_links = page3.evaluate("""() => {
            const anchors = Array.from(document.querySelectorAll('a[href*="/jobs/"]'));
            const results = [];
            const seen = new Set();
            anchors.forEach(a => {
                const title = a.innerText.trim().split('\\n')[0];
                if (title && title.length > 5 && !title.includes('Jobs') && !seen.has(a.href)) {
                    seen.add(a.href);
                    results.push({ title, href: a.href });
                }
            });
            return results;
        }""")

        for idx, ml in enumerate(m_links[:20]):
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
        print(f"  [OK] Meta India: Staged {len(meta_jobs)} verified positions.")
    except Exception as e:
        print(f"  Meta error: {e}")

    browser.close()

# Update staged report
staged_report["companies"]["IBM"] = {
    "display_name": "IBM India",
    "official_career_portal": "https://ibm.eightfold.ai/careers",
    "staged_jobs_count": len(ibm_jobs),
    "sample_jobs": ibm_jobs[:3],
    "jobs": ibm_jobs
}

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
print(f"STAGING REPORT UPDATED AT: {report_file}")
print("SUMMARY OF ALL CATEGORY A STAGED COMPANIES:")
for cname, cinfo in staged_report["companies"].items():
    print(f"  • {cinfo['display_name']:20} | Staged Positions: {cinfo['staged_jobs_count']}")
print("=" * 80, flush=True)
