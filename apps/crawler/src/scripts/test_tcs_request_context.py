from playwright.sync_api import sync_playwright
import time
import json

with sync_playwright() as p:
    browser = p.chromium.launch(channel='chrome', headless=True)
    context = browser.new_context()
    page = context.new_page()
    page.goto('https://ibegin.tcsapps.com/candidate/#/jobs/search?geography=IN&language=EN', wait_until='networkidle', timeout=30000)
    time.sleep(2)
    
    # Use context.request to fetch multiple pages rapidly!
    all_jobs = []
    
    for page_num in range(1, 6):
        payload = {
            "jobCity": None,
            "jobSkill": None,
            "pageNumber": str(page_num),
            "userText": "",
            "jobTitleOrder": None,
            "jobCityOrder": None,
            "jobFunctionOrder": None,
            "jobExperienceOrder": None,
            "applyByOrder": None,
            "regular": True,
            "walkin": True
        }
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
            data = res.json().get('data', {})
            total_jobs = data.get('totalJobs')
            jobs = data.get('jobs', [])
            all_jobs.extend(jobs)
            print(f"Page {page_num}: Retrieved {len(jobs)} jobs (Total in DB: {total_jobs})", flush=True)
        else:
            print(f"Page {page_num} Error: {res.status}", flush=True)
            
    print(f"\nTotal jobs collected: {len(all_jobs)}", flush=True)
    for j in all_jobs[:3]:
        print(f"  • [{j.get('id')}] {j.get('jobTitle')} | {j.get('location')} | {j.get('functionName')}")
        
    browser.close()
