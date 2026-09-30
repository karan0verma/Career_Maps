from playwright.sync_api import sync_playwright

def search_ntpc():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://duckduckgo.com/?q=NTPC+careers+current+openings&t=h_&ia=web")
        page.wait_for_timeout(3000)
        
        links = page.locator("a.result__url").all()
        for link in links:
            print(link.get_attribute("href"))
            
        browser.close()

if __name__ == "__main__":
    search_ntpc()
