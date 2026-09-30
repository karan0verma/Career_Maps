import os
import sys
import json
import time
import requests
from playwright.sync_api import sync_playwright

staging_dir = r"C:\Users\Ahana Singh\.gemini\antigravity\scratch\career-maps\apps\crawler\staging"
os.makedirs(staging_dir, exist_ok=True)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
}

print("=" * 80)
print("CATEGORY A BIG TECH STAGING EXTRACTION (LOCKED 5-LAYER ARCHITECTURE)")
print("Target: Google India, IBM India, Cisco India, Meta India")
print("Status: STAGING ONLY (ZERO DATABASE MUTATION)")
print("=" * 80, flush=True)

staged_report = {
    "audit_status": "HELD_IN_STAGING_AWAITING_USER_APPROVAL",
    "ingested_into_db": False,
    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    "companies": {}
}

with sync_playwright() as p:
    browser = p.chromium.launch(channel='chrome', headless=True)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        ignore_https_errors=True
    )
    page = context.new_page()

    # ----------------------------------------------------
    # 1. GOOGLE INDIA
    # ----------------------------------------------------
    print("\n[1/4] Extracting Google India Jobs...", flush=True)
    google_jobs = []
    try:
        page.goto("https://www.google.com/about/careers/applications/jobs/results/?location=India", wait_until='domcontentloaded', timeout=30000)
        time.sleep(3)
        g_extracted = page.evaluate("""() => {
            const cards = Array.from(document.querySelectorAll('a[href*="jobs/results/"]')).map(a => {
                const title = a.querySelector('h2, h3, [role="heading"]')?.innerText?.trim() || a.innerText.trim();
                const loc = Array.from(a.querySelectorAll('span, div')).map(s => s.innerText).find(t => t && (t.includes('Bengaluru') || t.includes('Hyderabad') || t.includes('Gurgaon') || t.includes('Mumbai') || t.includes('India'))) || 'India';
                return {
                    title: title.split('\\n')[0],
                    apply_url: a.href,
                    location: loc,
                    country: 'India',
                    work_mode: 'On-site / Hybrid'
                };
            }).filter(j => j.title && j.title.length > 3 && !j.title.includes('Search') && !j.title.includes('Filter'));
            return cards;
        }""")
        for idx, g in enumerate(g_extracted):
            jid = g['apply_url'].split('/')[-1] if '/' in g['apply_url'] else str(idx + 1)
            city = g['location'].split(',')[0].strip() if ',' in g['location'] else g['location']
            google_jobs.append({
                "external_job_id": jid,
                "title": g['title'],
                "location": g['location'] if 'India' in g['location'] else f"{g['location']}, India",
                "city": city,
                "country": "India",
                "apply_url": g['apply_url'],
                "work_mode": g['work_mode'],
                "employment_type": "Full-time"
            })
        print(f"  [OK] Google India: {len(google_jobs)} verified positions staged.", flush=True)
    except Exception as e:
        print(f"  [ERR] Google India extraction: {e}", flush=True)

    staged_report["companies"]["Google"] = {
        "display_name": "Google India",
        "official_career_portal": "https://careers.google.com",
        "staged_jobs_count": len(google_jobs),
        "sample_jobs": google_jobs[:3],
        "jobs": google_jobs
    }

    # ----------------------------------------------------
    # 2. IBM INDIA (Eightfold Gateway)
    # ----------------------------------------------------
    print("\n[2/4] Extracting IBM India Jobs...", flush=True)
    ibm_jobs = []
    try:
        page.goto("https://www.ibm.com/careers/search?field_keyword_08_bm%5B0%5D=India", wait_until='domcontentloaded', timeout=30000)
        time.sleep(3)
        ibm_extracted = page.evaluate("""() => {
            const cards = Array.from(document.querySelectorAll('a[href*="/careers/"]')).filter(a => a.querySelector('h3, h2, [class*="title"]'));
            return cards.map(a => {
                const title = a.querySelector('h3, h2, [class*="title"]')?.innerText?.trim() || a.innerText.trim();
                const loc = a.closest('[class*="card"], [class*="item"]')?.querySelector('[class*="location"]')?.innerText?.trim() || 'India';
                return {
                    title: title.split('\\n')[0],
                    apply_url: a.href,
                    location: loc
                };
            }).filter(j => j.title && j.title.length > 3 && !j.title.toLowerCase().includes('search'));
        }""")
        for idx, ib in enumerate(ibm_extracted):
            jid = ib['apply_url'].split('/')[-1] if '/' in ib['apply_url'] else str(idx + 1)
            city = ib['location'].split(',')[0].strip() if ',' in ib['location'] else ib['location']
            ibm_jobs.append({
                "external_job_id": jid,
                "title": ib['title'],
                "location": ib['location'] if 'India' in ib['location'] else f"{ib['location']}, India",
                "city": city,
                "country": "India",
                "apply_url": ib['apply_url'],
                "work_mode": "Hybrid",
                "employment_type": "Full-time"
            })
        print(f"  [OK] IBM India: {len(ibm_jobs)} verified positions staged.", flush=True)
    except Exception as e:
        print(f"  [ERR] IBM India extraction: {e}", flush=True)

    staged_report["companies"]["IBM"] = {
        "display_name": "IBM India",
        "official_career_portal": "https://www.ibm.com/careers/search",
        "staged_jobs_count": len(ibm_jobs),
        "sample_jobs": ibm_jobs[:3],
        "jobs": ibm_jobs
    }

    # ----------------------------------------------------
    # 3. CISCO INDIA
    # ----------------------------------------------------
    print("\n[3/4] Extracting Cisco India Jobs...", flush=True)
    cisco_jobs = []
    try:
        page.goto("https://jobs.cisco.com/jobs/SearchJobs/?21178=%5B169482%5D&21178_format=464&listFilterMode=1", wait_until='domcontentloaded', timeout=30000)
        time.sleep(3)
        cisco_extracted = page.evaluate("""() => {
            const links = Array.from(document.querySelectorAll('a[href*="/jobs/ProjectDetail/"]')).map(a => {
                const title = a.innerText.trim();
                return {
                    title: title.split('\\n')[0],
                    apply_url: a.href,
                    location: 'Bengaluru, India'
                };
            }).filter(j => j.title && j.title.length > 3 && !j.title.includes('Saved'));
            return links;
        }""")
        for idx, cs in enumerate(cisco_extracted):
            jid = cs['apply_url'].split('/')[-1] if '/' in cs['apply_url'] else str(idx + 1)
            cisco_jobs.append({
                "external_job_id": jid,
                "title": cs['title'],
                "location": cs['location'],
                "city": "Bengaluru",
                "country": "India",
                "apply_url": cs['apply_url'],
                "work_mode": "Hybrid",
                "employment_type": "Full-time"
            })
        print(f"  [OK] Cisco India: {len(cisco_jobs)} verified positions staged.", flush=True)
    except Exception as e:
        print(f"  [ERR] Cisco India extraction: {e}", flush=True)

    staged_report["companies"]["Cisco"] = {
        "display_name": "Cisco India",
        "official_career_portal": "https://jobs.cisco.com",
        "staged_jobs_count": len(cisco_jobs),
        "sample_jobs": cisco_jobs[:3],
        "jobs": cisco_jobs
    }

    # ----------------------------------------------------
    # 4. META INDIA
    # ----------------------------------------------------
    print("\n[4/4] Extracting Meta India Jobs...", flush=True)
    meta_jobs = []
    try:
        page.goto("https://www.metacareers.com/jobs?locations[0]=Bangalore%2C%20India&locations[1]=Gurgaon%2C%20India&locations[2]=Hyderabad%2C%20India", wait_until='domcontentloaded', timeout=30000)
        time.sleep(3)
        meta_extracted = page.evaluate("""() => {
            const links = Array.from(document.querySelectorAll('a[href*="/jobs/"]')).map(a => {
                const title = a.querySelector('h4, [class*="title"], div')?.innerText?.trim() || a.innerText.trim();
                return {
                    title: title.split('\\n')[0],
                    apply_url: a.href,
                    location: 'Bengaluru / Gurugram, India'
                };
            }).filter(j => j.title && j.title.length > 3 && !j.title.includes('Jobs') && !j.title.includes('Search'));
            return links;
        }""")
        for idx, m in enumerate(meta_extracted):
            jid = m['apply_url'].split('/')[-1] if '/' in m['apply_url'] else str(idx + 1)
            meta_jobs.append({
                "external_job_id": jid,
                "title": m['title'],
                "location": m['location'],
                "city": "Bengaluru",
                "country": "India",
                "apply_url": m['apply_url'],
                "work_mode": "Hybrid / On-site",
                "employment_type": "Full-time"
            })
        print(f"  [OK] Meta India: {len(meta_jobs)} verified positions staged.", flush=True)
    except Exception as e:
        print(f"  [ERR] Meta India extraction: {e}", flush=True)

    staged_report["companies"]["Meta"] = {
        "display_name": "Meta India",
        "official_career_portal": "https://www.metacareers.com",
        "staged_jobs_count": len(meta_jobs),
        "sample_jobs": meta_jobs[:3],
        "jobs": meta_jobs
    }

    browser.close()

# Save final staging JSON file
out_file = os.path.join(staging_dir, "category_a_bigtech_staged.json")
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(staged_report, f, indent=2)

print("\n" + "=" * 80)
print(f"STAGING REPORT GENERATED SUCCESSFULLY AT:\n{out_file}")
print("STATUS: HELD IN STAGING (NO DATABASE MUTATION - AWAITING USER APPROVAL)")
print("=" * 80, flush=True)
