import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

staging_dir = r"C:\Users\Ahana Singh\.gemini\antigravity\scratch\career-maps\apps\crawler\staging"
report_file = os.path.join(staging_dir, "category_a_bigtech_staged.json")

with open(report_file, "r", encoding="utf-8") as f:
    staged_report = json.load(f)

with sync_playwright() as p:
    browser = p.chromium.launch(channel='chrome', headless=True)
    page = browser.new_page()

    # 1. Cisco
    print("Testing Cisco Phenom portal...", flush=True)
    cisco_jobs = []
    try:
        page.goto("https://jobs.cisco.com/jobs/SearchJobs/?21178=%5B169482%5D&21178_format=464&listFilterMode=1", wait_until='networkidle', timeout=20000)
        time.sleep(3)
        # Parse table rows
        rows = page.evaluate("""() => {
            const table = document.querySelector('table');
            if (!table) return [];
            const trs = Array.from(table.querySelectorAll('tr')).slice(1);
            return trs.map(tr => {
                const a = tr.querySelector('a');
                const tds = Array.from(tr.querySelectorAll('td')).map(td => td.innerText.trim());
                return {
                    title: a ? a.innerText.trim() : (tds[0] || ''),
                    href: a ? a.href : '',
                    location: tds[1] || 'Bengaluru, India'
                };
            }).filter(j => j.title);
        }""")
        print("Cisco raw rows count:", len(rows))
        for idx, r in enumerate(rows):
            jid = r['href'].split('/')[-1] if r['href'] else str(idx + 1)
            cisco_jobs.append({
                "external_job_id": jid,
                "title": r['title'],
                "location": r['location'] if 'India' in r['location'] else f"{r['location']}, India",
                "city": "Bengaluru",
                "country": "India",
                "apply_url": r['href'] or f"https://jobs.cisco.com/jobs/ProjectDetail/{jid}",
                "work_mode": "Hybrid",
                "employment_type": "Full-time"
            })
    except Exception as e:
        print("Cisco test err:", e)

    # 2. Meta
    print("Testing Meta Careers page...", flush=True)
    meta_jobs = []
    try:
        page.goto("https://www.metacareers.com/jobs?q=India", wait_until='networkidle', timeout=20000)
        time.sleep(3)
        m_cards = page.evaluate("""() => {
            const links = Array.from(document.querySelectorAll('a[href*="/jobs/"]'));
            const results = [];
            const seen = new Set();
            links.forEach(a => {
                const text = a.innerText.trim();
                if (text && text.length > 5 && !text.includes('Search') && !text.includes('Jobs') && !seen.has(a.href)) {
                    seen.add(a.href);
                    results.push({ title: text.split('\\n')[0], href: a.href });
                }
            });
            return results;
        }""")
        print("Meta raw cards count:", len(m_cards))
        for idx, m in enumerate(m_cards):
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
    except Exception as e:
        print("Meta test err:", e)

    browser.close()

# Update staging report
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

print("Updated staging report.")
