from playwright.sync_api import sync_playwright

def inspect_ntpc():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(ignore_https_errors=True)
        
        try:
            print("Navigating to NTPC...")
            page.goto("https://careers.ntpc.co.in/recruitment/", timeout=15000)
            print("Title:", page.title())
            html = page.content()
            print("HTML length:", len(html))
        except Exception as e:
            print("Error:", e)
            
        try:
            print("Trying https://ntpccareers.net/")
            page.goto("https://ntpccareers.net/", timeout=15000)
            print("Title:", page.title())
        except Exception as e:
            print("Error:", e)
            
        browser.close()

if __name__ == "__main__":
    inspect_ntpc()
