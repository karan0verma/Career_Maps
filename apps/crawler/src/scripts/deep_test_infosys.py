import os
import sys
import time
from playwright.sync_api import sync_playwright

def deep_test_infosys():
    print("=" * 80)
    print("DEEP INVESTIGATION: WHY INFOSYS DIRECT URL RENDERS BLANK IN USER BROWSER")
    print("=" * 80)

    urls_to_test = [
        ("Direct Jobdesc (Old)", "https://career.infosys.com/jobdesc?jobReferenceCode=INFSYS-EXTERNAL-249251"),
        ("Direct Jobdesc with params", "https://career.infosys.com/jobdesc?jobReferenceCode=INFSYS-EXTERNAL-249251&companyhiringtype=IL&countrycode=IN"),
        ("Joblist with Reference Code", "https://career.infosys.com/joblist?keyword=INFSYS-EXTERNAL-249251"),
        ("Joblist with Search param", "https://career.infosys.com/joblist?searchJob=INFSYS-EXTERNAL-249251&companyhiringtype=IL&countrycode=IN"),
        ("Joblist with Reference Code Search", "https://career.infosys.com/joblist?companyhiringtype=IL&countrycode=IN&searchJob=INFSYS-EXTERNAL-249251")
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel='chrome',
            headless=True,
            args=['--disable-blink-features=AutomationControlled']
        )
        
        for name, u in urls_to_test:
            print(f"\n" + "-" * 80)
            print(f"TESTING [{name}]: {u}")
            print("-" * 80, flush=True)

            context = browser.new_context()
            page = context.new_page()

            console_logs = []
            failed_requests = []
            
            page.on('console', lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))
            page.on('requestfailed', lambda req: failed_requests.append(f"{req.method} {req.url} -> {req.failure}"))

            try:
                page.goto(u, wait_until='networkidle', timeout=25000)
            except Exception as e:
                print(f"  Goto warning/timeout: {e}", flush=True)

            time.sleep(3)

            final_url = page.url
            title = page.title()
            
            # Check what DOM elements exist
            dom_check = page.evaluate("""() => {
                const h1 = document.querySelector('h1, h2, h3, h4, .job-title, .jobTitle');
                const jd = document.querySelector('.job-description, .jobdesc, .description, mat-card');
                const bodyText = document.body.innerText.trim();
                const cards = document.querySelectorAll('mat-card, .card, .job-card');
                const btns = Array.from(document.querySelectorAll('button'));
                const applyBtn = btns.find(b => b.innerText && b.innerText.includes('Apply'));
                return {
                    bodyLength: bodyText.length,
                    bodySnippet: bodyText.slice(0, 250).replace(/\\n+/g, ' '),
                    hasJobTitle: !!h1,
                    jobTitleText: h1 ? h1.innerText : null,
                    cardsCount: cards.length,
                    hasApplyBtn: !!applyBtn
                };
            }""")

            print(f"  Final URL     : {final_url}", flush=True)
            print(f"  Page Title    : {title}", flush=True)
            print(f"  Body Length   : {dom_check['bodyLength']}", flush=True)
            print(f"  Body Snippet  : {dom_check['bodySnippet']}", flush=True)
            print(f"  Job Title DOM : {dom_check['jobTitleText']}", flush=True)
            print(f"  Cards Count   : {dom_check['cardsCount']}", flush=True)
            
            if console_logs:
                print(f"  Console Logs ({len(console_logs)}):", flush=True)
                for l in console_logs[:10]:
                    clean_l = l.encode('ascii', errors='replace').decode('ascii')
                    print(f"    {clean_l}", flush=True)

            if failed_requests:
                print(f"  Failed Requests ({len(failed_requests)}):")
                for fr in failed_requests[:5]:
                    print(f"    {fr}")

            context.close()

        browser.close()

if __name__ == "__main__":
    deep_test_infosys()
