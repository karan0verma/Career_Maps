from playwright.sync_api import sync_playwright
import time
import json

with sync_playwright() as p:
    browser = p.chromium.launch(channel='chrome', headless=True)
    page = browser.new_page()
    page.goto('https://ibegin.tcsapps.com/candidate/#/jobs/search?geography=IN&language=EN', wait_until='networkidle', timeout=30000)
    time.sleep(4)
    
    # Test page-by-page fetching with JobSearchService
    res = page.evaluate('''async () => {
        const el = angular.element(document.body);
        const Cache = el.injector().get('Cache');
        const JobSearchService = el.injector().get('JobSearchService');
        const $rootScope = el.injector().get('$rootScope');
        
        const fetchPage = (pageNum) => {
            return new Promise((resolve) => {
                const off = $rootScope.$on('SolrResponseSuccessful', () => {
                    off();
                    const data = Cache.get('job-search-result');
                    resolve(data ? data.jobList : []);
                });
                JobSearchService.searchResult({
                    pageNumber: pageNum.toString(),
                    userText: '',
                    jobTitle: null,
                    jobCity: null,
                    jobFunction: null,
                    jobExperience: null,
                    jobSkill: null,
                    walkin: null,
                    regular: null
                });
            });
        };
        
        const allFetched = [];
        for (let p = 1; p <= 5; p++) {
            const list = await fetchPage(p);
            allFetched.push(...list);
        }
        return allFetched;
    }''')
    
    print(f"Successfully fetched {len(res)} jobs across 5 pages!", flush=True)
    for j in res[:5]:
        print(f"  • [{j.get('jobId')}] {j.get('title')} | {j.get('location')} | {j.get('jobfunction')} | {j.get('experience')} Yrs | Skills: {j.get('skills')}")
    browser.close()
