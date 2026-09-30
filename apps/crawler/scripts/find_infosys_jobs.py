from playwright.sync_api import sync_playwright

def find_jobs_pw():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        page.goto("https://career.infosys.com/joblist", wait_until="networkidle")
        page.wait_for_timeout(5000)
        
        html = page.content()
        import re
        codes = re.findall(r'jobReferenceCode=([a-zA-Z0-9-]+)', html)
        print("Found job codes:", list(set(codes)))
        
        browser.close()

if __name__ == "__main__":
    find_jobs_pw()
