import asyncio
from playwright.async_api import async_playwright

async def analyze():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        await page.goto("https://careers.wipro.com/search/", wait_until="networkidle")
        html = await page.content()
        import re
        matches = re.findall(r'.{0,50}csrf.{0,50}', html, re.IGNORECASE)
        for m in matches:
            print("MATCH:", m)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(analyze())
