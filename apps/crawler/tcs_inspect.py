import time
from playwright.sync_api import sync_playwright

def inspect():
    with sync_playwright() as p:
        print("Launching browser...")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print("Navigating to TCS careers...")
        page.goto("https://www.tcs.com/careers", timeout=60000)
        time.sleep(5)
        print("Page title:", page.title())
        
        # Look for job links or common job card selectors
        links = page.query_selector_all("a")
        for link in links[:20]:
            href = link.get_attribute("href")
            text = link.inner_text().strip()
            if text:
                print(f"Link: {text} -> {href}")
                
        # Dump some HTML
        with open("tcs_dom.html", "w", encoding="utf-8") as f:
            f.write(page.content())
            
        print("Wrote DOM to tcs_dom.html")
        browser.close()

if __name__ == "__main__":
    inspect()
