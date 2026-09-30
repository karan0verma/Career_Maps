import asyncio
from playwright.async_api import async_playwright

async def analyze():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        await page.goto("https://careers.wipro.com/search/", wait_until="networkidle")
        
        import re
        html = await page.content()
        csrf_token = None
        match = re.search(r'CSRFToken\s*=\s*["\']([^"\']+)["\']', html, re.IGNORECASE)
        if match:
            csrf_token = match.group(1)
            
        print("CSRF:", csrf_token)
        
        payload = {
            "locale": "en_US",
            "pageNumber": 0,
            "sortBy": "",
            "keywords": "",
            "location": "",
            "facetFilters": {},
            "categoryId": 0
        }
        
        res = await page.evaluate('''async ([url, token, payload]) => {
            let r = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'x-csrf-token': token,
                    'Accept': 'application/json, text/plain, */*'
                },
                body: JSON.stringify(payload)
            });
            return await r.json();
        }''', ["https://careers.wipro.com/services/recruiting/v1/jobs", csrf_token, payload])
        
        jobs = res.get("jobSearchResult", [])
        if jobs:
            print("Job keys:", jobs[0].keys())
            if "job" in jobs[0]:
                print("Job details:", jobs[0]["job"].keys())
            elif "title" in jobs[0]:
                print("Job has title at root level")
            print("Full first job object:")
            import json
            print(json.dumps(jobs[0], indent=2))
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(analyze())
