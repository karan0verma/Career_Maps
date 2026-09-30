import sys
import json
import re
from playwright.sync_api import sync_playwright

companies = {
    "TCS": "https://www.tcs.com/careers",
    "GlobalLogic": "https://www.globallogic.com/careers/",
    "MAQ Software": "https://maqsoftware.com/careers",
    "Newgen Software": "https://newgensoft.com/careers",
    "Sopra Steria India": "https://careers.soprasteria.in/",
    "UKG": "https://www.ukg.com/company/careers",
    "Delhivery": "https://www.delhivery.com/careers",
    "LambdaTest": "https://www.testmuai.com/career/",
    "Pine Labs": "https://www.pinelabs.com/careers",
    "Chetu": "https://careers.chetu.com/",
    "RateGain": "https://rategain.com/careers",
    "TO THE NEW": "https://www.tothenew.com/careers",
    "Birlasoft": "https://www.birlasoft.com/careers",
    "Tech Mahindra": "https://www.techmahindra.com/careers/",
    "Coforge": "https://careers.coforge.com/coforge/",
    "Nagarro": "https://www.nagarro.com/en/careers",
    "Innovaccer": "https://innovaccer.com/careers",
    "Adobe India": "https://careers.adobe.com/us/en"
}

ATS_PATTERNS = {
    "WORKDAY": r"myworkdayjobs\.com|wd1\.myworkdayjobs\.com|wd3\.myworkdayjobs\.com|wd5\.myworkdayjobs\.com|workday",
    "SUCCESSFACTORS_RMK": r"jobs\.sap\.com|careers\.successfactors\.com|successfactors\.com|career4\.successfactors\.com|career8\.successfactors\.com|sfcareer|\.sapsf\.",
    "PHENOM": r"PhenomPeople|phenom",
    "GREENHOUSE": r"boards\.greenhouse\.io|greenhouse\.io/careers|greenhouse\.io/embed/job_board|boards-api\.greenhouse\.io|api\.greenhouse\.io|grnhse-iframe|gh-src",
    "LEVER": r"jobs\.lever\.co|api\.lever\.co",
    "ASHBY": r"jobs\.ashbyhq\.com|ashbyhq\.com/api|api\.ashbyhq\.com",
    "SMARTRECRUITERS": r"smartrecruiters\.com",
    "WORKABLE": r"workable\.com|apply\.workable\.com",
    "JOBVITE": r"jobs\.jobvite\.com",
    "BAMBOOHR": r"bamboohr\.com/careers|window\.BambooHR|bamboohr\.com",
    "EIGHTFOLD": r"eightfold\.ai",
    "ZOHO_RECRUIT": r"zohorecruit\.com",
    "TALEO": r"taleo\.net|\.taleo\.",
    "ICIMS": r"icims\.com|\.icims\.",
    "AVATURE": r"avature\.net",
    "I_CIMS": r"iCIMS",
    "BEAMERY": r"beamery\.com",
    "GEM": r"gem\.com",
    "APPLICANT_STACK": r"applicantstack\.com",
    "PAGEUP": r"pageuppeople\.com",
    "BRASSRING": r"brassring\.com",
    "WORKDAY_API": r"workday\.com",
    "EIGHTFOLD_API": r"eightfold\.ai"
}

results = {}

def investigate():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for name, url in companies.items():
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            
            print(f"Investigating {name}...")
            
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                try:
                    page.wait_for_load_state("networkidle", timeout=10000)
                except:
                    pass
                
                final_url = page.url
                html = page.content()
                
                frames = [frame.url for frame in page.frames]
                links = [link.get_attribute("href") for link in page.query_selector_all("a") if link.get_attribute("href")]
                
                matches = {}
                # Check URL, frames, and HTML
                for ats, pattern in ATS_PATTERNS.items():
                    regex = re.compile(pattern, re.I)
                    if regex.search(final_url):
                        matches[ats] = matches.get(ats, []) + ["Final URL matched"]
                    for frame in frames:
                        if regex.search(frame):
                            matches[ats] = matches.get(ats, []) + [f"Iframe URL matched: {frame}"]
                    for link in links:
                        if regex.search(link):
                            matches[ats] = matches.get(ats, []) + [f"Link URL matched: {link}"]
                    if regex.search(html):
                        matches[ats] = matches.get(ats, []) + ["HTML matched"]
                
                results[name] = {
                    "original_url": url,
                    "final_url": final_url,
                    "matches": matches,
                    "frames": frames,
                    "error": None
                }
            except Exception as e:
                print(f"Error for {name}: {e}")
                results[name] = {
                    "original_url": url,
                    "error": str(e)
                }
            finally:
                context.close()
        browser.close()
        
    with open("investigation_results.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    investigate()
