import time
from playwright.sync_api import sync_playwright

def find_jobs():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://mycareer.hsbc.com/en_GB/external", wait_until="networkidle")
        time.sleep(5)
        
        links = page.query_selector_all("a")
        found = []
        for l in links:
            href = l.get_attribute("href")
            text = l.inner_text().strip()
            if href and 'job' in href.lower():
                found.append((text, href))
                
        with open("hsbc_found.txt", "w", encoding="utf-8") as f:
            for title, url in found:
                f.write(f"{title}: {url}\n")
                
        browser.close()

if __name__ == "__main__":
    find_jobs()
