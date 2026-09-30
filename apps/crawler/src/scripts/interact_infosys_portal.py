import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

def interact_infosys():
    print("=" * 75)
    print("INTERACTING WITH INFOSYS CAREER PORTAL (CLICKING CARDS/FILTERS)")
    print("=" * 75)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            viewport={'width': 1440, 'height': 900}
        )
        page = context.new_page()

        captured = []

        def on_req(req):
            if 'infosysapps.com' in req.url or 'careersci' in req.url or 'search' in req.url or 'job' in req.url:
                print(f"[REQ] {req.method} {req.url}")
                if req.post_data:
                    print(f"      POST: {req.post_data[:200]}")
                captured.append({'method': req.method, 'url': req.url, 'post': req.post_data})

        def on_res(res):
            if 'infosysapps.com' in res.url or 'careersci' in res.url:
                try:
                    data = res.json()
                    print(f"[RES] {res.status} {res.url}")
                    if isinstance(data, dict):
                        for k, v in data.items():
                            if isinstance(v, list):
                                print(f"      Key '{k}' list length: {len(v)}")
                                if len(v) > 0:
                                    print(f"      First item: {str(v[0])[:150]}")
                    elif isinstance(data, list):
                        print(f"      List length: {len(data)}")
                except Exception:
                    pass

        page.on('request', on_req)
        page.on('response', on_res)

        page.goto('https://career.infosys.com/joblist', wait_until='networkidle', timeout=35000)
        time.sleep(4)

        # Click on one of the hot jobs or functional areas or location cards
        print("\nAttempting to click a job category/location card...")
        page.evaluate("""() => {
            // Find all clickable cards
            const cards = document.querySelectorAll('.card, .job-card, .location-card, a, button');
            for (let c of cards) {
                if (c.innerText && (c.innerText.includes('BANGALORE') || c.innerText.includes('Enterprise') || c.innerText.includes('View all') || c.innerText.includes('Search'))) {
                    console.log('Clicking:', c.innerText.trim().slice(0, 30));
                    c.click();
                    break;
                }
            }
        }""")
        time.sleep(5)

        # Look at URL and title after click
        print(f"URL after click: {page.url}")

        browser.close()

if __name__ == "__main__":
    interact_infosys()
