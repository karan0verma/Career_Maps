import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

def inspect_hcl_india():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        page = context.new_page()

        page.goto('https://careers.hcltech.com/go/India/9553955/', wait_until='networkidle', timeout=30000)
        time.sleep(3)

        # Extract job cards
        jobs = page.evaluate("""() => {
            const results = [];
            const rows = document.querySelectorAll('tr.data-row, table tbody tr, .job-tile');
            rows.forEach(r => {
                const titleA = r.querySelector('a.jobTitle-link, a');
                const loc = r.querySelector('.jobLocation, .location, [class*="location"]');
                const dept = r.querySelector('.jobDepartment, .department, [class*="department"]');
                const date = r.querySelector('.jobDate, .date, [class*="date"]');
                if (titleA && titleA.href.includes('/job/')) {
                    results.push({
                        title: titleA.innerText.trim(),
                        url: titleA.href,
                        location: loc ? loc.innerText.trim() : 'India',
                        dept: dept ? dept.innerText.trim() : '',
                        date: date ? date.innerText.trim() : ''
                    });
                }
            });
            return results;
        }""")
        print(f"Captured {len(jobs)} HCLTech India positions on page 1:", flush=True)
        for j in jobs[:5]:
            print(f"  • {j['title']} | {j['location']} | {j['url']}", flush=True)

        browser.close()

if __name__ == "__main__":
    inspect_hcl_india()
