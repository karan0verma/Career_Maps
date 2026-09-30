import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

def inspect_hcl_all():
    print("=" * 80)
    print("INSPECTING HCLTECH SAP SUCCESSFACTORS SEARCH PORTAL (ALL 9,280+ JOBS)")
    print("=" * 80, flush=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        page = context.new_page()

        # Let's test the main search URL
        url = "https://careers.hcltech.com/search/?q="
        print(f"Navigating to {url}...", flush=True)
        page.goto(url, wait_until='networkidle', timeout=35000)
        time.sleep(3)

        # Look for search results count and table
        result_info = page.evaluate("""() => {
            const countEl = document.querySelector('.pagination-label, .search-count, [class*="results"], [class*="count"]');
            const totalText = countEl ? countEl.innerText.trim() : '';
            
            const rows = Array.from(document.querySelectorAll('tr.data-row, table tbody tr, .job-tile')).map(tr => {
                const a = tr.querySelector('a.jobTitle-link, a[href*="/job/"]');
                const loc = tr.querySelector('.jobLocation, .location, [class*="location"]');
                const dept = tr.querySelector('.jobDepartment, .department, [class*="department"]');
                const date = tr.querySelector('.jobDate, .date, [class*="date"]');
                const shId = tr.querySelector('.jobShId, [class*="shId"]');
                return {
                    title: a ? a.innerText.trim() : '',
                    href: a ? a.href : '',
                    location: loc ? loc.innerText.trim() : '',
                    dept: dept ? dept.innerText.trim() : '',
                    date: date ? date.innerText.trim() : ''
                };
            }).filter(r => r.title && r.href);

            // Also check all links on page
            const allJobLinks = Array.from(document.querySelectorAll('a[href*="/job/"]')).map(a => ({
                text: a.innerText.trim(),
                href: a.href
            }));

            // Check pagination links
            const paginationLinks = Array.from(document.querySelectorAll('a[href*="startrow="], a.pagination-link, ul.pagination a')).map(a => ({
                text: a.innerText.trim(),
                href: a.href
            }));

            return {
                totalText,
                rowCount: rows.length,
                sampleRows: rows.slice(0, 5),
                allJobLinksCount: allJobLinks.length,
                sampleLinks: allJobLinks.slice(0, 5),
                paginationLinks
            };
        }""")

        print("\nResult Info from HCLTech Search:")
        print("  Total Text:", result_info['totalText'])
        print("  Row Count:", result_info['rowCount'])
        print("  Sample Rows:", json.dumps(result_info['sampleRows'], indent=2))
        print("  All Job Links Count:", result_info['allJobLinksCount'])
        print("  Sample Links:", json.dumps(result_info['sampleLinks'], indent=2))
        print("  Pagination Links:", json.dumps(result_info['paginationLinks'], indent=2))

        browser.close()

if __name__ == "__main__":
    inspect_hcl_all()
