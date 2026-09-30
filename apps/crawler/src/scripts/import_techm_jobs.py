import sys
import os
import time
import uuid
import re
from typing import List, Dict, Any
from urllib.parse import urljoin, parse_qs, urlparse

# Setup path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend')))

from dotenv import load_dotenv
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend', '.env')))

from src.db.session import SessionLocal
from src.models.company import Company
from src.models.job import Job

from playwright.sync_api import sync_playwright

def run_import():
    url = "https://careers.techmahindra.com/CurrentOpportunity.aspx"
    print("=" * 70)
    print("IMPORTING 635 REAL TECH MAHINDRA JOBS INTO POSTGRESQL")
    print("=" * 70)
    
    db = SessionLocal()
    
    # 1. Get or Create Tech Mahindra Company
    company = db.query(Company).filter(Company.display_name.ilike('%tech mahindra%')).first()
    if not company:
        print("Creating Tech Mahindra company record...")
        company = Company(
            company_id=uuid.uuid4(),
            official_name="Tech Mahindra Limited",
            display_name="Tech Mahindra",
            website="https://www.techmahindra.com",
            career_url="https://careers.techmahindra.com/CurrentOpportunity.aspx",
            industry="Information Technology & Services",
            company_type="Public",
            headquarters="Pune, Maharashtra, India",
            country="India",
            city="Pune",
            state="Maharashtra",
            is_active=True,
            is_deleted=False
        )
        db.add(company)
        db.commit()
        db.refresh(company)
    else:
        company.is_active = True
        company.is_deleted = False
        company.career_url = "https://careers.techmahindra.com/CurrentOpportunity.aspx"
        db.commit()
        
    print(f"Tech Mahindra Company ID: {company.company_id}")
    
    # 2. Extract listings using Playwright
    print("\nExtracting live jobs from Tech Mahindra portal...")
    raw_extracted = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1440, "height": 900}
        )
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=40000)
        time.sleep(2)
        
        # Remove cookie overlay
        page.evaluate("""() => {
            const ot = document.getElementById('onetrust-consent-sdk');
            if (ot) ot.remove();
            const dark = document.querySelector('.onetrust-pc-dark-filter');
            if (dark) dark.remove();
        }""")
        time.sleep(1)
        
        # Trigger Search
        page.evaluate("document.getElementById('ctl00_ContentPlaceHolder1_btnFreeSearch').click()")
        page.wait_for_load_state('networkidle', timeout=20000)
        time.sleep(3)
        
        extracted_cards = page.evaluate("""() => {
            const cards = [];
            const cells = document.querySelectorAll('table td');
            
            cells.forEach(cell => {
                const text = (cell.innerText || '').trim();
                const link = cell.querySelector('a[href*="JobDetails.aspx"], a[href*="JobCode="]');
                
                if (!link || text.length < 20) return;
                
                const href = link.getAttribute('href') || '';
                const lines = text.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
                
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

    print(f"Extracted {len(raw_extracted)} job postings.")
    
    # 3. Insert into PostgreSQL
    inserted_count = 0
    updated_count = 0
    seen_urls = set()
    
    for item in raw_extracted:
        apply_url = item['applyUrl'].strip()
        if not apply_url or apply_url in seen_urls:
            continue
        seen_urls.add(apply_url)
        
        title = item['title'].strip()
        location = item.get('location', '').strip()
        skills_str = item.get('skills', '').strip()
        exp_str = item.get('experience', '').strip()
        domain = item.get('domain', 'Technology').strip()
        
        # Parse external job id from URL query parameters
        parsed_url = urlparse(apply_url)
        params = parse_qs(parsed_url.query)
        ext_id = params.get('JobCode', [''])[0][:50]
        
        # Determine country / city
        city = location if location.upper() in ['PUNE', 'BENGALURU', 'BANGALORE', 'HYDERABAD', 'NOIDA', 'CHENNAI', 'MUMBAI', 'KOLKATA', 'CHANDIGARH', 'GURUGRAM', 'GURGAON', 'DELHI'] else None
        country = "India" if city or 'INDIA' in location.upper() else "International"
        
        description = (
            f"Role: {title}\n"
            f"Domain: {domain or 'IT'}\n"
            f"Location: {location}, {country}\n"
            f"Experience Required: {exp_str or 'Not specified'}\n"
            f"Key Skills: {skills_str or 'Software Engineering'}\n\n"
            f"About Tech Mahindra:\n"
            f"Tech Mahindra offers innovative and customer-centric digital experiences, enabling enterprises, "
            f"associates, and the society to Rise. Apply directly on the official careers portal."
        )
        
        skills_list = [s.strip() for s in skills_str.split(',') if s.strip()] if skills_str else []
        
        existing_job = db.query(Job).filter(Job.apply_url == apply_url).first()
        
        if existing_job:
            existing_job.title = title
            existing_job.company_id = company.company_id
            existing_job.location = f"{location}, {country}" if location else "India"
            existing_job.country = country
            existing_job.city = city
            existing_job.department = domain
            existing_job.description = description
            existing_job.requirements = f"Experience: {exp_str}\nSkills: {skills_str}"
            existing_job.required_skills = skills_list
            existing_job.work_mode = "On-site / Hybrid"
            existing_job.employment_type = "Full-time"
            existing_job.experience_level = exp_str
            existing_job.is_active = True
            existing_job.is_deleted = False
            updated_count += 1
        else:
            new_job = Job(
                job_id=uuid.uuid4(),
                company_id=company.company_id,
                external_job_id=ext_id,
                title=title,
                department=domain,
                location=f"{location}, {country}" if location else "India",
                country=country,
                city=city,
                work_mode="On-site / Hybrid",
                employment_type="Full-time",
                experience_level=exp_str,
                description=description,
                requirements=f"Experience: {exp_str}\nSkills: {skills_str}",
                required_skills=skills_list,
                apply_url=apply_url,
                source_url=url,
                is_active=True,
                is_deleted=False
            )
            db.add(new_job)
            inserted_count += 1
            
    db.commit()
    db.close()
    
    print("\n" + "=" * 70)
    print(f"DATABASE COMMIT SUCCESSFUL!")
    print(f"  • Newly Inserted Jobs : {inserted_count}")
    print(f"  • Updated Active Jobs  : {updated_count}")
    print(f"  • Total Live for TechM : {inserted_count + updated_count}")
    print("=" * 70)

if __name__ == "__main__":
    run_import()
