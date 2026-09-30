from playwright.sync_api import sync_playwright

def inspect_cell():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://careers.techmahindra.com/CurrentOpportunity.aspx", wait_until="networkidle")
        
        cells = page.query_selector_all("td")
        for cell in cells:
            html = cell.inner_html()
            if "Project Manager" in html:
                print(html)
                break
        
        browser.close()

if __name__ == "__main__":
    inspect_cell()
