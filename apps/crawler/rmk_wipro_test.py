import asyncio
from playwright.async_api import async_playwright

async def analyze():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        url = "https://careers.wipro.com/careers-home/jobs"
        print(f"Loading {url}...")
        await page.goto(url, wait_until="networkidle")
        
        # Look for custom RMK elements mentioned in verification
        elements = await page.query_selector_all('rmk-jobs-search, .rmk-jobs-search, [id*="rmk"]')
        print(f"Found {len(elements)} elements matching rmk-jobs-search")
        
        job_links = await page.eval_on_selector_all('a', "elements => elements.map(e => e.href).filter(href => href.includes('job') || href.includes('posting'))")
        print(f"Found {len(job_links)} potential job links")
        for link in job_links[:5]:
            print(f" - {link}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(analyze())
