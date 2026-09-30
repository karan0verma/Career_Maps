from playwright.sync_api import sync_playwright

def print_table():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://careers.techmahindra.com/CurrentOpportunity.aspx", wait_until="networkidle")
        
        table = page.query_selector("table")
        if table:
            print("Table content preview:")
            print(table.inner_text()[:500])
        else:
            print("No table found")
            print(page.content()[:1000])
        
        browser.close()

if __name__ == "__main__":
    print_table()
