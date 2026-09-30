import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

def inspect_all_portals():
    print("=" * 80)
    print("INSPECTING PORTALS ACROSS CATEGORIES A, B, AND C")
    print("=" * 80, flush=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        page = context.new_page()

        portals = [
            # Category A
            ("Google India", "https://www.google.com/about/careers/applications/jobs/results/?location=India"),
            ("IBM India", "https://ibm.eightfold.ai/careers?domain=ibm.com&location=India"),
            ("Adobe India", "https://adobe.wd5.myworkdayjobs.com/en-US/external_experienced"),
            ("Cisco India", "https://jobs.cisco.com/jobs/SearchJobs/?21178=%5B169482%5D&21178_format=464&listFilterMode=1"),
            ("Meta India", "https://www.metacareers.com/jobs?locations[0]=Bangalore%2C%20India&locations[1]=Gurgaon%2C%20India&locations[2]=Hyderabad%2C%20India"),
            
            # Category B
            ("Accenture India", "https://www.accenture.com/in-en/careers/jobsearch?jk=&sb=1&pg=1"),
            ("Capgemini India", "https://www.capgemini.com/in-en/careers/job-search/?country_code=in-en"),
            ("LTIMindtree", "https://careers.ltimindtree.com/search/?q="),
            
            # Category C
            ("Flipkart", "https://www.flipkartcareers.com/#!/search-jobs"),
            ("Swiggy", "https://careers.swiggy.com/#/"),
            ("Zomato", "https://www.zomato.com/careers"),
        ]

        results = []

        for name, url in portals:
            try:
                print(f"\nProbing {name} ({url[:60]}...)", flush=True)
                page.goto(url, wait_until='domcontentloaded', timeout=20000)
                time.sleep(3)

                info = page.evaluate("""() => {
                    const title = document.title;
                    const jobLinks = Array.from(document.querySelectorAll('a[href*="/job"], a[href*="/careers/"], a[href*="job-details"], a[href*="/jobs/"]')).map(a => ({
                        text: a.innerText.trim(),
                        href: a.href
                    })).filter(j => j.text.length > 3 && !j.text.toLowerCase().includes('search'));

                    const countText = Array.from(document.querySelectorAll('*')).map(e => e.innerText).find(t => t && (t.includes('jobs found') || t.includes('openings') || t.includes('results') || t.includes('Positions'))) || '';

                    return {
                        title,
                        countText: countText.slice(0, 80),
                        jobLinksCount: jobLinks.length,
                        sampleJob: jobLinks[0] || null
                    };
                }""")
                print(f"  • Title: {info['title'][:50]}")
                print(f"  • Jobs on Page: {info['jobLinksCount']} | Count Text: {info['countText']}")
                print(f"  • Sample Job: {info['sampleJob']}")
                results.append({"name": name, "status": "OK", "info": info})
            except Exception as e:
                print(f"  • Error on {name}: {e}")
                results.append({"name": name, "status": "ERR", "error": str(e)})

        browser.close()

    # Save summary
    out = r"C:\Users\Ahana Singh\.gemini\antigravity\scratch\career-maps\apps\crawler\staging\all_portals_probe.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nProbe saved to {out}")

if __name__ == "__main__":
    inspect_all_portals()
