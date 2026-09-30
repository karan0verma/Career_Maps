from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://careers.ibm.com/search/?search=India")
    page.wait_for_timeout(5000)
    jobs = page.evaluate("""() => {
        return Array.from(document.querySelectorAll('a[href*="/job/"]')).map(a => {
            return {title: a.innerText, url: a.href}
        }).filter(j => j.title.trim().length > 0)
    }""")
    print(jobs[:5])
    browser.close()
