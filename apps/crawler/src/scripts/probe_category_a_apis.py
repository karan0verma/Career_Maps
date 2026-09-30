import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

def probe_all_5():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        page = context.new_page()

        # 1. Google
        print("Probing Google Careers...", flush=True)
        page.goto("https://www.google.com/about/careers/applications/jobs/results/?location=India", wait_until='networkidle', timeout=30000)
        time.sleep(3)
        g_jobs = page.evaluate("""() => {
            const cards = Array.from(document.querySelectorAll('li[data-item-id], [class*="job-card"], [class*="Gz908b"], a[href*="jobs/results/"]'));
            return {
                cardCount: cards.length,
                sample: cards.slice(0, 3).map(c => c.innerText.trim())
            };
        }""")
        print("Google results:", g_jobs, flush=True)

        # 2. IBM
        print("\nProbing IBM Careers...", flush=True)
        page.goto("https://www.ibm.com/careers/search?field_keyword_08_bm%5B0%5D=India", wait_until='networkidle', timeout=30000)
        time.sleep(3)
        ibm_jobs = page.evaluate("""() => {
            const countEl = document.querySelector('[class*="results-count"], [class*="total"]');
            const links = Array.from(document.querySelectorAll('a[href*="/careers/"]')).filter(a => a.querySelector('h3, h2, div'));
            return {
                totalText: countEl ? countEl.innerText : '',
                linkCount: links.length,
                sample: links.slice(0, 3).map(l => ({ text: l.innerText.trim(), href: l.href }))
            };
        }""")
        print("IBM results:", ibm_jobs, flush=True)

        # 3. Adobe Workday
        print("\nProbing Adobe Workday...", flush=True)
        page.goto("https://adobe.wd5.myworkdayjobs.com/en-US/external_experienced?locations=bc33aa3152ec42d4995f4791a106ed09", wait_until='networkidle', timeout=30000)
        time.sleep(3)
        ad_jobs = page.evaluate("""() => {
            const countEl = document.querySelector('[data-automation-id="jobFoundText"], [class*="jobFound"]');
            const items = Array.from(document.querySelectorAll('a[data-automation-id="jobTitle"], a[href*="/job/"]'));
            return {
                totalText: countEl ? countEl.innerText : '',
                itemsCount: items.length,
                sample: items.slice(0, 3).map(a => ({ title: a.innerText.trim(), href: a.href }))
            };
        }""")
        print("Adobe results:", ad_jobs, flush=True)

        # 4. Cisco
        print("\nProbing Cisco...", flush=True)
        page.goto("https://jobs.cisco.com/jobs/SearchJobs/?21178=%5B169482%5D&21178_format=464&listFilterMode=1", wait_until='networkidle', timeout=30000)
        time.sleep(3)
        cisco_jobs = page.evaluate("""() => {
            const countEl = document.querySelector('.total-results, [class*="results"]');
            const rows = Array.from(document.querySelectorAll('tr[class*="job"], .job-item, a[href*="/jobs/ProjectDetail/"]'));
            return {
                totalText: countEl ? countEl.innerText : '',
                rowCount: rows.length,
                sample: rows.slice(0, 3).map(r => r.innerText.trim())
            };
        }""")
        print("Cisco results:", cisco_jobs, flush=True)

        # 5. Meta
        print("\nProbing Meta...", flush=True)
        page.goto("https://www.metacareers.com/jobs?locations[0]=Bangalore%2C%20India&locations[1]=Gurgaon%2C%20India&locations[2]=Hyderabad%2C%20India&locations[3]=Mumbai%2C%20India", wait_until='networkidle', timeout=30000)
        time.sleep(3)
        meta_jobs = page.evaluate("""() => {
            const links = Array.from(document.querySelectorAll('a[href*="/jobs/"]'));
            return {
                linkCount: links.length,
                sample: links.slice(0, 3).map(a => ({ text: a.innerText.trim(), href: a.href }))
            };
        }""")
        print("Meta results:", meta_jobs, flush=True)

        browser.close()

if __name__ == "__main__":
    probe_all_5()
