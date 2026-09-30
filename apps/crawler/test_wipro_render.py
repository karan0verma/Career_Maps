import time
from playwright.sync_api import sync_playwright

url = "https://careers.wipro.com/careers-home/jobs"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url, wait_until="networkidle", timeout=60000)
    time.sleep(10)
    html = page.content()
    
    with open("wipro_rendered.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    browser.close()
