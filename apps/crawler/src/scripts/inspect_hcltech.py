import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

def inspect_hcl():
    print("=" * 80)
    print("INSPECTING HCLTECH SAP SUCCESSFACTORS SEARCH PORTAL")
    print("=" * 80, flush=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        page = context.new_page()

        url = "https://careers.hcltech.com/search/?locationsearch=India"
        print(f"Navigating to {url}", flush=True)
        page.goto(url, wait_until='networkidle', timeout=30000)
        time.sleep(3)

        # Total count
        total_text = page.evaluate("""() => {
            const el = document.querySelector('.pagination-label, .search-count, [class*="results"], [class*="count"]');
            return el ? el.innerText : '';
        }""")
        print("HCLTech Total Count Text:", total_text)

        # Extract table rows
        rows = page.evaluate("""() => {
            const trs = Array.from(document.querySelectorAll('tr.data-row, table tbody tr, .job-tile'));
            return trs.map(tr => {
                const link = tr.querySelector('a.jobTitle-link, a');
                const loc = tr.querySelector('.jobLocation, .location, [class*="location"]');
                const dept = tr.querySelector('.jobDepartment, .department, [class*="department"]');
                const date = tr.querySelector('.jobDate, .date, [class*="date"]');
                return {
                    title: link ? link.innerText.trim() : '',
                    url: link ? link.href : '',
                    location: loc ? loc.innerText.trim() : '',
                    department: dept ? dept.innerText.trim() : '',
                    date: date ? date.innerText.trim() : ''
                };
            }).filter(r => r.title && r.url);
        }""")
        print(f"Captured {len(rows)} HCLTech jobs on page 1:")
        for r in rows[:5]:
            print("  ", r)

        browser.close()

if __name__ == "__main__":
    inspect_hcl()
