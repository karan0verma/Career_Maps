import os
import time
import requests
import psycopg
import uuid
import re
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright

db_url = "postgresql://postgres:postgres@localhost:5433/careermaps"

print("=" * 80)
print("FETCHING FRESH & ACCURATE DATA FOR IBM, CISCO, META")
print("=" * 80)

with psycopg.connect(db_url) as conn:
    with conn.cursor() as cur:
        # Delete bad jobs again just in case
        cur.execute("DELETE FROM jobs WHERE company_id IN (SELECT company_id FROM companies WHERE display_name IN ('IBM', 'Cisco', 'Meta'))")
        
        cur.execute("SELECT company_id, display_name FROM companies WHERE display_name IN ('IBM', 'Cisco', 'Meta')")
        comp_ids = {name: cid for cid, name in cur.fetchall()}

        def insert_job(cid, jid, title, city, apply_url):
            if not apply_url.startswith("http"):
                return False
                
            cur.execute("SELECT job_id FROM jobs WHERE external_job_id = %s AND company_id = %s", (jid, cid))
            if not cur.fetchone():
                cur.execute("""
                    INSERT INTO jobs (
                        job_id, company_id, external_job_id, title, 
                        location, city, country, apply_url, 
                        work_mode, employment_type, is_active, is_deleted,
                        first_seen_at, last_seen_at, created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    uuid.uuid4(), cid, jid, title, f"{city}, India", city, "India", apply_url,
                    "Hybrid", "Full-time", True, False,
                    datetime.now(timezone.utc), datetime.now(timezone.utc),
                    datetime.now(timezone.utc), datetime.now(timezone.utc)
                ))
                return True
            return False

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        # 1. CISCO
        print("Fetching Cisco via API...", flush=True)
        cisco_count = 0
        try:
            for p_num in range(1, 30):
                url = f"https://jobs.cisco.com/jobs/SearchJobs/India?listFilterMode=1&page={p_num}"
                res = requests.get(url, headers=headers, timeout=10)
                if not res.ok: break
                
                # Extract URL, Title, Location from HTML table
                # format: <a href="/jobs/ProjectDetail/Software-Engineer-II/1423423">Software Engineer</a>... <td>Bengaluru, India</td>
                matches = re.findall(r'<td[^>]*><a[^>]*href="([^"]+)"[^>]*>\s*(.*?)\s*</a>(.*?)<td[^>]*>(.*?)</td>', res.text, re.DOTALL | re.IGNORECASE)
                
                added_page = 0
                for match in matches:
                    href = match[0].strip()
                    title = match[1].strip()
                    loc_html = match[3].strip()
                    # clean HTML tags from location
                    loc_text = re.sub(r'<[^>]+>', '', loc_html).strip()
                    
                    if not title or not href: continue
                        
                    jid = href.split('/')[-1]
                    apply_url = href if href.startswith('http') else f"https://jobs.cisco.com{href}"
                    
                    city = "Bengaluru"
                    if "Pune" in loc_text: city = "Pune"
                    if "Chennai" in loc_text: city = "Chennai"
                    if "Hyderabad" in loc_text: city = "Hyderabad"
                    if "Gurugram" in loc_text or "Gurgaon" in loc_text: city = "Gurugram"
                    if "Noida" in loc_text: city = "Noida"
                    if "Mumbai" in loc_text: city = "Mumbai"
                    
                    if insert_job(comp_ids['Cisco'], jid, title, city, apply_url):
                        cisco_count += 1
                        added_page += 1
                
                if added_page == 0:
                    break
        except Exception as e:
            print("Cisco Error:", e)
        print(f"[OK] Inserted {cisco_count} valid Cisco India jobs.", flush=True)

        # 2. IBM
        print("Fetching IBM via Phenom/Eightfold...", flush=True)
        ibm_count = 0
        try:
            # We will use Playwright to load the page and extract JSON state or DOM links
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto("https://www.ibm.com/careers/search?field_keyword_08_bm%5B0%5D=India", wait_until="networkidle", timeout=20000)
                time.sleep(4)
                
                # Scroll down multiple times to lazy load
                for _ in range(15):
                    page.evaluate("window.scrollBy(0, 1500)")
                    time.sleep(1.5)
                
                ibm_jobs = page.evaluate("""() => {
                    return Array.from(document.querySelectorAll('a[href*="/job/"]')).map(a => {
                        const card = a.closest('.ibm-card') || a.parentElement;
                        const title = a.innerText.trim();
                        let loc = "Bengaluru";
                        if (card) {
                            const t = card.innerText;
                            if (t.includes("Pune")) loc = "Pune";
                            if (t.includes("Hyderabad")) loc = "Hyderabad";
                            if (t.includes("Gurugram") || t.includes("Gurgaon")) loc = "Gurugram";
                            if (t.includes("Noida")) loc = "Noida";
                            if (t.includes("Kolkata")) loc = "Kolkata";
                            if (t.includes("Mumbai")) loc = "Mumbai";
                            if (t.includes("Chennai")) loc = "Chennai";
                            if (t.includes("Kochi")) loc = "Kochi";
                        }
                        return { title: title.split('\\n')[0], url: a.href, city: loc };
                    }).filter(j => j.title.length > 5);
                }""")
                
                for j in ibm_jobs:
                    jid = j['url'].split('/')[-1]
                    if insert_job(comp_ids['IBM'], jid, j['title'], j['city'], j['url']):
                        ibm_count += 1
                
                browser.close()
        except Exception as e:
            print("IBM Error:", e)
        print(f"[OK] Inserted {ibm_count} valid IBM India jobs.", flush=True)

        # 3. META
        print("Fetching Meta via Playwright...", flush=True)
        meta_count = 0
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto("https://www.metacareers.com/jobs/?locations[0]=India", wait_until='networkidle', timeout=20000)
                time.sleep(4)
                
                # Check for "show more" buttons
                page.evaluate("""() => {
                    const btns = document.querySelectorAll('button');
                    btns.forEach(b => { if(b.innerText.toLowerCase().includes('more')) b.click(); });
                }""")
                time.sleep(3)
                
                m_jobs = page.evaluate("""() => {
                    return Array.from(document.querySelectorAll('a[href*="/v2/jobs/"]')).map(a => {
                        const p = a.parentElement.parentElement;
                        let text = p ? p.innerText : a.innerText;
                        return {
                            title: a.innerText.trim().split('\\n')[0],
                            url: a.href,
                            text: text
                        };
                    }).filter(j => j.title.length > 5);
                }""")
                
                for m in m_jobs:
                    jid = m['url'].split('/')[-2] if m['url'].endswith('/') else m['url'].split('/')[-1]
                    city = "Gurugram"
                    if "Bengaluru" in m['text'] or "Bangalore" in m['text']: city = "Bengaluru"
                    if "Hyderabad" in m['text']: city = "Hyderabad"
                    if "Mumbai" in m['text']: city = "Mumbai"
                    
                    if insert_job(comp_ids['Meta'], jid, m['title'], city, m['url']):
                        meta_count += 1
                        
                browser.close()
        except Exception as e:
            print("Meta Error:", e)
        print(f"[OK] Inserted {meta_count} valid Meta India jobs.", flush=True)
        
        conn.commit()

print("=" * 80)
print("DATABASE FIX COMPLETE. Please check frontend now.")
