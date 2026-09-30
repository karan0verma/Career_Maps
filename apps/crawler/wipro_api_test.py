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
                if 'v1/jobs' in request.url:
                    print(f"\n--- API REQUEST ---")
                    print(f"Method: {request.method}")
                    print(f"Headers: {request.headers}")
                    print(f"Post Data: {request.post_data}")
            
            async def handle_response(response):
                if 'v1/jobs' in response.url:
                    print(f"\n--- API RESPONSE ({response.status}) ---")
                    try:
                        data = await response.json()
                        print(f"Data snippet: {str(data)[:300]}")
                    except Exception as e:
                        print(f"Could not parse JSON: {e}")
                    
            page.on("request", handle_request)
            page.on("response", handle_response)
            
            await page.goto(url, wait_until="networkidle")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(analyze())
