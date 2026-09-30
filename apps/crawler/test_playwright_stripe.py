from playwright.sync_api import sync_playwright
import re

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://stripe.com/in/careers', wait_until="networkidle")
    html = page.content()
    browser.close()
    
    matches = set(re.findall(r'https?://[^\s"\'<>]+', html))
    ats_urls = [m for m in matches if any(x in m.lower() for x in ['lever', 'greenhouse', 'ashby', 'workday', 'smartrecruiters', 'eightfold', 'jobvite', 'bamboohr'])]
    print("Playwright ATS URLs for Stripe:", ats_urls)
