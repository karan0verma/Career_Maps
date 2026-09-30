import asyncio
import json
from playwright.async_api import async_playwright

async def analyze():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        urls = ["https://careers.wipro.com/search/"]
        
        for url in urls:
            print(f"Loading {url}...")
            
            def handle_request(request):
                if request.resource_type in ["fetch", "xhr"]:
                    print(f"XHR/FETCH Request: {request.url}")
            
            def handle_response(response):
                if response.request.resource_type in ["fetch", "xhr"]:
                    print(f"XHR/FETCH Response {response.status}: {response.url}")
                    
            page.on("request", handle_request)
            page.on("response", handle_response)
            
            await page.goto(url, wait_until="networkidle")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(analyze())
