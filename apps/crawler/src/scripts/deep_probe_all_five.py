import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

def deep_probe():
    print("=" * 85)
    print("DEEP PROBING: MICROSOFT, ORACLE, COGNIZANT, HCLTECH, AMAZON")
    print("=" * 85, flush=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel='chrome',
            headless=True,
            args=['--no-sandbox', '--disable-blink-features=AutomationControlled']
        )
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            viewport={'width': 1440, 'height': 900}
        )

        # -------------------------------------------------------------
        # 1. MICROSOFT INDIA
        # -------------------------------------------------------------
        print("\n[1] Probing Microsoft India Portal...", flush=True)
        p_ms = context.new_page()
        ms_apis = []
        def on_ms_res(res):
            if ('api' in res.url or 'search' in res.url) and 'json' in res.headers.get('content-type', ''):
                try:
                    data = res.json()
                    ms_apis.append({'url': res.url, 'data': data})
                    print(f"  [MS API] {res.url[:100]} -> Keys: {list(data.keys()) if isinstance(data, dict) else len(data)}")
                except:
                    pass
        p_ms.on('response', on_ms_res)
        p_ms.goto('https://jobs.careers.microsoft.com/global/en/search?lc=India&l=en_us&pg=1&pgSz=20&o=Recent', wait_until='networkidle', timeout=30000)
        time.sleep(3)
        print(f"  Microsoft Page Title: {p_ms.title()}", flush=True)
        p_ms.close()

        # -------------------------------------------------------------
        # 2. COGNIZANT INDIA (Phenom)
        # -------------------------------------------------------------
        print("\n[2] Probing Cognizant India Portal...", flush=True)
        p_cog = context.new_page()
        cog_apis = []
        def on_cog_res(res):
            if ('api' in res.url or 'search' in res.url or 'jobs' in res.url or 'phenom' in res.url) and 'json' in res.headers.get('content-type', ''):
                try:
                    data = res.json()
                    cog_apis.append({'url': res.url, 'data': data})
                    print(f"  [Cognizant API] {res.url[:100]} -> Keys: {list(data.keys()) if isinstance(data, dict) else len(data)}")
                except:
                    pass
        p_cog.on('response', on_cog_res)
        p_cog.goto('https://careers.cognizant.com/india-en/jobs/?location=India', wait_until='networkidle', timeout=30000)
        time.sleep(3)
        print(f"  Cognizant Page Title: {p_cog.title()}", flush=True)
        p_cog.close()

        # -------------------------------------------------------------
        # 3. ORACLE INDIA (Oracle Cloud HCM)
        # -------------------------------------------------------------
        print("\n[3] Probing Oracle Careers Portal...", flush=True)
        p_ora = context.new_page()
        ora_apis = []
        def on_ora_res(res):
            if ('hcmRestApi' in res.url or 'recruiting' in res.url or 'jobs' in res.url or 'requisition' in res.url) and 'json' in res.headers.get('content-type', ''):
                try:
                    data = res.json()
                    ora_apis.append({'url': res.url, 'data': data})
                    print(f"  [Oracle API] {res.url[:100]} -> Keys: {list(data.keys()) if isinstance(data, dict) else len(data)}")
                except:
                    pass
        p_ora.on('response', on_ora_res)
        p_ora.goto('https://careers.oracle.com/jobs/#en/sites/jobsearch/requisitions?location=India&locationId=300000000106965', wait_until='networkidle', timeout=30000)
        time.sleep(3)
        print(f"  Oracle Page Title: {p_ora.title()}", flush=True)
        p_ora.close()

        # -------------------------------------------------------------
        # 4. HCLTECH PORTAL
        # -------------------------------------------------------------
        print("\n[4] Probing HCLTech Portal...", flush=True)
        p_hcl = context.new_page()
        hcl_apis = []
        def on_hcl_res(res):
            if ('job' in res.url.lower() or 'search' in res.url.lower() or 'api' in res.url.lower()) and 'json' in res.headers.get('content-type', ''):
                try:
                    data = res.json()
                    hcl_apis.append({'url': res.url, 'data': data})
                    print(f"  [HCLTech API] {res.url[:100]} -> Keys: {list(data.keys()) if isinstance(data, dict) else len(data)}")
                except:
                    pass
        p_hcl.on('response', on_hcl_res)
        p_hcl.goto('https://www.hcltech.com/careers/Careers-in-india', wait_until='networkidle', timeout=30000)
        time.sleep(3)
        print(f"  HCLTech Page Title: {p_hcl.title()}", flush=True)
        p_hcl.close()

        browser.close()

    print("\n" + "=" * 85)
    print("PROBE ROUND COMPLETED")
    print("=" * 85, flush=True)

if __name__ == "__main__":
    deep_probe()
