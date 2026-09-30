import asyncio
from playwright.async_api import async_playwright

async def analyze():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        urls = ["https://careers.wipro.com/search/", "https://career.benteler.jobs/search/"]
        
        for url in urls:
            print(f"Loading {url}...")
            await page.goto(url, wait_until="networkidle")
            
            search_table = await page.query_selector('#searchresults')
            if search_table:
                html = await search_table.inner_html()
                print(f"Found #searchresults with {len(html)} bytes")
                
                rows = await page.query_selector_all('tr.data-row')
                print(f"Found {len(rows)} data-row elements")
                if rows:
                    text = await rows[0].inner_text()
                    print(f"Sample row:\n{text}")
            else:
                print("No #searchresults found.")
                # Maybe Wipro uses a different CSS class like .jobSearchResults?
                el = await page.query_selector('.jobSearchResults, .jobs-list')
                if el:
                    print(f"Found fallback selector.")
                else:
                    body = await page.evaluate("document.body.innerHTML")
                    print(f"Body snippet: {body[:200]}")
                    
        await browser.close()

if __name__ == "__main__":
    asyncio.run(analyze())
