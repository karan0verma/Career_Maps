import requests
import re
from bs4 import BeautifulSoup
import urllib3
urllib3.disable_warnings()

urls = {
    "Google": "https://careers.google.com/",
    "Microsoft": "https://jobs.careers.microsoft.com/global/en/search",
    "Amazon": "https://amazon.jobs/en/search",
    "TCS": "https://www.tcs.com/careers",
    "Infosys": "https://www.infosys.com/careers.html",
    "Wipro": "https://careers.wipro.com/",
    "Flipkart": "https://www.flipkartcareers.com/",
    "Zomato": "https://www.zomato.com/careers",
    "Swiggy": "https://careers.swiggy.com/",
    "Meta": "https://www.metacareers.com/"
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

ats_signatures = {
    "Greenhouse": ["greenhouse.io", "boards.greenhouse.io"],
    "Lever": ["lever.co", "jobs.lever.co"],
    "Workday": ["myworkdayjobs.com", "workday"],
    "Taleo": ["taleo.net"],
    "SuccessFactors": ["successfactors.com", "career?.successfactors"],
    "iCIMS": ["icims.com"],
    "SmartRecruiters": ["smartrecruiters.com"],
    "Ashby": ["ashbyhq.com"],
    "Eightfold": ["eightfold.ai"]
}

for name, url in urls.items():
    try:
        resp = requests.get(url, headers=headers, timeout=10, verify=False, allow_redirects=True)
        html = resp.text.lower()
        found_ats = []
        for ats, sigs in ats_signatures.items():
            for sig in sigs:
                if sig.lower() in html or sig.lower() in resp.url:
                    found_ats.append(ats)
                    break
        
        # Check for generic API endpoints
        apis = []
        if "api" in html: apis.append("api")
        if "graphql" in html: apis.append("graphql")
        
        print(f"[{name}] URL: {resp.url} | Status: {resp.status_code}")
        print(f"  ATS: {', '.join(found_ats) if found_ats else 'Custom/Unknown'}")
        
    except Exception as e:
        print(f"[{name}] Error: {e}")
