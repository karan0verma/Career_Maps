from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print("Navigating to microsoft careers...")
        page.goto("https://jobs.careers.microsoft.com/global/en/search", timeout=60000)
        page.wait_for_timeout(5000)
        
        # Try to find elements
        print("Page title:", page.title())
        
        # Print a snippet of HTML to find the jobs
        print(page.content()[:1000])
        
        # Let's try to query buttons, links or some job container
        print("Finding potential job cards...")
        cards = page.query_selector_all('div[role="listitem"], .ms-List-cell, .job-item, a, div[aria-label]')
        for i, card in enumerate(cards[:20]):
            try:
                print(f"Card {i} text: {card.inner_text()[:100].strip()}")
                print(f"Card {i} class: {card.get_attribute('class')}")
            except:
                pass
                
        browser.close()

if __name__ == "__main__":
    run()
