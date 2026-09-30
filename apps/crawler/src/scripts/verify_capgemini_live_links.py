import os
import sys
import time
from playwright.sync_api import sync_playwright

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend')))

from dotenv import load_dotenv
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend', '.env')))

from src.db.session import SessionLocal
from src.models.company import Company
from src.models.job import Job

def verify_capgemini_links():
    db = SessionLocal()
    capgemini = db.query(Company).filter(Company.display_name == 'Capgemini').first()
    sample_jobs = db.query(Job).filter(Job.company_id == capgemini.company_id).limit(3).all()

    print("=" * 80)
    print("VERIFYING LIVE CAPGEMINI DIRECT APPLY LINKS IN CHROME")
    print("=" * 80)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        page = browser.new_page()

        for j in sample_jobs:
            print(f"\nTesting: {j.title}")
            print(f"URL: {j.apply_url}")
            page.goto(j.apply_url, wait_until='domcontentloaded', timeout=20000)
            time.sleep(3)

            page_title = page.title()
            has_apply_btn = page.evaluate("""() => {
                const btn = Array.from(document.querySelectorAll('button, a, input[type="submit"]')).find(b => b.innerText.toLowerCase().includes('apply'));
                return btn !== undefined;
            }""")

            print(f"  • Page Title: {page_title}")
            print(f"  • Has 'Apply now' Button: {has_apply_btn}")
            if "not found" not in page_title.lower() and has_apply_btn:
                print("  ✓ SUCCESS: Valid Live Job Application Page!")
            else:
                print("  ✗ FAILURE: Page not found or missing button")

        browser.close()

    db.close()

if __name__ == "__main__":
    verify_capgemini_links()
