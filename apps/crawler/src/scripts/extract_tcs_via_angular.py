from playwright.sync_api import sync_playwright
import time
import json

print("Extracting TCS jobs via Angular service context...", flush=True)

with sync_playwright() as p:
    browser = p.chromium.launch(channel='chrome', headless=True)
    page = browser.new_page()
    page.goto('https://ibegin.tcsapps.com/candidate/#/jobs/search?geography=IN&language=EN', wait_until='networkidle', timeout=30000)
    time.sleep(4)
    
    # Use Angular $http directly
    res = page.evaluate('''() => {
        return new Promise((resolve, reject) => {
            try {
                const el = angular.element(document.querySelector('[ng-controller]') || document.body);
                const $http = el.injector().get('$http');
                const payload = {
                    userText: '',
                    pageNumber: '1',
                    jobTitle: null,
                    jobCity: null,
                    jobFunction: null,
                    jobExperience: null,
                    jobSkill: null,
                    walkin: null,
                    regular: null
                };
                $http.post('api/v1/jobs/searchJ', payload).then(
                    (response) => resolve(response.data),
                    (error) => reject(error)
                );
            } catch (err) {
                reject(err.toString());
            }
        });
    }''')
    
    print("\nResult from Angular evaluate:", type(res), res, flush=True)
    if isinstance(res, dict):
        data = res.get('data', {})
        print("Total Jobs in TCS Database:", data.get('totalJobs'), flush=True)
        jobs = data.get('jobs', [])
        print(f"Jobs returned in page 1: {len(jobs)}", flush=True)
        for j in jobs[:5]:
            print(f"  • [{j.get('id')}] {j.get('jobTitle')} | {j.get('location')} | Exp: {j.get('experience')} | Skills: {j.get('skills')}", flush=True)
        
    browser.close()
