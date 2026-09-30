from playwright.sync_api import sync_playwright
import time
import json

with sync_playwright() as p:
    browser = p.chromium.launch(channel='chrome', headless=True)
    page = browser.new_page()
    page.goto('https://ibegin.tcsapps.com/candidate/#/jobs/search?geography=IN&language=EN', wait_until='networkidle', timeout=30000)
    time.sleep(3)
    
    # Test batch fetching pages 1 to 5 via browser evaluate
    res = page.evaluate('''async () => {
        const results = [];
        const el = angular.element(document.querySelector('[ng-controller]') || document.body);
        const $http = el.injector().get('$http');
        
        for (let p = 1; p <= 5; p++) {
            const payload = {
                userText: '',
                pageNumber: p.toString(),
                jobTitle: null,
                jobCity: null,
                jobFunction: null,
                jobExperience: null,
                jobSkill: null,
                walkin: null,
                regular: null
            };
            try {
                const resp = await $http.post(`api/v1/jobs/searchJ?at=${Date.now()}`, payload);
                if (resp && resp.data && resp.data.data && resp.data.data.jobs) {
                    results.push(...resp.data.data.jobs);
                }
            } catch (e) {
                console.error("Error at page", p, e);
            }
        }
        return results;
    }''')
    
    print(f"Successfully batch fetched {len(res)} jobs across 5 pages!", flush=True)
    for j in res[:3]:
        print(f"  - {j.get('id')}: {j.get('jobTitle')} | {j.get('location')}")
    browser.close()
