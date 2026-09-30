import asyncio
from playwright.async_api import async_playwright

async def analyze():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        url = "https://careers.wipro.com/careers-home/jobs"
        print(f"Loading {url}...")
        await page.goto(url, wait_until="networkidle")
        
        content = await page.content()
        with open('wipro_jobs.html', 'w', encoding='utf-8') as f:
            f.write(content)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(analyze())
