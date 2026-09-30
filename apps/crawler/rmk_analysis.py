import asyncio
import json
from playwright.async_api import async_playwright

COMPANIES = [
    "https://careers.wipro.com/careers-home/jobs",
    "https://career.benteler.jobs/search/",
    "https://career.bizerba.com/search/",
    "https://career.celcom.com.my/search/",
    "https://career.deutsche-boerse.com/search/",
    "https://career.elm.sa/search/",
    "https://career.hipp.com/search/"
]

async def analyze_site(p, url):
    print(f"\n--- Analyzing {url} ---")
    browser = await p.chromium.launch(headless=True)
    context = await browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    page = await context.new_page()
    
    api_endpoints = []
    
    def handle_request(request):
        if 'api' in request.url.lower() or 'search' in request.url.lower() or 'graphql' in request.url.lower():
            if 'rmk' in request.url.lower() or 'json' in request.url.lower():
                api_endpoints.append(request.url)
    
    page.on("request", handle_request)
    
    try:
        await page.goto(url, wait_until="networkidle", timeout=25000)
        
        # Check for standard RMK elements
        rmk_search = await page.query_selector('.jobSearchResults')
        search_table = await page.query_selector('#searchresults')
        
        print(f"Has .jobSearchResults: {bool(rmk_search)}")
        print(f"Has #searchresults: {bool(search_table)}")
        
        if api_endpoints:
            print("Potential APIs:")
            for ep in list(set(api_endpoints))[:3]:
                print(f" - {ep}")
        else:
            print("No obvious API endpoints detected (likely SSR).")
            
        # Try to find jobs in the HTML
        job_links = await page.eval_on_selector_all('a[href*="/job/"]', "elements => elements.map(e => e.href)")
        print(f"Found {len(job_links)} job links in the DOM.")
        if job_links:
            print(f"Sample link: {job_links[0]}")
            
    except Exception as e:
        print(f"Error analyzing {url}: {e}")
    finally:
        await browser.close()

async def main():
    async with async_playwright() as p:
        for url in COMPANIES:
            await analyze_site(p, url)

if __name__ == "__main__":
    asyncio.run(main())
