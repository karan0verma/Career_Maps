import os
import sys
import json
import time
import urllib.request
import urllib.parse
from playwright.sync_api import sync_playwright

def probe_all_five():
    print("=" * 85)
    print("PROBING 5 TARGET COMPANIES: HCLTECH, COGNIZANT, MICROSOFT, AMAZON, ORACLE")
    print("=" * 85, flush=True)

    results = {}

    # -------------------------------------------------------------
    # 1. MICROSOFT INDIA (Direct REST API)
    # -------------------------------------------------------------
    print("\n[1/5] Probing Microsoft India Careers API...", flush=True)
    try:
        # Microsoft global career search API
        ms_url = "https://jobs.careers.microsoft.com/api/v1/search?lc=India&l=en_us&pg=1&pgSz=20"
        req = urllib.request.Request(ms_url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://jobs.careers.microsoft.com/global/en/search'
        })
        res = urllib.request.urlopen(req, timeout=15)
        ms_data = json.loads(res.read().decode())
        total_ms = ms_data.get('operationResult', {}).get('result', {}).get('totalJobs', 0)
        jobs_ms = ms_data.get('operationResult', {}).get('result', {}).get('jobs', [])
        print(f"  -> Microsoft India Live Jobs: {total_ms} positions found!", flush=True)
        results['Microsoft'] = {
            'status': 'SUCCESS',
            'total_jobs': total_ms,
            'endpoint': ms_url,
            'sample_jobs': jobs_ms[:3]
        }
    except Exception as e:
        print(f"  -> Microsoft error: {e}", flush=True)
        results['Microsoft'] = {'status': 'ERROR', 'error': str(e)}

    # -------------------------------------------------------------
    # 2. AMAZON INDIA (Direct REST API)
    # -------------------------------------------------------------
    print("\n[2/5] Probing Amazon India Careers API...", flush=True)
    try:
        amz_url = "https://www.amazon.jobs/en/search.json?country=IND&facets%5B%5D=location&facets%5B%5D=business_category&facets%5B%5D=category&facets%5B%5D=schedule_type_id&facets%5B%5D=employee_class&facets%5B%5D=normalized_location&facets%5B%5D=job_function_id&offset=0&result_limit=10"
        req = urllib.request.Request(amz_url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.amazon.jobs/en/search?loc_country=IND'
        })
        res = urllib.request.urlopen(req, timeout=15)
        amz_data = json.loads(res.read().decode())
        total_amz = amz_data.get('hits', 0)
        jobs_amz = amz_data.get('jobs', [])
        print(f"  -> Amazon India Live Jobs: {total_amz} positions found!", flush=True)
        results['Amazon'] = {
            'status': 'SUCCESS',
            'total_jobs': total_amz,
            'endpoint': amz_url,
            'sample_jobs': jobs_amz[:3]
        }
    except Exception as e:
        print(f"  -> Amazon error: {e}", flush=True)
        results['Amazon'] = {'status': 'ERROR', 'error': str(e)}

    # -------------------------------------------------------------
    # 3. ORACLE INDIA (Eightfold / Cloud HCM API)
    # -------------------------------------------------------------
    print("\n[3/5] Probing Oracle India Careers API...", flush=True)
    try:
        # Oracle uses Eightfold API: https://oracle.eightfold.ai/api/apply/v2/jobs?domain=oracle.com&location=India
        oracle_url = "https://oracle.eightfold.ai/api/apply/v2/jobs?domain=oracle.com&location=India&num=10&start=0"
        req = urllib.request.Request(oracle_url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://oracle.eightfold.ai/careers?domain=oracle.com'
        })
        res = urllib.request.urlopen(req, timeout=15)
        oracle_data = json.loads(res.read().decode())
        total_oracle = oracle_data.get('count', 0)
        jobs_oracle = oracle_data.get('positions', [])
        print(f"  -> Oracle India Live Jobs: {total_oracle} positions found!", flush=True)
        results['Oracle'] = {
            'status': 'SUCCESS',
            'total_jobs': total_oracle,
            'endpoint': oracle_url,
            'sample_jobs': jobs_oracle[:3]
        }
    except Exception as e:
        print(f"  -> Oracle error: {e}", flush=True)
        results['Oracle'] = {'status': 'ERROR', 'error': str(e)}

    # -------------------------------------------------------------
    # 4 & 5. HCLTECH & COGNIZANT (Browser-Assisted Network Interceptor)
    # -------------------------------------------------------------
    print("\n[4 & 5] Probing HCLTech & Cognizant with Real Browser Engine...", flush=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

        # 4. HCLTech
        print("  -> Probing HCLTech Portal (https://www.hcltech.com/careers)...", flush=True)
        p_hcl = context.new_page()
        hcl_apis = []
        p_hcl.on('response', lambda r: hcl_apis.append(r.url) if ('job' in r.url.lower() or 'search' in r.url.lower() or 'api' in r.url.lower()) and 'json' in r.headers.get('content-type', '') else None)
        try:
            p_hcl.goto('https://www.hcltech.com/careers/Careers-in-india', wait_until='domcontentloaded', timeout=25000)
            time.sleep(3)
            print(f"     HCLTech Title: {p_hcl.title()} | Captured {len(hcl_apis)} JSON endpoints")
        except Exception as e:
            print(f"     HCLTech probe note: {e}")
        p_hcl.close()

        # 5. Cognizant
        print("  -> Probing Cognizant Portal (https://careers.cognizant.com/global/en)...", flush=True)
        p_cog = context.new_page()
        cog_apis = []
        p_cog.on('response', lambda r: cog_apis.append(r.url) if ('job' in r.url.lower() or 'search' in r.url.lower() or 'api' in r.url.lower()) and 'json' in r.headers.get('content-type', '') else None)
        try:
            p_cog.goto('https://careers.cognizant.com/india-en/jobs/', wait_until='domcontentloaded', timeout=25000)
            time.sleep(3)
            print(f"     Cognizant Title: {p_cog.title()} | Captured {len(cog_apis)} JSON endpoints")
        except Exception as e:
            print(f"     Cognizant probe note: {e}")
        p_cog.close()

        browser.close()

    print("\n" + "=" * 85)
    print("PROBE COMPLETED SUCCESSFULLY")
    print("=" * 85, flush=True)

if __name__ == "__main__":
    probe_all_five()
