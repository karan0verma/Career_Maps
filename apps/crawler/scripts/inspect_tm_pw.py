from playwright.sync_api import sync_playwright

def inspect_tm_pw():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://careers.techmahindra.com/CurrentOpportunity.aspx")
        page.wait_for_timeout(3000)
        
        # See if there's a table of jobs
        links = page.locator("a").all()
        for link in links:
            href = link.get_attribute("href")
            text = link.inner_text().strip()
            if href and ('Job' in href or 'Opportunity' in href or 'javascript' in href):
                print(f"[{text}] -> {href}")
                
        browser.close()

if __name__ == "__main__":
    inspect_tm_pw()
