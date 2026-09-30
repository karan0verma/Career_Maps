import time
from playwright.sync_api import sync_playwright

def inspect_1k_kirana():
    print("Initiating Deep Extraction for 1K Kirana Bazaar...")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            print("Navigating to https://www.1knetworks.com/careers...")
            response = page.goto("https://www.1knetworks.com/careers", wait_until="networkidle", timeout=30000)
            
            if response:
                print(f"Status: {response.status}")
                
            time.sleep(3)
            print("Extracting all links...")
            links = page.query_selector_all("a")
            job_links = []
            for l in links:
                href = l.get_attribute("href")
                text = l.inner_text().strip() if l.inner_text() else ""
                if href:
                    job_links.append((text, href))
            
            print(f"Found {len(job_links)} total links. Analyzing for job postings...")
            for text, href in job_links:
                if 'job' in href.lower() or 'apply' in href.lower() or 'career' in href.lower():
                    print(f"Potential Match: [{text}] -> {href}")
                    
            html = page.content()
            if "No openings" in html or "No jobs" in html:
                print("Text 'No openings' found in DOM.")
                
            browser.close()
    except Exception as e:
        print(f"Error during extraction: {e}")

if __name__ == "__main__":
    inspect_1k_kirana()
