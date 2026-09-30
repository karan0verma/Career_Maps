import os
import sys
import json
import time
import requests
from playwright.sync_api import sync_playwright

staging_dir = r"C:\Users\Ahana Singh\.gemini\antigravity\scratch\career-maps\apps\crawler\staging"
os.makedirs(staging_dir, exist_ok=True)

print("=" * 80)
print("CATEGORY A DISCOVERY & EXTRACTION PIPELINE: BIG TECH & PRODUCT GIANTS")
print("Target: Google India, IBM India, Adobe India, Cisco India, Meta India")
print("=" * 80, flush=True)

extracted_data = {
    "google": {"company": "Google India", "jobs": [], "total_portal_count": 0, "verified_urls": []},
    "ibm": {"company": "IBM India", "jobs": [], "total_portal_count": 0, "verified_urls": []},
    "adobe": {"company": "Adobe India", "jobs": [], "total_portal_count": 0, "verified_urls": []},
    "cisco": {"company": "Cisco India", "jobs": [], "total_portal_count": 0, "verified_urls": []},
    "meta": {"company": "Meta India", "jobs": [], "total_portal_count": 0, "verified_urls": []},
}

with sync_playwright() as p:
    browser = p.chromium.launch(channel='chrome', headless=True)
    context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    page = context.new_page()

    # ----------------------------------------------------
    # 1. GOOGLE INDIA
    # ----------------------------------------------------
    print("\n[1/5] Extracting Google India Jobs...", flush=True)
    try:
        # Google Careers API endpoint
        google_api_url = "https://careers.google.com/api/v3/search/?distance=50&location=India&max=100&page=1"
        res = page.request.get(google_api_url)
        if res.ok:
            data = res.json()
            total_g = data.get('count', 0)
            extracted_data['google']['total_portal_count'] = total_g
            print(f"  Google API returned {total_g} total India jobs.", flush=True)
            
            # Fetch all pages
            jobs_list = data.get('jobs', [])
            total_pages = (total_g // 100) + 1
            for pg in range(2, total_pages + 1):
                p_res = page.request.get(f"https://careers.google.com/api/v3/search/?distance=50&location=India&max=100&page={pg}")
                if p_res.ok:
                    jobs_list.extend(p_res.json().get('jobs', []))
            
            for j in jobs_list:
                jid = j.get('id', '')
                title = j.get('title', '')
                locs = [loc.get('display', '') for loc in j.get('locations', [])]
                loc_str = ", ".join(locs) if locs else "India"
                apply_url = j.get('apply_url') or f"https://careers.google.com/jobs/results/{jid}"
                extracted_data['google']['jobs'].append({
                    "id": jid,
                    "title": title,
                    "location": loc_str,
                    "country": "India",
                    "apply_url": apply_url,
                    "work_mode": "On-site / Hybrid",
                    "description": j.get('description', '')[:500]
                })
            print(f"  Extracted {len(extracted_data['google']['jobs'])} unique Google India jobs.", flush=True)
    except Exception as e:
        print(f"  Error extracting Google: {e}", flush=True)

    # ----------------------------------------------------
    # 2. IBM INDIA
    # ----------------------------------------------------
    print("\n[2/5] Extracting IBM India Jobs...", flush=True)
    try:
        # IBM BrassRing / Kenexa / Search API
        page.goto("https://www.ibm.com/careers/search?field_keyword_08_bm%5B0%5D=India", wait_until='domcontentloaded', timeout=30000)
        time.sleep(3)

        # Inspect network for IBM API
        ibm_api_url = "https://www.ibm.com/careers/api/search?field_keyword_08_bm%5B0%5D=India&limit=100"
        ibm_res = page.request.get(ibm_api_url)
        if ibm_res.ok:
            d = ibm_res.json()
            total_ibm = d.get('total', len(d.get('hits', [])))
            extracted_data['ibm']['total_portal_count'] = total_ibm
            print(f"  IBM API returned {total_ibm} total India jobs.", flush=True)
            for hit in d.get('hits', []):
                jid = hit.get('id') or hit.get('req_id', '')
                title = hit.get('title', '')
                loc = hit.get('location', 'India')
                apply_url = hit.get('url') or f"https://www.ibm.com/careers/job/{jid}"
                extracted_data['ibm']['jobs'].append({
                    "id": str(jid),
                    "title": title,
                    "location": loc,
                    "country": "India",
                    "apply_url": apply_url,
                    "work_mode": "Hybrid",
                    "description": hit.get('description', '')[:500]
                })
        else:
            # DOM fallback for IBM
            ibm_jobs = page.evaluate("""() => {
                const links = Array.from(document.querySelectorAll('a[href*="/careers/"]')).filter(a => a.querySelector('h3, h2, [class*="title"]'));
                return links.map(a => ({
                    title: a.innerText.trim(),
                    href: a.href
                }));
            }""")
            print(f"  Extracted {len(ibm_jobs)} IBM jobs from DOM.", flush=True)
    except Exception as e:
        print(f"  Error extracting IBM: {e}", flush=True)

    # ----------------------------------------------------
    # 3. ADOBE INDIA (Workday API)
    # ----------------------------------------------------
    print("\n[3/5] Extracting Adobe India Jobs...", flush=True)
    try:
        adobe_url = "https://adobe.wd5.myworkdayjobs.com/wday/cxs/adobe/external_experienced/jobs"
        adobe_payload = {"appliedFacets": {"locationCountry": ["bc33aa3152ec42d4995f4791a106ed09"]}, "limit": 50, "offset": 0, "searchText": ""}
        adobe_res = page.request.post(adobe_url, data=json.dumps(adobe_payload), headers={'content-type': 'application/json'})
        if adobe_res.ok:
            ad_data = adobe_res.json()
            total_adobe = ad_data.get('total', 0)
            extracted_data['adobe']['total_portal_count'] = total_adobe
            print(f"  Adobe Workday API returned {total_adobe} total India jobs.", flush=True)
            
            job_postings = ad_data.get('jobPostings', [])
            # Iterate pages
            for off in range(50, min(total_adobe, 500), 50):
                p_payload = {"appliedFacets": {"locationCountry": ["bc33aa3152ec42d4995f4791a106ed09"]}, "limit": 50, "offset": off, "searchText": ""}
                p_res = page.request.post(adobe_url, data=json.dumps(p_payload), headers={'content-type': 'application/json'})
                if p_res.ok:
                    job_postings.extend(p_res.json().get('jobPostings', []))
            
            for j in job_postings:
                jid = j.get('bulletFields', [j.get('externalPath', '')])[0]
                title = j.get('title', '')
                ext_path = j.get('externalPath', '')
                loc = j.get('locationsText', 'India')
                apply_url = f"https://adobe.wd5.myworkdayjobs.com/en-US/external_experienced{ext_path}"
                extracted_data['adobe']['jobs'].append({
                    "id": str(jid),
                    "title": title,
                    "location": loc,
                    "country": "India",
                    "apply_url": apply_url,
                    "work_mode": "Hybrid / On-site",
                    "description": f"Adobe hiring for {title} in {loc}"
                })
            print(f"  Extracted {len(extracted_data['adobe']['jobs'])} unique Adobe India jobs.", flush=True)
    except Exception as e:
        print(f"  Error extracting Adobe: {e}", flush=True)

    # ----------------------------------------------------
    # 4. CISCO INDIA
    # ----------------------------------------------------
    print("\n[4/5] Extracting Cisco India Jobs...", flush=True)
    try:
        cisco_url = "https://jobs.cisco.com/api/jobs?location=India&page=1&limit=100"
        cisco_res = page.request.get(cisco_url)
        if cisco_res.ok:
            c_data = cisco_res.json()
            total_cisco = c_data.get('total', len(c_data.get('jobs', [])))
            extracted_data['cisco']['total_portal_count'] = total_cisco
            print(f"  Cisco API returned {total_cisco} total India jobs.", flush=True)
            for j in c_data.get('jobs', []):
                jid = j.get('id', '')
                title = j.get('data', {}).get('title') or j.get('title', '')
                loc = j.get('data', {}).get('city', 'India') + ", India"
                apply_url = j.get('data', {}).get('apply_url') or f"https://jobs.cisco.com/jobs/ProjectDetail/{jid}"
                extracted_data['cisco']['jobs'].append({
                    "id": str(jid),
                    "title": title,
                    "location": loc,
                    "country": "India",
                    "apply_url": apply_url,
                    "work_mode": "Hybrid",
                    "description": f"Cisco hiring for {title} in {loc}"
                })
            print(f"  Extracted {len(extracted_data['cisco']['jobs'])} unique Cisco India jobs.", flush=True)
    except Exception as e:
        print(f"  Error extracting Cisco: {e}", flush=True)

    # ----------------------------------------------------
    # 5. META INDIA
    # ----------------------------------------------------
    print("\n[5/5] Extracting Meta India Jobs...", flush=True)
    try:
        meta_url = "https://www.metacareers.com/graphql"
        # Let's inspect Meta Careers landing page
        page.goto("https://www.metacareers.com/jobs?locations[0]=Bangalore%2C%20India&locations[1]=Gurgaon%2C%20India&locations[2]=Hyderabad%2C%20India&locations[3]=Mumbai%2C%20India", wait_until='domcontentloaded', timeout=30000)
        time.sleep(3)

        meta_jobs = page.evaluate("""() => {
            const cards = Array.from(document.querySelectorAll('a[href*="/jobs/"]')).filter(a => a.querySelector('h4, [class*="title"], div'));
            const results = [];
            const seen = new Set();
            cards.forEach(a => {
                const title = a.querySelector('h4, [class*="_8t44"], div')?.innerText?.trim() || a.innerText.trim();
                const loc = Array.from(a.querySelectorAll('div, span')).map(s => s.innerText).find(t => t.includes('India')) || 'India';
                if (title && a.href && !seen.has(a.href)) {
                    seen.add(a.href);
                    results.push({
                        title: title.split('\\n')[0],
                        href: a.href,
                        location: loc
                    });
                }
            });
            return results;
        }""")
        extracted_data['meta']['total_portal_count'] = len(meta_jobs)
        for idx, mj in enumerate(meta_jobs):
            extracted_data['meta']['jobs'].append({
                "id": str(idx + 1),
                "title": mj['title'],
                "location": mj['location'],
                "country": "India",
                "apply_url": mj['href'],
                "work_mode": "Hybrid / On-site",
                "description": f"Meta hiring for {mj['title']} in {mj['location']}"
            })
        print(f"  Extracted {len(extracted_data['meta']['jobs'])} unique Meta India jobs.", flush=True)
    except Exception as e:
        print(f"  Error extracting Meta: {e}", flush=True)

    browser.close()

# Save staging data for double-check report
out_file = os.path.join(staging_dir, "category_a_extracted.json")
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(extracted_data, f, indent=2)

print("\n" + "=" * 80)
print(f"CATEGORY A EXTRACTION STAGED FOR USER MANUAL REVIEW: {out_file}")
print("=" * 80, flush=True)
