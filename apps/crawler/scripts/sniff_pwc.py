from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.on("response", lambda r: print(r.url) if 'cxs' in r.url or 'jobs' in r.url else None)
    try:
        page.goto("https://pwc.wd3.myworkdayjobs.com/Global_Careers", wait_until='networkidle')
        page.wait_for_timeout(3000)
    except Exception as e:
        print(e)
    browser.close()
