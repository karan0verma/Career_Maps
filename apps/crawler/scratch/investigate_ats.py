import asyncio
from playwright.async_api import async_playwright
import json
import logging

logging.basicConfig(level=logging.INFO)

companies = [
    "stripe.com",
    "openai.com",
    "cloudflare.com",
    "gitlab.com",
    "shopify.com",
    "discord.com",
    "framer.com",
    "canva.com",
    "airbnb.com",
    "doordash.com",
    "plaid.com",
    "lyft.com",
    "pinterest.com",
    "coinbase.com",
    "zoom.us",
    "hubspot.com"
]

career_urls = {
    "stripe.com": "https://stripe.com/jobs",
    "openai.com": "https://openai.com/careers/search",
    "cloudflare.com": "https://www.cloudflare.com/careers/jobs/",
    "gitlab.com": "https://about.gitlab.com/jobs/",
    "shopify.com": "https://www.shopify.com/careers/search",
    "discord.com": "https://discord.com/careers",
    "framer.com": "https://www.framer.com/careers/",
    "canva.com": "https://www.lifeatcanva.com/en",
    "airbnb.com": "https://careers.airbnb.com/",
    "doordash.com": "https://careers.doordash.com/",
    "plaid.com": "https://plaid.com/careers/",
    "lyft.com": "https://www.lyft.com/careers",
    "pinterest.com": "https://www.pinterestcareers.com/",
    "coinbase.com": "https://www.coinbase.com/careers",
    "zoom.us": "https://careers.zoom.us/",
    "hubspot.com": "https://www.hubspot.com/careers"
}

async def investigate(domain, url):
    print(f"\n--- Investigating {domain} ---")
    print(f"Target URL: {url}")
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            requests = []
            page.on("request", lambda request: requests.append(request.url))
            
            await page.goto(url, wait_until="networkidle", timeout=15000)
            
            final_url = page.url
            print(f"Final URL: {final_url}")
            
            content = await page.content()
            
            # Basic analysis
            ats_hints = {
                "Workday": ["myworkdayjobs.com", "workday"],
                "Greenhouse": ["boards.greenhouse.io", "api.greenhouse.io", "boards-api.greenhouse.io"],
                "Lever": ["jobs.lever.co", "api.lever.co"],
                "Ashby": ["jobs.ashbyhq.com", "api.ashbyhq.com"],
                "SmartRecruiters": ["smartrecruiters.com", "api.smartrecruiters.com"],
                "BambooHR": ["bamboohr.com"],
                "Jobvite": ["jobs.jobvite.com"],
                "Eightfold": ["eightfold.ai"]
            }
            
            found_ats = []
            
            for ats, hints in ats_hints.items():
                for hint in hints:
                    if hint in final_url or hint in content.lower():
                        found_ats.append(ats)
                        break
                    for req in requests:
                        if hint in req.lower():
                            found_ats.append(ats)
                            break
                    if ats in found_ats: break
            
            print(f"Detected ATS Hints: {found_ats}")
            
            # Print some network requests to see API calls
            api_requests = [r for r in requests if "api" in r or "graphql" in r or "jobs" in r][:5]
            print(f"Interesting Network Requests: {api_requests}")
            
            await browser.close()
    except Exception as e:
        print(f"Error investigating {domain}: {e}")

async def main():
    for domain in companies:
        url = career_urls.get(domain, f"https://{domain}/careers")
        await investigate(domain, url)

if __name__ == "__main__":
    asyncio.run(main())
