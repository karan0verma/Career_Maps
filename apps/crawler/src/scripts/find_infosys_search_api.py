import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

def find_search_api():
    print("=" * 75)
    print("TRIGGERING SEARCH ON INFOSYS CAREER PORTAL")
    print("=" * 75)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            viewport={'width': 1440, 'height': 900}
        )
        page = context.new_page()

        apis = []

        def on_req(req):
            if 'intapgateway' in req.url or 'careersci' in req.url or 'search' in req.url:
                print(f"[REQ] {req.method} {req.url}")
                if req.post_data:
                    print(f"      Data: {req.post_data}")
                apis.append({'method': req.method, 'url': req.url, 'data': req.post_data})

        def on_res(res):
            if 'intapgateway' in res.url or 'careersci' in res.url or 'search' in res.url:
                try:
                    data = res.json()
                    print(f"[RES] {res.status} {res.url}")
                    if isinstance(data, dict):
                        print(f"      Keys: {list(data.keys())}")
                        for k, v in data.items():
                            if isinstance(v, list) and len(v) > 0:
                                print(f"      '{k}' list count: {len(v)} | Sample: {v[0] if isinstance(v[0], dict) else v[:2]}")
                except Exception:
                    pass

        page.on('request', on_req)
        page.on('response', on_res)

        page.goto('https://career.infosys.com/joblist', wait_until='networkidle', timeout=40000)
        time.sleep(4)

        # Type in keyword and click search
        print("\nInteracting with search elements...")
        page.evaluate("""() => {
            const inputs = document.querySelectorAll('input');
            console.log('Found inputs:', inputs.length);
            const btn = document.querySelector('.search-btn, button[type="submit"], .btn-search, button');
            if (btn) btn.click();
        }""")
        time.sleep(5)

        # Check job listing page functionalAreaCount API directly
        # Let's inspect getJobList or search endpoints
        print("\nProbing common intapgateway endpoints...")
        test_urls = [
            "https://intapgateway.infosysapps.com/careersci/search/intapjbsrch/getHotJobsDetails?location=All%20locations&sourceId=1,21",
            "https://intapgateway.infosysapps.com/careersci/search/intapjbsrch/searchJobs",
            "https://intapgateway.infosysapps.com/careersci/search/intapjbsrch/getJobDetails",
            "https://intapgateway.infosysapps.com/careersci/search/intapjbsrch/jobListingPage/jobList",
            "https://intapgateway.infosysapps.com/careersci/search/intapjbsrch/v1/search"
        ]

        for u in test_urls:
            try:
                r = context.request.get(u, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Referer': 'https://career.infosys.com/',
                    'Origin': 'https://career.infosys.com'
                })
                print(f"[DIRECT GET] {u} -> Status: {r.status}")
                if r.status == 200:
                    try:
                        print("  Response:", str(r.json())[:300])
                    except:
                        pass
            except Exception as e:
                print(f"Error on {u}: {e}")

        browser.close()

if __name__ == "__main__":
    find_search_api()
