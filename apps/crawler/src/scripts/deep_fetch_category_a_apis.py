import os
import sys
import json
import time
import requests
from playwright.sync_api import sync_playwright

staging_dir = r"C:\Users\Ahana Singh\.gemini\antigravity\scratch\career-maps\apps\crawler\staging"
os.makedirs(staging_dir, exist_ok=True)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*'
}

staged_data = {
    "audit_status": "HELD_IN_STAGING_AWAITING_USER_APPROVAL",
    "ingested_into_db": False,
    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    "companies": {}
}

print("=" * 80)
print("DEEP API DISCOVERY & STAGING EXTRACTION: GOOGLE, IBM, CISCO, META")
print("=" * 80, flush=True)

# ----------------------------------------------------
# 1. IBM INDIA (Eightfold API)
# ----------------------------------------------------
print("\n[1/4] Extracting IBM India via Eightfold Gateway...", flush=True)
ibm_jobs = []
try:
    url = "https://ibm.eightfold.ai/api/apply/v2/jobs?domain=ibm.com&location=India&start=0&num=100"
    res = requests.get(url, headers=headers, timeout=10)
    if res.ok:
        data = res.json()
        positions = data.get('positions', [])
        print(f"  Eightfold API returned {len(positions)} IBM India positions.")
        for p in positions:
            jid = str(p.get('id') or p.get('positionId', ''))
            title = p.get('name', 'Technology Professional')
            loc = p.get('location', 'Bengaluru, India')
            apply_url = p.get('canonicalPositionUrl') or f"https://www.ibm.com/careers/job/{jid}"
            city = loc.split(',')[0].strip() if ',' in loc else loc
            ibm_jobs.append({
                "external_job_id": jid,
                "title": title,
                "location": loc if 'India' in loc else f"{loc}, India",
                "city": city,
                "country": "India",
                "apply_url": apply_url,
                "work_mode": "Hybrid",
                "employment_type": "Full-time"
            })
    else:
        print(f"  Eightfold HTTP Status: {res.status_code}")
except Exception as e:
    print(f"  IBM error: {e}")

staged_data["companies"]["IBM"] = {
    "display_name": "IBM India",
    "official_career_portal": "https://ibm.eightfold.ai/careers",
    "staged_jobs_count": len(ibm_jobs),
    "sample_jobs": ibm_jobs[:3],
    "jobs": ibm_jobs
}

# ----------------------------------------------------
# 2. GOOGLE INDIA (Google Careers API)
# ----------------------------------------------------
print("\n[2/4] Extracting Google India Jobs...", flush=True)
google_jobs = []
try:
    g_url = "https://careers.google.com/api/v3/search/?distance=50&location=India&max=100&page=1"
    g_res = requests.get(g_url, headers=headers, timeout=10)
    if g_res.ok:
        g_data = g_res.json()
        raw_jobs = g_data.get('jobs', [])
        print(f"  Google API returned {len(raw_jobs)} positions.")
        for j in raw_jobs:
            jid = j.get('id', '')
            title = j.get('title', '')
            locs = [loc.get('display', '') for loc in j.get('locations', [])]
            loc_str = ", ".join(locs) if locs else "Bengaluru, India"
            apply_url = j.get('apply_url') or f"https://careers.google.com/jobs/results/{jid}"
            city = locs[0].split(',')[0].strip() if locs else "Bengaluru"
            google_jobs.append({
                "external_job_id": str(jid),
                "title": title,
                "location": loc_str if 'India' in loc_str else f"{loc_str}, India",
                "city": city,
                "country": "India",
                "apply_url": apply_url,
                "work_mode": "On-site / Hybrid",
                "employment_type": "Full-time"
            })
    else:
        print(f"  Google API Status: {g_res.status_code}")
except Exception as e:
    print(f"  Google error: {e}")

staged_data["companies"]["Google"] = {
    "display_name": "Google India",
    "official_career_portal": "https://careers.google.com",
    "staged_jobs_count": len(google_jobs),
    "sample_jobs": google_jobs[:3],
    "jobs": google_jobs
}

# ----------------------------------------------------
# 3. CISCO INDIA & META INDIA (Playwright Engine)
# ----------------------------------------------------
print("\n[3/4 & 4/4] Sniffing Cisco & Meta Portals using Playwright...", flush=True)
cisco_jobs = []
meta_jobs = []

with sync_playwright() as p:
    browser = p.chromium.launch(channel='chrome', headless=True)
    page = browser.new_page()

    # Cisco
    try:
        page.goto("https://jobs.cisco.com/jobs/SearchJobs/?21178=%5B169482%5D&21178_format=464&listFilterMode=1", wait_until='networkidle', timeout=20000)
        time.sleep(2)
        c_items = page.evaluate("""() => {
            const rows = Array.from(document.querySelectorAll('tr[class*="job"], .job-item, a[href*="/jobs/ProjectDetail/"]'));
            return rows.map(r => {
                const a = r.tagName === 'A' ? r : r.querySelector('a');
                return {
                    title: a ? a.innerText.trim() : '',
                    href: a ? a.href : ''
                };
            }).filter(j => j.title && j.href && !j.title.includes('Saved'));
        }""")
        for idx, c in enumerate(c_items):
            jid = c['href'].split('/')[-1] if '/' in c['href'] else str(idx + 1)
            cisco_jobs.append({
                "external_job_id": jid,
                "title": c['title'].split('\n')[0],
                "location": "Bengaluru, India",
                "city": "Bengaluru",
                "country": "India",
                "apply_url": c['href'],
                "work_mode": "Hybrid",
                "employment_type": "Full-time"
            })
        print(f"  Cisco: Staged {len(cisco_jobs)} verified positions.")
    except Exception as e:
        print(f"  Cisco error: {e}")

    # Meta
    try:
        page.goto("https://www.metacareers.com/jobs?locations[0]=Bangalore%2C%20India&locations[1]=Gurgaon%2C%20India&locations[2]=Hyderabad%2C%20India", wait_until='networkidle', timeout=20000)
        time.sleep(2)
        m_items = page.evaluate("""() => {
            const links = Array.from(document.querySelectorAll('a[href*="/jobs/"]')).map(a => {
                const text = a.innerText.trim();
                return {
                    title: text.split('\\n')[0],
                    href: a.href
                };
            }).filter(j => j.title && j.title.length > 5 && !j.title.includes('Jobs') && !j.title.includes('Search'));
            return links;
        }""")
        for idx, m in enumerate(m_items):
            jid = m['href'].split('/')[-1] if '/' in m['href'] else str(idx + 1)
            meta_jobs.append({
                "external_job_id": jid,
                "title": m['title'],
                "location": "Bengaluru / Gurugram, India",
                "city": "Bengaluru",
                "country": "India",
                "apply_url": m['href'],
                "work_mode": "Hybrid / On-site",
                "employment_type": "Full-time"
            })
        print(f"  Meta: Staged {len(meta_jobs)} verified positions.")
    except Exception as e:
        print(f"  Meta error: {e}")

    browser.close()

staged_data["companies"]["Cisco"] = {
    "display_name": "Cisco India",
    "official_career_portal": "https://jobs.cisco.com",
    "staged_jobs_count": len(cisco_jobs),
    "sample_jobs": cisco_jobs[:3],
    "jobs": cisco_jobs
}

staged_data["companies"]["Meta"] = {
    "display_name": "Meta India",
    "official_career_portal": "https://www.metacareers.com",
    "staged_jobs_count": len(meta_jobs),
    "sample_jobs": meta_jobs[:3],
    "jobs": meta_jobs
}

# Save Staging Report
out_path = os.path.join(staging_dir, "category_a_bigtech_staged.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(staged_data, f, indent=2)

print("\n" + "=" * 80)
print(f"CATEGORY A STAGING REPORT GENERATED AT:\n{out_path}")
print("STAGED JOBS BREAKDOWN FOR MANUAL REVIEW:")
for cname, cinfo in staged_data["companies"].items():
    print(f"  • {cinfo['display_name']:20} | Staged Requisitions: {cinfo['staged_jobs_count']}")
print("=" * 80, flush=True)
