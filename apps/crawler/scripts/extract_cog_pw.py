from playwright.sync_api import sync_playwright
import time

def extract_cog():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://careers.cognizant.com/india-en/jobs/")
        
        try:
            page.wait_for_selector(".ph-job-list li", timeout=15000)
        except:
            try:
                page.wait_for_selector(".jobs-list-item", timeout=10000)
            except:
                pass
                
        print("URL:", page.url)
        
        links = page.query_selector_all("a")
        found = []
        for l in links:
            href = l.get_attribute("href")
            if href and '/jobs/' in href and '-' in href and not href.endswith('/jobs/'):
                found.append(href)
                
        print("Found Job Links:", len(set(found)))
        if found:
            print(found[:3])
            
        browser.close()

if __name__ == "__main__":
    extract_cog()
