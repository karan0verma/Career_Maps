import os
import sys
import json
import urllib.request
from playwright.sync_api import sync_playwright

def probe_hcl_cog():
    print("=" * 85)
    print("EXTRACTING LIVE JOB TOTALS FOR HCLTECH, COGNIZANT, ORACLE, MICROSOFT, AMAZON")
    print("=" * 85, flush=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

        # 1. HCLTech
        p_hcl = context.new_page()
        hcl_data = None
        def on_hcl_resp(r):
            nonlocal hcl_data
            if 'services/recruiting/v1/jobs' in r.url or 'jobSearchResult' in r.url:
                try:
                    hcl_data = r.json()
                    print(f"Captured HCL JSON: {list(hcl_data.keys())}", flush=True)
                except:
                    pass
        p_hcl.on('response', on_hcl_resp)
        p_hcl.goto('https://careers.hcltech.com/search/?createNewAlert=false&q=&locationsearch=India', wait_until='networkidle', timeout=30000)
        
        # Check text count
        hcl_count_text = p_hcl.evaluate("""() => {
            const el = document.querySelector('.paginationSummary, .search-results, .totalJobs, h1, h2');
            return el ? el.innerText : '';
        }""")
        print(f"HCLTech Page Indicator: {hcl_count_text}", flush=True)
        if hcl_data:
            print(f"HCLTech Total from API: {hcl_data.get('totalJobs', len(hcl_data))}", flush=True)
        p_hcl.close()

        # 2. Cognizant
        p_cog = context.new_page()
        cog_data = None
        def on_cog_resp(r):
            nonlocal cog_data
            if ('api' in r.url or 'search' in r.url or 'jobs' in r.url) and 'json' in r.headers.get('content-type', ''):
                try:
                    data = r.json()
                    if 'job' in str(data).lower() or 'total' in str(data).lower():
                        cog_data = data
                        print(f"Captured Cognizant JSON from {r.url[:80]}", flush=True)
                except:
                    pass
        p_cog.on('response', on_cog_resp)
        p_cog.goto('https://careers.cognizant.com/global/en/search-results?location=India', wait_until='networkidle', timeout=30000)
        cog_count_text = p_cog.evaluate("""() => {
            const el = document.querySelector('.total-jobs, .search-count, [data-ph-id*="total-jobs"], h2');
            return el ? el.innerText : '';
        }""")
        print(f"Cognizant Page Indicator: {cog_count_text}", flush=True)
        p_cog.close()

        # 3. Oracle India Total Count
        p_ora = context.new_page()
        ora_data = None
        def on_ora_resp(r):
            nonlocal ora_data
            if 'recruitingCEJobRequisitions' in r.url:
                try:
                    ora_data = r.json()
                    print(f"Captured Oracle Requisitions: Count={ora_data.get('count')}, Items={len(ora_data.get('items', []))}", flush=True)
                except:
                    pass
        p_ora.on('response', on_ora_resp)
        p_ora.goto('https://careers.oracle.com/jobs/#en/sites/jobsearch/requisitions?location=India&locationId=300000000106965', wait_until='networkidle', timeout=30000)
        ora_count_text = p_ora.evaluate("""() => {
            const el = document.querySelector('.search-results-count, .results-count, h1, h2');
            return el ? el.innerText : '';
        }""")
        print(f"Oracle Page Indicator: {ora_count_text}", flush=True)
        p_ora.close()

        browser.close()

if __name__ == "__main__":
    probe_hcl_cog()
