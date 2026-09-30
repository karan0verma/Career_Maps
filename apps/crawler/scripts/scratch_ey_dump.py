from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("https://careers.ey.com/experienced/go/Careers-in-India/3468501/")
    page.wait_for_timeout(5000)
    
    html = page.content()
    with open("ey_dump.html", "w", encoding="utf-8") as f:
        f.write(html)
        
    print("HTML dumped successfully")
    browser.close()
