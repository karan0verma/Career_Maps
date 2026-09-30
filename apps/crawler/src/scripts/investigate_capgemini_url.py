import os
import sys
import json
import time
import requests
from playwright.sync_api import sync_playwright

print("=" * 80)
print("INVESTIGATING REAL CAPGEMINI JOB URL STRUCTURE & OFFICIAL LOGOS")
print("=" * 80)

# 1. Official Logos from genuine corporate websites
logos_dir = r"C:\Users\Ahana Singh\.gemini\antigravity\scratch\career-maps\apps\frontend\public\logos"

with sync_playwright() as p:
    browser = p.chromium.launch(channel='chrome', headless=True)
    context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    page = context.new_page()

    # --- 1.1 Download Authentic Adobe Logo from adobe.com ---
    print("\n[1] Fetching official Adobe logo from adobe.com...", flush=True)
    try:
        page.goto("https://www.adobe.com/in/", wait_until='domcontentloaded', timeout=20000)
        time.sleep(2)
        adobe_logo_src = page.evaluate("""() => {
            const img = document.querySelector('header img, a[class*="logo"] img, img[alt*="Adobe" i], svg[class*="adobe"]');
            if (img) {
                return img.tagName.toLowerCase() === 'svg' ? { type: 'svg', content: img.outerHTML } : { type: 'img', src: img.src };
            }
            return null;
        }""")
        if adobe_logo_src:
            if adobe_logo_src.get('type') == 'svg':
                with open(os.path.join(logos_dir, "adobe.svg"), "w", encoding="utf-8") as f:
                    f.write(adobe_logo_src['content'])
                print("  [OK] Saved authentic Adobe SVG from adobe.com header!")
            elif adobe_logo_src.get('src'):
                res = requests.get(adobe_logo_src['src'], headers={'User-Agent': 'Mozilla/5.0'})
                if res.ok:
                    ext = '.svg' if 'svg' in adobe_logo_src['src'] else '.png'
                    with open(os.path.join(logos_dir, f"adobe{ext}"), "wb") as f:
                        f.write(res.content)
                    print(f"  [OK] Downloaded authentic adobe{ext} from adobe.com header!")
    except Exception as e:
        print(f"  Adobe logo err: {e}")

    # --- 1.2 Download Authentic Capgemini Logo from capgemini.com ---
    print("\n[2] Fetching official Capgemini logo from capgemini.com...", flush=True)
    try:
        page.goto("https://www.capgemini.com/in-en/", wait_until='domcontentloaded', timeout=20000)
        time.sleep(2)
        cap_logo_src = page.evaluate("""() => {
            const img = document.querySelector('header img, a[class*="logo"] img, img[alt*="Capgemini" i]');
            return img ? img.src : null;
        }""")
        if cap_logo_src:
            res = requests.get(cap_logo_src, headers={'User-Agent': 'Mozilla/5.0'})
            if res.ok:
                ext = '.svg' if 'svg' in cap_logo_src else '.png'
                with open(os.path.join(logos_dir, f"capgemini{ext}"), "wb") as f:
                    f.write(res.content)
                print(f"  [OK] Downloaded authentic capgemini{ext} from capgemini.com header!")
    except Exception as e:
        print(f"  Capgemini logo err: {e}")

    # --- 2. Investigate Capgemini Real Job URLs ---
    print("\n[3] Investigating Capgemini Real Job Click Navigation...", flush=True)
    try:
        page.goto("https://www.capgemini.com/in-en/careers/job-search/?country_code=in-en", wait_until='domcontentloaded', timeout=30000)
        time.sleep(4)

        # Inspect real job links rendered on page
        job_links = page.evaluate("""() => {
            const links = Array.from(document.querySelectorAll('a[href*="job"], a[class*="card"], [class*="job"] a'));
            return links.map(a => ({
                text: a.innerText.trim(),
                href: a.href
            })).filter(j => j.text.length > 5);
        }""")
        print(f"Found {len(job_links)} candidate links on Capgemini search page:")
        for l in job_links[:10]:
            print(f"  • {l['text'][:40]} -> {l['href']}")

        # Also let's query the raw Capgemini API object to see what fields exist for URL
        api_res = page.request.get("https://cg-jobstream-api.azurewebsites.net/api/job-search?page=1&size=5&country_code=in-en")
        if api_res.ok:
            data = api_res.json()
            print("\nCapgemini API Raw Job Object keys & values:")
            for item in data.get('data', [])[:2]:
                print(json.dumps(item, indent=2))

    except Exception as e:
        print(f"Capgemini link inspection error: {e}")

    browser.close()
