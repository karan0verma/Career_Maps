from playwright.sync_api import sync_playwright

def find_ntpc_jobs():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(ignore_https_errors=True)
        
        page.goto("https://careers.ntpc.co.in/recruitment/", timeout=15000)
        
        # Look for PDF links or job postings
        links = page.locator("a").all()
        for link in links:
            href = link.get_attribute("href")
            text = link.inner_text().strip()
            if href and ('advt' in href.lower() or '.pdf' in href.lower() or 'recruitment' in href.lower()):
                if text:
                    print(f"[{text}] -> {href}")
                    
        browser.close()

if __name__ == "__main__":
    find_ntpc_jobs()
