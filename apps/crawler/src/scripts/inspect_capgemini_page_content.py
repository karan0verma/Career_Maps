import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(channel='chrome', headless=True)
    page = browser.new_page()
    
    url = "https://careers.capgemini.com/job/Mumbai-%28ex-Bombay%29-Base24-Classic-Developer/1291375701/?feedId=388633&utm_source=CareerSite&tcsource=apply"
    print("Navigating to:", url)
    page.goto(url, wait_until='networkidle', timeout=20000)
    time.sleep(3)

    print("Final URL:", page.url)
    print("Page Title:", page.title())
    body_text = page.evaluate("() => document.body.innerText")
    print("Body text snippet:\n", body_text[:400])

    browser.close()
