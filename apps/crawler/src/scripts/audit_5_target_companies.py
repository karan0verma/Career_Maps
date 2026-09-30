import os
import sys
import json
import urllib.request
import urllib.parse
from playwright.sync_api import sync_playwright

def audit_5_companies():
    print("=" * 85)
    print("AUDITING 5 TARGET COMPANIES: LIVE JOB COUNTS, LOCATIONS, SAMPLE LINKS")
    print("=" * 85, flush=True)

    report = {}

    # -----------------------------------------------------------------
    # 1. AMAZON INDIA
    # -----------------------------------------------------------------
    print("\n1. Auditing Amazon India...", flush=True)
    try:
        url_amz = "https://www.amazon.jobs/en/search.json?country=IND&facets%5B%5D=normalized_location&offset=0&result_limit=10"
        req = urllib.request.Request(url_amz, headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req)
        data = json.loads(res.read().decode())
        total_amz = data.get('hits', 0)
        jobs_amz = data.get('jobs', [])
        loc_facets = data.get('facets', {}).get('normalized_location', {})
        
        report['Amazon India'] = {
            'portal_source': 'Amazon Jobs Official Gateway (amazon.jobs)',
            'total_live_jobs': total_amz,
            'top_locations': {k: v for k, v in list(loc_facets.items())[:5]},
            'sample_jobs': [
                {
                    'title': j.get('title'),
                    'location': j.get('location'),
                    'url': f"https://www.amazon.jobs{j.get('job_path')}"
                } for j in jobs_amz[:2]
            ]
        }
        print(f"   -> Amazon Total Jobs: {total_amz}", flush=True)
    except Exception as e:
        print(f"   -> Amazon Error: {e}")

    # -----------------------------------------------------------------
    # 2. MICROSOFT INDIA
    # -----------------------------------------------------------------
    print("\n2. Auditing Microsoft India...", flush=True)
    try:
        url_ms = "https://apply.careers.microsoft.com/api/pcsx/search?domain=microsoft.com&query=&location=India&start=0&num=10"
        req = urllib.request.Request(url_ms, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://jobs.careers.microsoft.com/'})
        res = urllib.request.urlopen(req)
        data = json.loads(res.read().decode())
        total_ms = data.get('data', {}).get('count', 0)
        positions = data.get('data', {}).get('positions', [])
        
        report['Microsoft India'] = {
            'portal_source': 'Microsoft Careers Gateway (apply.careers.microsoft.com)',
            'total_live_jobs': total_ms,
            'sample_jobs': [
                {
                    'title': p.get('name'),
                    'location': p.get('location'),
                    'url': f"https://jobs.careers.microsoft.com/global/en/share/{p.get('id')}"
                } for p in positions[:2]
            ]
        }
        print(f"   -> Microsoft Total Jobs: {total_ms}", flush=True)
    except Exception as e:
        print(f"   -> Microsoft Error: {e}")

    # -----------------------------------------------------------------
    # 3. ORACLE INDIA
    # -----------------------------------------------------------------
    print("\n3. Auditing Oracle India...", flush=True)
    try:
        url_ora = "https://eeho.fa.us2.oraclecloud.com/hcmRestApi/resources/latest/recruitingCEJobRequisitions?onlyData=true&finder=findReqs;siteNumber=CX_45001,facetsList=LOCATIONS%3BTITLES,limit=10,locationId=300000000106965"
        req = urllib.request.Request(url_ora, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://careers.oracle.com/'})
        res = urllib.request.urlopen(req)
        data = json.loads(res.read().decode())
        total_ora = data.get('count', 0)
        items_ora = data.get('items', [])
        
        report['Oracle India'] = {
            'portal_source': 'Oracle Cloud HCM Official Gateway (careers.oracle.com)',
            'total_live_jobs': total_ora,
            'sample_jobs': [
                {
                    'title': it.get('Title'),
                    'location': it.get('PrimaryLocation'),
                    'url': f"https://careers.oracle.com/jobs/#en/sites/jobsearch/job/{it.get('Id')}"
                } for it in items_ora[:2]
            ]
        }
        print(f"   -> Oracle Total Jobs: {total_ora}", flush=True)
    except Exception as e:
        print(f"   -> Oracle Error: {e}")

    # -----------------------------------------------------------------
    # 4. COGNIZANT & HCLTECH VIA BROWSER DISCOVERY
    # -----------------------------------------------------------------
    print("\n4 & 5. Auditing Cognizant & HCLTech...", flush=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context()

        # Cognizant
        p_cog = context.new_page()
        p_cog.goto('https://careers.cognizant.com/india-en/jobs/?location=India', wait_until='domcontentloaded', timeout=25000)
        time.sleep(3)
        total_text_cog = p_cog.evaluate("""() => {
            const el = document.querySelector('.total-jobs, .search-count, [data-ph-id*="total-jobs"], h2');
            return el ? el.innerText : 'Available on portal';
        }""")
        report['Cognizant India'] = {
            'portal_source': 'Cognizant Careers Portal (careers.cognizant.com)',
            'portal_indicator': total_text_cog,
            'sample_url': 'https://careers.cognizant.com/india-en/jobs/'
        }
        print(f"   -> Cognizant status: {total_text_cog}")
        p_cog.close()

        # HCLTech
        p_hcl = context.new_page()
        p_hcl.goto('https://www.hcltech.com/careers/Careers-in-india', wait_until='domcontentloaded', timeout=25000)
        time.sleep(3)
        hcl_title = p_hcl.title()
        report['HCLTech'] = {
            'portal_source': 'HCLTech Official Careers (hcltech.com/careers)',
            'page_title': hcl_title,
            'sample_url': 'https://www.hcltech.com/careers/Careers-in-india'
        }
        print(f"   -> HCLTech status: {hcl_title}")
        p_hcl.close()

        browser.close()

    print("\n" + "=" * 85)
    print("AUDIT REPORT JSON:")
    print(json.dumps(report, indent=2))
    print("=" * 85)

if __name__ == "__main__":
    audit_5_companies()
