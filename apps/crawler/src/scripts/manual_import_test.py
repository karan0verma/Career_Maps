import sys
import os
import time
import json
import re
from typing import List, Dict, Any
from urllib.parse import urljoin

# Setup path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend')))

from dotenv import load_dotenv
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend', '.env')))

from playwright.sync_api import sync_playwright

def run_tech_mahindra_manual_extract():
    url = "https://careers.techmahindra.com/CurrentOpportunity.aspx"
    print("=" * 70)
    print("MANUAL REAL-WEBSITE JOB IMPORT: TECH MAHINDRA")
    print(f"Target URL: {url}")
    print("=" * 70 + "\n")
    print("[1/3] Launching browser and navigating to real job listings...")
    
    raw_extracted = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1440, "height": 900}
        )
        page = context.new_page()
        
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=40000)
        except Exception as e:
            print(f"[Notice] Page loaded with notice: {e}")
            
        time.sleep(2)
        
        # 1. Clear OneTrust cookie overlay
        page.evaluate("""() => {
            const ot = document.getElementById('onetrust-consent-sdk');
            if (ot) ot.remove();
            const dark = document.querySelector('.onetrust-pc-dark-filter');
            if (dark) dark.remove();
        }""")
        time.sleep(1)
        
        # 2. Select Country India & Trigger Search
        print("[2/3] Querying live opportunities database for all roles...")
        try:
            # Click Free Search button directly to retrieve all current active opportunities
            page.evaluate("document.getElementById('ctl00_ContentPlaceHolder1_btnFreeSearch').click()")
            page.wait_for_load_state('networkidle', timeout=20000)
        except Exception as e:
            print(f"[Notice] Search trigger: {e}")
            
        time.sleep(3)
        
        # 3. Extract distinct job cards
        # Tech Mahindra renders cards inside table structure with job detail links
        extracted_cards = page.evaluate("""() => {
            const cards = [];
            
            // Look for table cells containing individual job postings
            const cells = document.querySelectorAll('table td');
            
            cells.forEach(cell => {
                const text = (cell.innerText || '').trim();
                const link = cell.querySelector('a[href*="JobDetails.aspx"], a[href*="JobCode="]');
                
                if (!link || text.length < 20) return;
                
                const href = link.getAttribute('href') || '';
                const lines = text.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
                
                // Parse fields from text
                // Structure typically:
                // [0] IT / Domain
                // [1] Job Title
                // [2] Skill Set : ...
                // [3] Experience : ...
                // [4] Location : ...
                
                let domain = '';
                let title = '';
                let skills = '';
                let experience = '';
                let location = '';
                
                lines.forEach((line, idx) => {
                    const lLower = line.toLowerCase();
                    if (lLower.startsWith('skill set :') || lLower.startsWith('skill set:')) {
                        skills = line.split(':')[1]?.trim() || '';
                    } else if (lLower.startsWith('experience :') || lLower.startsWith('experience:')) {
                        experience = line.split(':')[1]?.trim() || '';
                    } else if (lLower.startsWith('location :') || lLower.startsWith('location:')) {
                        location = line.split(':')[1]?.trim() || '';
                    } else if (idx === 0 && line.length <= 10) {
                        domain = line;
                    } else if (!title && !lLower.includes('apply') && !lLower.includes('shortlist') && line.length > 3) {
                        title = line;
                    }
                });
                
                if (title && href) {
                    cards.push({
                        domain: domain,
                        title: title,
                        skills: skills,
                        experience: experience,
                        location: location || 'India',
                        applyUrl: href,
                        rawText: text
                    });
                }
            });
            
            return cards;
        }""")
        
        for c in extracted_cards:
            if c['applyUrl'] and not c['applyUrl'].startswith('http'):
                c['applyUrl'] = urljoin(url, c['applyUrl'])
            raw_extracted.append(c)
            
        browser.close()
        
    print(f"[3/3] Performing Validation, Audit & Deduplication on {len(raw_extracted)} records...\n")
    
    discovered_count = len(raw_extracted)
    valid_jobs = []
    invalid_jobs = []
    duplicate_jobs = []
    missing_info_jobs = []
    ready_for_import = []
    
    seen_keys = set()
    non_job_keywords = {'about us', 'contact us', 'privacy policy', 'terms', 'home', 'careers', 'phone', 'cookie', 'apply/shortlist'}
    
    for job in raw_extracted:
        title = (job.get('title') or '').strip()
        apply_url = (job.get('applyUrl') or '').strip()
        location = (job.get('location') or '').strip()
        skills = (job.get('skills') or '').strip()
        exp = (job.get('experience') or '').strip()
        
        is_invalid = False
        reasons = []
        
        # Title sanity
        if len(title) < 3:
            is_invalid = True
            reasons.append("Title too short (< 3 chars)")
        if any(title.lower() == kw for kw in non_job_keywords):
            is_invalid = True
            reasons.append(f"Title is non-job keyword: '{title}'")
        if not apply_url or 'JobCode=' not in apply_url:
            is_invalid = True
            reasons.append("Missing specific JobCode in apply URL")
            
        if is_invalid:
            invalid_jobs.append({"title": title, "reasons": reasons, "url": apply_url})
            continue
            
        # Deduplication
        dedup_key = f"{title.lower()}||{location.lower()}||{apply_url.lower()}"
        if dedup_key in seen_keys:
            duplicate_jobs.append(job)
            continue
        seen_keys.add(dedup_key)
        
        # Missing Critical Info Check
        missing_fields = []
        if not location or location.lower() == 'india':
            missing_fields.append("Specific city missing (generic India)")
        if not skills:
            missing_fields.append("Skill requirements")
        if not exp:
            missing_fields.append("Experience criteria")
            
        if missing_fields:
            missing_info_jobs.append({
                "job": job,
                "missing": missing_fields
            })
            
        # Complete normalized record
        normalized_job = {
            "company": "Tech Mahindra",
            "title": title,
            "domain": job.get('domain', 'Technology'),
            "location": location if location and location != 'India' else 'Multiple Locations, India',
            "country": "India" if location.upper() in ['PUNE', 'BENGALURU', 'BANGALORE', 'HYDERABAD', 'NOIDA', 'CHENNAI', 'MUMBAI', 'KOLKATA', 'CHANDIGARH', 'INDIA'] else "International",
            "experience": exp if exp else "Not specified",
            "skills": skills if skills else "General Software Engineering",
            "description": f"Domain: {job.get('domain', 'IT')} | Required Skills: {skills} | Experience: {exp}. Apply directly via Tech Mahindra Careers Portal.",
            "apply_url": apply_url,
            "employment_type": "Full-time",
            "work_mode": "On-site / Hybrid"
        }
        
        valid_jobs.append(normalized_job)
        ready_for_import.append(normalized_job)

    # OUTPUT REPORT
    print("=" * 70)
    print("PRE-IMPORT AUDIT BREAKDOWN: TECH MAHINDRA")
    print("=" * 70)
    print(f"  • Jobs discovered                : {discovered_count}")
    print(f"  • Valid jobs                     : {len(valid_jobs)}")
    print(f"  • Invalid / Rejected jobs        : {len(invalid_jobs)}")
    print(f"  • Duplicate jobs                 : {len(duplicate_jobs)}")
    print(f"  • Jobs with partial/missing info : {len(missing_info_jobs)}")
    print(f"  • Jobs READY for import          : {len(ready_for_import)}")
    print("=" * 70 + "\n")
    
    if invalid_jobs:
        print("--- REJECTED / INVALID SAMPLES ---")
        for inv in invalid_jobs[:5]:
            print(f"  [REJECTED] Title: {inv['title']} | Reasons: {', '.join(inv['reasons'])}")
        print()

    print("--- READY FOR IMPORT SAMPLES (First 10 Real Jobs) ---")
    for i, j in enumerate(ready_for_import[:10], 1):
        print(f"[{i}] {j['title']}")
        print(f"    Company         : {j['company']}")
        print(f"    Location        : {j['location']} ({j['country']})")
        print(f"    Experience Level: {j['experience']}")
        print(f"    Key Skills      : {j['skills']}")
        print(f"    Work Mode       : {j['work_mode']}")
        print(f"    Apply URL       : {j['apply_url']}")
        print(f"    Description     : {j['description']}")
        print("-" * 70)
        
    print("\n" + "=" * 70)
    print("DATABASE STATUS: NO JOBS COMMITTED TO POSTGRESQL YET.")
    print("Awaiting your confirmation to insert into PostgreSQL.")
    print("=" * 70)

if __name__ == "__main__":
    run_tech_mahindra_manual_extract()
