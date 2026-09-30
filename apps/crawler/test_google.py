from playwright.sync_api import sync_playwright

def test():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print("Navigating to https://www.google.com/about/careers/applications/jobs/results/ ...")
        page.goto("https://www.google.com/about/careers/applications/jobs/results/")
        page.wait_for_load_state("networkidle")
        
        # Save HTML
        with open("google_jobs.html", "w", encoding="utf-8") as f:
            f.write(page.content())
            
        # Take a screenshot
        page.screenshot(path="google_jobs_page.png")
        print("Done. Saved google_jobs.html and google_jobs_page.png")
        browser.close()

if __name__ == "__main__":
    test()
