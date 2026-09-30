import requests
import urllib3
from urllib.parse import urlparse
import sys
import json
import time

urllib3.disable_warnings()

companies = {
    "Samsung Research Institute India (Noida)": "research.samsung.com",
    "Adobe India": "adobe.com",
    "Tata Consultancy Services (TCS)": "tcs.com",
    "GlobalLogic": "globallogic.com",
    "MAQ Software": "maqsoftware.com",
    "Newgen Software": "newgensoft.com",
    "Sopra Steria India": "soprasteria.in",
    "UKG (Ultimate Kronos Group)": "ukg.com",
    "Delhivery": "delhivery.com",
    "LambdaTest": "lambdatest.com",
    "Pine Labs": "pinelabs.com",
    "Chetu": "chetu.com",
    "RateGain": "rategain.com",
    "TO THE NEW": "tothenew.com",
    "Barco": "barco.com",
    "Birlasoft": "birlasoft.com",
    "Wipro": "wipro.com",
    "Tech Mahindra": "techmahindra.com",
    "Coforge": "coforge.com",
    "Nagarro": "nagarro.com",
    "Innovaccer": "innovaccer.com",
    "HCLTech": "hcltech.com"
}

from bs4 import BeautifulSoup

def analyze():
    headers = {"User-Agent": "Mozilla/5.0"}
    session = requests.Session()
    
    results = {}
    
    for name, domain in companies.items():
        print(f"Checking {name}...")
        try:
            # 1. Quick search for career page
            url = f"https://www.google.com/search?q={name}+careers"
            resp = session.get(url, headers=headers, timeout=5)
            soup = BeautifulSoup(resp.text, 'html.parser')
            career_url = None
            for a in soup.find_all('a', href=True):
                href = a['href']
                if 'url?q=' in href and 'google' not in href:
                    clean_url = href.split('url?q=')[1].split('&')[0]
                    if domain in clean_url or 'careers' in clean_url.lower() or 'jobs' in clean_url.lower():
                        career_url = clean_url
                        break
            
            if not career_url:
                career_url = f"https://{domain}/careers"
                
            print(f"  URL: {career_url}")
            
            # 2. Visit career page to see redirects and content
            resp2 = session.get(career_url, headers=headers, timeout=10, verify=False, allow_redirects=True)
            final_url = resp2.url
            print(f"  Final URL: {final_url}")
            
            content = resp2.text.lower()
            
            # Detect ATS footprints
            ats = "UNKNOWN"
            if 'taleo.net' in content or 'taleo' in final_url:
                ats = "TALEO"
            elif 'icims.com' in content or 'icims' in final_url:
                ats = "ICIMS"
            elif 'myworkdayjobs.com' in content or 'myworkdayjobs' in final_url or 'workday' in content:
                ats = "WORKDAY"
            elif 'successfactors.com' in content or 'successfactors' in final_url:
                ats = "SUCCESSFACTORS"
            elif 'brassring.com' in content or 'brassring' in final_url:
                ats = "BRASSRING"
            elif 'avature.net' in content or 'avature' in final_url:
                ats = "AVATURE"
            elif 'jobvite.com' in content or 'jobvite' in final_url:
                ats = "JOBVITE"
            elif 'workable.com' in content or 'workable' in final_url:
                ats = "WORKABLE"
            elif 'breezy.hr' in content or 'breezy' in final_url:
                ats = "BREEZY"
            elif 'recruitee.com' in content or 'recruitee' in final_url:
                ats = "RECRUITEE"
            elif 'eightfold.ai' in content or 'eightfold' in final_url:
                ats = "EIGHTFOLD"
            elif 'smartrecruiters' in content or 'smartrecruiters' in final_url:
                ats = "SMARTRECRUITERS"
            elif 'phenompeople' in content or 'phenom' in final_url:
                ats = "PHENOM"
            elif 'darwinbox' in content or 'darwinbox' in final_url:
                ats = "DARWINBOX"
                
            print(f"  Detected: {ats}")
            results[name] = {"url": career_url, "final_url": final_url, "ats": ats}
            
        except Exception as e:
            print(f"  Error: {e}")
            results[name] = {"error": str(e)}
            
        time.sleep(1)
        
    print("\n\nSUMMARY:")
    for k, v in results.items():
        print(f"{k}: {v.get('ats', 'ERROR')}")

if __name__ == "__main__":
    analyze()
