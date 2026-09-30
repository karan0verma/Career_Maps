import os
import sys
import time
from playwright.sync_api import sync_playwright

def compare_infosys_urls():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context()
        
        # Test 1: Direct joblist with keyword/reference
        p1 = context.new_page()
        print("Testing: https://career.infosys.com/joblist?keyword=INFSYS-EXTERNAL-251345", flush=True)
        p1.goto("https://career.infosys.com/joblist?keyword=INFSYS-EXTERNAL-251345", wait_until='load', timeout=20000)
        time.sleep(3)
        print("Title 1:", p1.title(), flush=True)
        print("Body 1 Snippet:", p1.inner_text('body')[:200].replace('\n', ' '), flush=True)
        p1.close()

        # Test 2: Direct joblist with search
        p2 = context.new_page()
        print("\nTesting: https://career.infosys.com/joblist?search=INFSYS-EXTERNAL-251345", flush=True)
        p2.goto("https://career.infosys.com/joblist?search=INFSYS-EXTERNAL-251345", wait_until='load', timeout=20000)
        time.sleep(3)
        print("Title 2:", p2.title(), flush=True)
        print("Body 2 Snippet:", p2.inner_text('body')[:200].replace('\n', ' '), flush=True)
        p2.close()

        browser.close()

if __name__ == "__main__":
    compare_infosys_urls()
