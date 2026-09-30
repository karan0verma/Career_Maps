import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

def inspect_hcl_facets():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        page = context.new_page()

        page.goto('https://careers.hcltech.com/search/?q=&searchResultView=LIST', wait_until='networkidle', timeout=35000)
        time.sleep(2)

        tests = [
            ("All Global Jobs pageNumber=0", {"locale":"en_US","pageNumber":0,"sortBy":"","keywords":"","location":"","facetFilters":{},"brand":"","skills":[],"categoryId":0,"alertId":"","rcmCandidateId":""}),
            ("Country Region India", {"locale":"en_US","pageNumber":0,"sortBy":"","keywords":"","location":"","facetFilters":{"custCountryRegion":["India"]},"brand":"","skills":[],"categoryId":0,"alertId":"","rcmCandidateId":""}),
            ("optionsFacetsDD_country India", {"locale":"en_US","pageNumber":0,"sortBy":"","keywords":"","location":"","facetFilters":{"country":["India"]},"brand":"","skills":[],"categoryId":0,"alertId":"","rcmCandidateId":""})
        ]

        for name, pl in tests:
            res = page.request.post("https://careers.hcltech.com/services/recruiting/v1/jobs", data=json.dumps(pl), headers={'content-type': 'application/json'})
            d = res.json()
            print(f"\n{name} -> totalJobs: {d.get('totalJobs')}, returned: {len(d.get('jobSearchResult', []))}")
            jsr = d.get('jobSearchResult', [])
            if jsr:
                r0 = jsr[0].get('response', {})
                print(f"  Sample: {r0.get('unifiedStandardTitle')} | Country: {r0.get('custCountryRegion')} | City: {r0.get('custprimecity')} | ID: {r0.get('id')}")

        browser.close()

if __name__ == "__main__":
    inspect_hcl_facets()
