import os
import sys
import json
import uuid
import re
import time
import datetime
from typing import Dict, List, Any, Set, Tuple
from uuid import UUID

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend')))

from dotenv import load_dotenv
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend', '.env')))

from src.db.session import SessionLocal
from src.models.company import Company
from src.models.job import Job
from playwright.sync_api import sync_playwright
import urllib.request

class DeltaSyncEngine:
    """
    Precision Differential Delta Synchronization Engine.
    Detects new vacancies, refreshes active positions, and auto-deactivates expired jobs.
    """

    def __init__(self):
        self.db = SessionLocal()

    def sync_tcs(self) -> Dict[str, Any]:
        company_id = UUID('6edf9a38-5bd9-4103-8d24-490c4919d100')
        company = self.db.query(Company).filter(Company.company_id == company_id).first()
        print(f"\n[1/3] Syncing {company.display_name} (TCS iBegin Portal)...", flush=True)

        all_live_raw = []
        with sync_playwright() as p:
            browser = p.chromium.launch(channel='chrome', headless=True)
            context = browser.new_context()
            page = context.new_page()
            page.goto('https://ibegin.tcsapps.com/candidate/#/jobs/search?geography=IN&language=EN', wait_until='networkidle', timeout=35000)
            time.sleep(3)

            payload_init = {
                "jobCity": None, "jobSkill": None, "pageNumber": "1", "userText": "",
                "jobTitleOrder": None, "jobCityOrder": None, "jobFunctionOrder": None,
                "jobExperienceOrder": None, "applyByOrder": None, "regular": True, "walkin": True
            }
            res_init = context.request.post(
                f"https://ibegin.tcsapps.com/candidate/api/v1/jobs/searchJ?at={int(time.time()*1000)}",
                headers={
                    "referer": "https://ibegin.tcsapps.com/candidate/jobs/search",
                    "content-type": "application/json;charset=UTF-8",
                    "accept": "application/json, text/plain, */*"
                },
                data=json.dumps(payload_init)
            )
            data_init = res_init.json().get('data', {})
            total_jobs_count = data_init.get('totalJobs', 3961)
            total_pages = (total_jobs_count // 10) + (1 if total_jobs_count % 10 != 0 else 0)

            for p_idx in range(1, total_pages + 1):
                payload = {
                    "jobCity": None, "jobSkill": None, "pageNumber": str(p_idx), "userText": "",
                    "jobTitleOrder": None, "jobCityOrder": None, "jobFunctionOrder": None,
                    "jobExperienceOrder": None, "applyByOrder": None, "regular": True, "walkin": True
                }
                try:
                    res = context.request.post(
                        f"https://ibegin.tcsapps.com/candidate/api/v1/jobs/searchJ?at={int(time.time()*1000)}",
                        headers={
                            "referer": "https://ibegin.tcsapps.com/candidate/jobs/search",
                            "content-type": "application/json;charset=UTF-8",
                            "accept": "application/json, text/plain, */*"
                        },
                        data=json.dumps(payload)
                    )
                    if res.status == 200:
                        items = res.json().get('data', {}).get('jobs', [])
                        all_live_raw.extend(items)
                except Exception as e:
                    print(f"Error on page {p_idx}: {e}")
            browser.close()

        # Transform to standardized format
        standardized_live = []
        for item in all_live_raw:
            ext_id = str(item.get('id') or item.get('jobId') or '').strip()
            if not ext_id:
                continue
            apply_url = f"https://ibegin.tcsapps.com/candidate/#/jobs/{ext_id}"
            title = (item.get('jobTitle') or "Software Engineer").strip()
            city = (item.get('location') or "Pan India").strip()
            location = f"{city}, India" if city.lower() != "pan india" else "Pan India"
            exp_level = f"{item.get('experience') or '2-8'} Years"
            func_name = item.get('functionName') or "Technology"
            skill_raw = item.get('skills') or func_name
            skills_list = [s.strip() for s in re.split(r'[,|/]', skill_raw) if s.strip() and len(s.strip()) > 1]
            if func_name and func_name not in skills_list:
                skills_list.append(func_name.title())

            jd_text = (
                f"Tata Consultancy Services (TCS) is hiring for the position of {title}.\n\n"
                f"Key Details:\n"
                f"• Role: {title}\n"
                f"• Function / Domain: {func_name}\n"
                f"• Location: {location}\n"
                f"• Experience: {exp_level}\n"
                f"• Skills: {', '.join(skills_list)}\n\n"
                f"Apply directly through the TCS iBegin portal."
            )

            standardized_live.append({
                "apply_url": apply_url,
                "title": title,
                "city": city,
                "location": location,
                "country": "India",
                "experience_level": exp_level,
                "required_skills": skills_list,
                "description": jd_text,
                "requirements": f"Experience: {exp_level} | Function: {func_name} | Skills: {', '.join(skills_list)}",
                "work_mode": "On-site / Hybrid"
            })

        return self._apply_delta(company, standardized_live)

    def sync_tech_mahindra(self) -> Dict[str, Any]:
        company_id = UUID('7d1045e7-0020-4660-a61b-13b81485263c')
        company = self.db.query(Company).filter(Company.company_id == company_id).first()
        print(f"\n[2/3] Syncing {company.display_name} (Tech Mahindra Portal)...", flush=True)

        url = "https://careers.techmahindra.com/CurrentOpportunity.aspx"
        cards = []
        with sync_playwright() as p:
            browser = p.chromium.launch(channel='chrome', headless=True)
            context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            page = context.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=45000)
            time.sleep(2)
            page.evaluate("() => { const ot = document.getElementById('onetrust-consent-sdk'); if(ot) ot.remove(); }")
            page.evaluate("document.getElementById('ctl00_ContentPlaceHolder1_btnFreeSearch').click()")
            page.wait_for_load_state('networkidle', timeout=25000)
            time.sleep(2)
            
            raw_cells = page.evaluate("""() => {
                const results = [];
                const cells = document.querySelectorAll('table td');
                cells.forEach(cell => {
                    const text = (cell.innerText || '').trim();
                    const link = cell.querySelector('a[href*="JobDetails.aspx"], a[href*="JobCode="]');
                    if (!link || text.length < 20) return;
                    const href = link.getAttribute('href') || '';
                    results.push({ text, href });
                });
                return results;
            }""")
            browser.close()
            
            for item in raw_cells:
                text = item['text']
                href = item['href']
                lines = [l.strip() for l in text.split('\n') if l.strip()]
                title = lines[0] if lines else "Software Engineer"
                skills = "Technology"
                exp = "3-8 Years"
                loc = "India"
                for line in lines:
                    ll = line.lower()
                    if 'skill set' in ll and ':' in line:
                        skills = line.split(':', 1)[1].strip()
                    elif 'experience' in ll and ':' in line:
                        exp = line.split(':', 1)[1].strip()
                    elif 'location' in ll and ':' in line:
                        loc = line.split(':', 1)[1].strip()
                
                full_url = href if href.startswith('http') else f"https://careers.techmahindra.com/{href.lstrip('/')}"
                cards.append({
                    "apply_url": full_url,
                    "title": title,
                    "city": loc,
                    "location": f"{loc}, India" if loc.lower() != 'india' else 'India',
                    "country": "India",
                    "experience_level": f"{exp} Years" if 'year' not in exp.lower() else exp,
                    "required_skills": [s.strip() for s in skills.split(',') if s.strip()],
                    "description": f"Tech Mahindra is hiring for {title}.\n\nKey Details:\n• Role: {title}\n• Location: {loc}\n• Experience: {exp}\n• Skills: {skills}",
                    "requirements": f"Experience: {exp} | Skills: {skills}",
                    "work_mode": "On-site / Hybrid"
                })

        return self._apply_delta(company, cards)

    def sync_coforge(self) -> Dict[str, Any]:
        company_id = UUID('af7bc651-d0b4-400f-8d57-9eb76636b11d')
        company = self.db.query(Company).filter(Company.company_id == company_id).first()
        print(f"\n[3/3] Syncing {company.display_name} (Coforge Zwayam Portal)...", flush=True)

        import requests
        from bs4 import BeautifulSoup

        url = 'https://public.zwayam.com/jobs/search'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Origin': 'https://careers.coforge.com',
            'Referer': 'https://careers.coforge.com/coforge/'
        }

        cards = []
        start = 0

        while True:
            d = {
                'filterCri': json.dumps({
                    'paginationStartNo': start,
                    'selectedCall': 'sort',
                    'sortCriteria': {'name': 'modifiedDate', 'isAscending': False},
                    'anyOfTheseWords': ''
                }),
                'domain': 'careers.coforge.com',
                'companyId': 'MTUxNzM='
            }
            try:
                r = requests.post(url, headers=headers, data=d, timeout=15)
                if r.status_code != 200:
                    break
                items = r.json().get('data', {}).get('data', [])
                if not items:
                    break
                for item in items:
                    job_id_ext = str(item.get('id', ''))
                    job_title = item.get('job_title', 'Software Engineer')
                    job_url_name = item.get('job_url_name', 'role')
                    apply_url = f"https://careers.coforge.com/coforge/jobview/{job_url_name}?id={job_id_ext}"

                    location_raw = item.get('location', '') or 'India'
                    loc_parts = [p.strip() for p in location_raw.split(',') if p.strip()]
                    city = loc_parts[0] if loc_parts else "India"

                    min_exp = item.get('min_exp')
                    max_exp = item.get('max_exp')
                    if min_exp is not None and max_exp is not None:
                        exp_str = f"{min_exp} to {max_exp} Years"
                    elif min_exp is not None:
                        exp_str = f"{min_exp}+ Years"
                    else:
                        exp_str = "3-8 Years"

                    skills = item.get('skills') or []
                    if isinstance(skills, str):
                        skills = [s.strip() for s in skills.split(',') if s.strip()]

                    desc_raw = item.get('job_description', '')
                    clean_desc = desc_raw
                    if desc_raw:
                        soup = BeautifulSoup(desc_raw.replace('<br>', '\n').replace('</p>', '\n\n'), 'html.parser')
                        clean_desc = soup.get_text().strip()

                    cards.append({
                        "apply_url": apply_url,
                        "title": job_title,
                        "city": city,
                        "location": location_raw if location_raw.lower() != 'india' else f"{city}, India",
                        "country": "India",
                        "experience_level": exp_str,
                        "required_skills": skills,
                        "description": clean_desc or f"Coforge is hiring for {job_title}.\n\nLocation: {location_raw}\nExperience: {exp_str}",
                        "requirements": f"Experience: {exp_str} | Skills: {', '.join(skills)}",
                        "work_mode": "On-site / Hybrid"
                    })
                start += len(items)
            except Exception as e:
                print(f"Error fetching Coforge batch: {e}")
                break

        return self._apply_delta(company, cards)

    def _apply_delta(self, company: Company, live_jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
        now = datetime.datetime.now(datetime.timezone.utc)
        
        # 1. Map live jobs by unique apply_url
        live_by_url: Dict[str, Dict[str, Any]] = {}
        for j in live_jobs:
            u = j.get('apply_url')
            if u and u not in live_by_url:
                live_by_url[u] = j

        live_urls: Set[str] = set(live_by_url.keys())

        # 2. Get existing DB jobs for this company
        existing_jobs = self.db.query(Job).filter(Job.company_id == company.company_id).all()
        existing_by_url = {j.apply_url: j for j in existing_jobs if j.apply_url}
        existing_urls: Set[str] = set(existing_by_url.keys())

        new_urls = live_urls - existing_urls
        active_urls = live_urls & existing_urls
        expired_urls = set(j.apply_url for j in existing_jobs if j.is_active and j.apply_url not in live_urls)

        print(f"  -> Total Live on Portal : {len(live_urls)}")
        print(f"  -> Existing in DB       : {len(existing_urls)}")
        print(f"  -> Newly Discovered     : {len(new_urls)}")
        print(f"  -> Still Active         : {len(active_urls)}")
        print(f"  -> Expired / Closed     : {len(expired_urls)}")

        # 3. Insert NEW jobs
        new_samples = []
        for url in new_urls:
            raw = live_by_url[url]
            new_job = Job(
                job_id=uuid.uuid4(),
                company_id=company.company_id,
                title=raw.get('title'),
                location=raw.get('location'),
                city=raw.get('city'),
                country=raw.get('country'),
                work_mode=raw.get('work_mode'),
                employment_type="Full-time",
                experience_level=raw.get('experience_level'),
                required_skills=raw.get('required_skills'),
                description=raw.get('description'),
                requirements=raw.get('requirements'),
                apply_url=url,
                is_active=True,
                is_deleted=False,
                first_seen_at=now,
                last_seen_at=now
            )
            self.db.add(new_job)
            if len(new_samples) < 3:
                new_samples.append(raw.get('title'))

        # 4. Refresh STILL ACTIVE jobs
        for url in active_urls:
            db_job = existing_by_url[url]
            db_job.last_seen_at = now
            db_job.is_active = True
            db_job.is_deleted = False

        # 5. Soft-Expire CLOSED jobs
        expired_samples = []
        for url in expired_urls:
            db_job = existing_by_url[url]
            db_job.is_active = False
            db_job.last_seen_at = now
            if len(expired_samples) < 3:
                expired_samples.append(db_job.title)

        self.db.commit()

        total_active_now = self.db.query(Job).filter(
            Job.company_id == company.company_id,
            Job.is_active == True,
            Job.is_deleted == False
        ).count()

        return {
            "company_name": company.display_name,
            "total_live": len(live_urls),
            "new_count": len(new_urls),
            "new_samples": new_samples,
            "active_count": len(active_urls),
            "expired_count": len(expired_urls),
            "expired_samples": expired_samples,
            "current_total_active": total_active_now
        }

    def sync_infosys(self) -> Dict[str, Any]:
        company_id = UUID('8b6e2d14-0e31-419b-9c71-29e557b71900')
        company = self.db.query(Company).filter(Company.company_id == company_id).first()
        print(f"\n[4/5] Syncing {company.display_name} (Infosys INTAP Gateway)...", flush=True)

        url = "https://intapgateway.infosysapps.com/careersci/search/intapjbsrch/getCareerSearchJobs?sourceId=1&searchText=ALL"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://career.infosys.com/joblist',
            'Origin': 'https://career.infosys.com'
        }

        req = urllib.request.Request(url, headers=headers)
        cards = []
        try:
            res = urllib.request.urlopen(req, timeout=25)
            raw_jobs = json.loads(res.read().decode('utf-8'))
            for item in raw_jobs:
                ref_code = item.get('referenceCode') or f"INFSYS-{item.get('postingId')}"
                title = (item.get('postingTitle') or "Software Engineer").strip()
                loc_raw = (item.get('location') or "Bengaluru").strip().title()
                location = f"{loc_raw}, India"
                min_e = item.get('minExperienceLevel', 2)
                max_e = item.get('maxExperienceLevel', 8)
                exp_level = f"{min_e}-{max_e} Years"
                func_area = item.get('functionalArea') or "Technology"

                desc_parts = []
                if item.get('postingDescription'):
                    desc_parts.append(item.get('postingDescription').strip())
                if item.get('rolesResponsibilities'):
                    desc_parts.append(f"Roles & Responsibilities:\n{item.get('rolesResponsibilities').strip()}")
                if item.get('technicalRequirement'):
                    desc_parts.append(f"Technical Requirements:\n{item.get('technicalRequirement').strip()}")

                full_desc = "\n\n".join(desc_parts) if desc_parts else f"Infosys Limited is hiring for {title}."
                apply_url = f"https://career.infosys.com/jobdesc?jobReferenceCode={ref_code}&companyhiringtype=IL&countrycode=IN"

                cards.append({
                    "apply_url": apply_url,
                    "title": title,
                    "city": loc_raw,
                    "location": location,
                    "country": "India",
                    "experience_level": exp_level,
                    "required_skills": [func_area, "Technology", "Software Engineering"],
                    "description": full_desc,
                    "requirements": f"Experience: {exp_level} | Function: {func_area} | Reference: {ref_code}",
                    "work_mode": "On-site / Hybrid"
                })
        except Exception as e:
            print(f"Error fetching Infosys live: {e}")

        return self._apply_delta(company, cards)

    def sync_wipro(self) -> Dict[str, Any]:
        company_id = UUID('de6eabf2-5a61-4872-9ef4-989da3ff6a20')
        company = self.db.query(Company).filter(Company.company_id == company_id).first()
        print(f"\n[5/5] Syncing {company.display_name} (Wipro Recruiting API)...", flush=True)

        cards = []
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(channel='chrome', headless=True)
                context = browser.new_context()
                page = context.new_page()

                csrf_token = ""
                def on_req(req):
                    nonlocal csrf_token
                    if 'x-csrf-token' in req.headers:
                        csrf_token = req.headers['x-csrf-token']

                page.on('request', on_req)
                page.goto('https://careers.wipro.com/search/?q=&locationsearch=India&searchResultView=LIST', wait_until='domcontentloaded', timeout=30000)
                time.sleep(3)

                headers = {
                    'content-type': 'application/json',
                    'referer': 'https://careers.wipro.com/search/?q=&locationsearch=India&searchResultView=LIST',
                    'x-csrf-token': csrf_token
                }

                page_num = 0
                while True:
                    payload = {
                        "locale": "en_US",
                        "pageNumber": page_num,
                        "sortBy": "",
                        "keywords": "",
                        "location": "India",
                        "facetFilters": {},
                        "brand": "",
                        "skills": [],
                        "categoryId": 0,
                        "alertId": "",
                        "rcmCandidateId": ""
                    }
                    res = context.request.post("https://careers.wipro.com/services/recruiting/v1/jobs", headers=headers, data=json.dumps(payload))
                    if res.status != 200:
                        break
                    data = res.json()
                    jobs = data.get('jobSearchResult', [])
                    total_jobs = data.get('totalJobs', 0)
                    if not jobs:
                        break

                    for item in jobs:
                        resp = item.get('response', {})
                        jid = str(resp.get('id', ''))
                        slug = resp.get('unifiedUrlTitle') or resp.get('urlTitle') or 'wipro-opportunity'
                        apply_url = f"https://careers.wipro.com/job/{slug}/{jid}-en_US/" if jid else None
                        if not apply_url:
                            continue

                        title = (resp.get('unifiedStandardTitle') or resp.get('urlTitle') or resp.get('jobTitle') or "Software Engineer").strip()
                        loc_raw = resp.get('jobLocationShort', ['Bengaluru, India'])[0] if resp.get('jobLocationShort') else 'Bengaluru, India'
                        clean_loc = re.sub(r'<[^>]+>', '', loc_raw).strip()
                        parts = [p.strip() for p in clean_loc.split(',') if p.strip()]
                        city = parts[0] if parts else "Bengaluru"
                        location = f"{city}, India" if "india" not in city.lower() else city

                        department = resp.get('department', ['Technology'])[0] if resp.get('department') else 'Technology'

                        cards.append({
                            "apply_url": apply_url,
                            "title": title,
                            "city": city,
                            "location": location,
                            "country": "India",
                            "experience_level": "3-8 Years",
                            "required_skills": [department, "Technology", "Software Engineering"],
                            "description": f"Wipro Limited is hiring for {title}.\nLocation: {location}\nDepartment: {department}",
                            "requirements": f"Location: {location} | Department: {department}",
                            "work_mode": "On-site / Hybrid"
                        })

                    if len(cards) >= total_jobs:
                        break
                    page_num += 1

                browser.close()
        except Exception as e:
            print(f"Error fetching Wipro live: {e}")

        return self._apply_delta(company, cards)

    def close(self):
        self.db.close()

def run_delta_audit():
    engine = DeltaSyncEngine()
    results = []
    
    # Sync all 5 companies
    results.append(engine.sync_tcs())
    results.append(engine.sync_tech_mahindra())
    results.append(engine.sync_coforge())
    results.append(engine.sync_infosys())
    results.append(engine.sync_wipro())
    
    engine.close()
    return results

if __name__ == "__main__":
    run_delta_audit()
