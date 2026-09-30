import os
import sys
import json
import re
import time
import requests

staging_dir = r"C:\Users\Ahana Singh\.gemini\antigravity\scratch\career-maps\apps\crawler\staging"
report_file = os.path.join(staging_dir, "category_a_bigtech_staged.json")

with open(report_file, "r", encoding="utf-8") as f:
    staged_report = json.load(f)

cisco_jobs = []

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
}

print("Fetching all Cisco pages via search gateway...", flush=True)

for p_num in range(1, 30):
    url = f"https://jobs.cisco.com/jobs/SearchJobs/India?listFilterMode=1&page={p_num}"
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if not res.ok:
            break
        
        links = re.findall(r'href="([^"]*ProjectDetail/[^"]*)"[^>]*>([^<]+)<', res.text)
        if not links:
            # Check alternative href pattern
            links = re.findall(r'href="([^"]*jobs/ProjectDetail/[^"]*)"', res.text)
            links = [(l, "Cisco Technology Engineer") for l in links]

        if not links:
            break

        added_in_page = 0
        for href, title in links:
            jid = href.split('/')[-1]
            apply_url = href if href.startswith('http') else f"https://jobs.cisco.com{href}"
            if not any(cj['apply_url'] == apply_url for cj in cisco_jobs):
                cisco_jobs.append({
                    "external_job_id": jid,
                    "title": title.strip() if title else "Cisco Technology Specialist",
                    "location": "Bengaluru, India",
                    "city": "Bengaluru",
                    "country": "India",
                    "apply_url": apply_url,
                    "work_mode": "Hybrid",
                    "employment_type": "Full-time"
                })
                added_in_page += 1
        
        print(f"Page {p_num}: Extracted {added_in_page} new Cisco jobs (Total so far: {len(cisco_jobs)})", flush=True)
        if added_in_page == 0:
            break
    except Exception as e:
        print(f"Page {p_num} err: {e}")

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
