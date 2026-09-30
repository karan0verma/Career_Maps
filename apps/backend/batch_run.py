import os
import json
import time
import requests
import concurrent.futures
from urllib.parse import urlparse
from src.db.session import SessionLocal
from src.models.company import Company, CompanySource
from src.models.job import Job
from src.services.crawler import CrawlerService

COMPANIES = [
    # Top IT & Consulting
    {"domain": "tcs.com", "name": "Tata Consultancy Services", "city": "Mumbai"},
    {"domain": "infosys.com", "name": "Infosys", "city": "Bengaluru"},
    {"domain": "wipro.com", "name": "Wipro", "city": "Bengaluru"},
    {"domain": "hcltech.com", "name": "HCLTech", "city": "Noida"},
    {"domain": "techmahindra.com", "name": "Tech Mahindra", "city": "Pune"},
    {"domain": "ltimindtree.com", "name": "LTIMindtree", "city": "Mumbai"},
    {"domain": "mphasis.com", "name": "Mphasis", "city": "Bengaluru"},
    {"domain": "mindtree.com", "name": "Mindtree", "city": "Bengaluru"},
    {"domain": "hexaware.com", "name": "Hexaware", "city": "Navi Mumbai"},
    {"domain": "birlasoft.com", "name": "Birlasoft", "city": "Pune"},
    {"domain": "zensar.com", "name": "Zensar", "city": "Pune"},
    {"domain": "cyient.com", "name": "Cyient", "city": "Hyderabad"},
    {"domain": "coforge.com", "name": "Coforge", "city": "Noida"},
    {"domain": "persistent.com", "name": "Persistent Systems", "city": "Pune"},
    {"domain": "tataelxsi.com", "name": "Tata Elxsi", "city": "Bengaluru"},
    {"domain": "kpit.com", "name": "KPIT", "city": "Pune"},
    {"domain": "sonata-software.com", "name": "Sonata Software", "city": "Bengaluru"},
    {"domain": "ramcosystems.com", "name": "Ramco Systems", "city": "Chennai"},
    {"domain": "happiestminds.com", "name": "Happiest Minds", "city": "Bengaluru"},
    {"domain": "mastek.com", "name": "Mastek", "city": "Mumbai"},

    # MNCs with Huge India Presence
    {"domain": "accenture.com", "name": "Accenture", "city": "Bengaluru"},
    {"domain": "ibm.com", "name": "IBM", "city": "Bengaluru"},
    {"domain": "cognizant.com", "name": "Cognizant", "city": "Chennai"},
    {"domain": "capgemini.com", "name": "Capgemini", "city": "Pune"},
    {"domain": "deloitte.com", "name": "Deloitte", "city": "Hyderabad"},
    {"domain": "ey.com", "name": "EY", "city": "Gurugram"},
    {"domain": "pwc.com", "name": "PwC", "city": "Kolkata"},
    {"domain": "kpmg.com", "name": "KPMG", "city": "Mumbai"},
    {"domain": "amazon.jobs", "name": "Amazon", "city": "Bengaluru"},
    {"domain": "microsoft.com", "name": "Microsoft", "city": "Hyderabad"},
    {"domain": "google.com", "name": "Google", "city": "Bengaluru"},
    {"domain": "apple.com", "name": "Apple", "city": "Hyderabad"},
    {"domain": "meta.com", "name": "Meta", "city": "Gurugram"},
    {"domain": "oracle.com", "name": "Oracle", "city": "Bengaluru"},
    {"domain": "cisco.com", "name": "Cisco", "city": "Bengaluru"},
    {"domain": "intel.com", "name": "Intel", "city": "Bengaluru"},
    {"domain": "qualcomm.com", "name": "Qualcomm", "city": "Hyderabad"},
    {"domain": "samsung.com", "name": "Samsung", "city": "Noida"},
    {"domain": "nokia.com", "name": "Nokia", "city": "Noida"},
    {"domain": "ericsson.com", "name": "Ericsson", "city": "Gurugram"},
    {"domain": "barco.com", "name": "Barco", "city": "Noida"},
    {"domain": "globallogic.com", "name": "GlobalLogic", "city": "Noida"},
    {"domain": "soprasteria.in", "name": "Sopra Steria", "city": "Noida"},
    {"domain": "adobe.com", "name": "Adobe", "city": "Noida"},
    {"domain": "salesforce.com", "name": "Salesforce", "city": "Hyderabad"},
    {"domain": "sap.com", "name": "SAP", "city": "Bengaluru"},
    {"domain": "vmware.com", "name": "VMware", "city": "Bengaluru"},
    {"domain": "intuit.com", "name": "Intuit", "city": "Bengaluru"},
    {"domain": "walmart.com", "name": "Walmart", "city": "Bengaluru"},
    {"domain": "target.com", "name": "Target", "city": "Bengaluru"},
    {"domain": "jpmorgan.com", "name": "JP Morgan", "city": "Mumbai"},
    {"domain": "goldmansachs.com", "name": "Goldman Sachs", "city": "Bengaluru"},
    {"domain": "morganstanley.com", "name": "Morgan Stanley", "city": "Mumbai"},
    {"domain": "wellsfargo.com", "name": "Wells Fargo", "city": "Hyderabad"},
    {"domain": "americanexpress.com", "name": "American Express", "city": "Gurugram"},
    {"domain": "mastercard.com", "name": "Mastercard", "city": "Gurugram"},
    {"domain": "visa.com", "name": "Visa", "city": "Bengaluru"},
    {"domain": "paypal.com", "name": "PayPal", "city": "Bengaluru"},
    {"domain": "uber.com", "name": "Uber", "city": "Gurugram"},
    {"domain": "netflix.com", "name": "Netflix", "city": "Mumbai"},

    # Top Indian Startups & Product Companies
    {"domain": "flipkart.com", "name": "Flipkart", "city": "Bengaluru"},
    {"domain": "paytm.com", "name": "Paytm", "city": "Noida"},
    {"domain": "zomato.com", "name": "Zomato", "city": "Gurugram"},
    {"domain": "swiggy.com", "name": "Swiggy", "city": "Bengaluru"},
    {"domain": "olaelectric.com", "name": "Ola", "city": "Bengaluru"},
    {"domain": "oyo.com", "name": "OYO", "city": "Gurugram"},
    {"domain": "byjus.com", "name": "BYJU'S", "city": "Bengaluru"},
    {"domain": "cred.club", "name": "CRED", "city": "Bengaluru"},
    {"domain": "razorpay.com", "name": "Razorpay", "city": "Bengaluru"},
    {"domain": "pine-labs.com", "name": "Pine Labs", "city": "Noida"},
    {"domain": "phonepe.com", "name": "PhonePe", "city": "Bengaluru"},
    {"domain": "bharatpe.com", "name": "BharatPe", "city": "New Delhi"},
    {"domain": "meesho.com", "name": "Meesho", "city": "Bengaluru"},
    {"domain": "nykaa.com", "name": "Nykaa", "city": "Mumbai"},
    {"domain": "policybazaar.com", "name": "PolicyBazaar", "city": "Gurugram"},
    {"domain": "cars24.com", "name": "CARS24", "city": "Gurugram"},
    {"domain": "delhivery.com", "name": "Delhivery", "city": "Gurugram"},
    {"domain": "makemytrip.com", "name": "MakeMyTrip", "city": "Gurugram"},
    {"domain": "freshworks.com", "name": "Freshworks", "city": "Chennai"},
    {"domain": "zoho.com", "name": "Zoho", "city": "Chennai"},
    {"domain": "browserstack.com", "name": "BrowserStack", "city": "Mumbai"},
    {"domain": "postman.com", "name": "Postman", "city": "Bengaluru"},
    {"domain": "druva.com", "name": "Druva", "city": "Pune"},
    {"domain": "inmobi.com", "name": "InMobi", "city": "Bengaluru"},
    {"domain": "glance.com", "name": "Glance", "city": "Bengaluru"},
    {"domain": "myntra.com", "name": "Myntra", "city": "Bengaluru"},
    {"domain": "cleartrip.com", "name": "Cleartrip", "city": "Mumbai"},
    {"domain": "dream11.com", "name": "Dream11", "city": "Mumbai"},
    {"domain": "upstox.com", "name": "Upstox", "city": "Mumbai"},
    {"domain": "zerodha.com", "name": "Zerodha", "city": "Bengaluru"},
    {"domain": "groww.in", "name": "Groww", "city": "Bengaluru"},
    {"domain": "sharechat.com", "name": "ShareChat", "city": "Bengaluru"},
    {"domain": "unacademy.com", "name": "Unacademy", "city": "Bengaluru"},
    {"domain": "upgrad.com", "name": "upGrad", "city": "Mumbai"},
    {"domain": "vedantu.com", "name": "Vedantu", "city": "Bengaluru"},
    {"domain": "pharmeasy.in", "name": "PharmEasy", "city": "Mumbai"},
    {"domain": "1mg.com", "name": "1mg", "city": "Gurugram"},
    {"domain": "cure.fit", "name": "CureFit", "city": "Bengaluru"},
    {"domain": "lenskart.com", "name": "Lenskart", "city": "Gurugram"},
    {"domain": "urbancompany.com", "name": "Urban Company", "city": "Gurugram"},
    {"domain": "blinkit.com", "name": "Blinkit", "city": "Gurugram"},
    {"domain": "zeptonow.com", "name": "Zepto", "city": "Mumbai"},
    {"domain": "dunzo.com", "name": "Dunzo", "city": "Bengaluru"},
    {"domain": "spinny.com", "name": "Spinny", "city": "Gurugram"},
    {"domain": "atherenergy.com", "name": "Ather Energy", "city": "Bengaluru"},
    {"domain": "boat-lifestyle.com", "name": "boAt", "city": "Mumbai"},
    {"domain": "mamaearth.in", "name": "Mamaearth", "city": "Gurugram"},
    {"domain": "ofbusiness.com", "name": "OfBusiness", "city": "Gurugram"},
    {"domain": "zetwerk.com", "name": "Zetwerk", "city": "Bengaluru"},
    {"domain": "inframarket.com", "name": "Infra.Market", "city": "Thane"},
    {"domain": "moglix.com", "name": "Moglix", "city": "Noida"},
    {"domain": "rivigo.com", "name": "Rivigo", "city": "Gurugram"},
    {"domain": "blackbuck.com", "name": "BlackBuck", "city": "Bengaluru"},
    {"domain": "udaan.com", "name": "Udaan", "city": "Bengaluru"},
    {"domain": "dailhunt.in", "name": "Dailyhunt", "city": "Bengaluru"},
    {"domain": "fractal.ai", "name": "Fractal", "city": "Mumbai"},
    {"domain": "mu-sigma.com", "name": "Mu Sigma", "city": "Bengaluru"},
    {"domain": "innovaccer.com", "name": "Innovaccer", "city": "Noida"},
    {"domain": "rategain.com", "name": "RateGain", "city": "Noida"},
    {"domain": "newgensoftware.com", "name": "Newgen Software", "city": "Noida"},
    {"domain": "nagarro.com", "name": "Nagarro", "city": "Gurugram"},
    {"domain": "chetu.com", "name": "Chetu", "city": "Noida"},
    {"domain": "lambdatest.com", "name": "LambdaTest", "city": "Noida"},
    {"domain": "tothenew.com", "name": "TO THE NEW", "city": "Noida"},
    {"domain": "irissoftware.com", "name": "Iris Software", "city": "Noida"},
    {"domain": "xebia.com", "name": "Xebia", "city": "Gurugram"},
    {"domain": "maqsoftware.com", "name": "MAQ Software", "city": "Noida"},

    # PSUs & Government
    {"domain": "sbi.co.in", "name": "State Bank of India", "city": "Mumbai"},
    {"domain": "isro.gov.in", "name": "ISRO", "city": "Bengaluru"},
    {"domain": "ongcindia.com", "name": "ONGC", "city": "New Delhi"},
    {"domain": "ntpc.co.in", "name": "NTPC", "city": "New Delhi"},
    {"domain": "sail.co.in", "name": "SAIL", "city": "New Delhi"},
    {"domain": "bhel.com", "name": "BHEL", "city": "New Delhi"},
    {"domain": "iocl.com", "name": "Indian Oil", "city": "New Delhi"}
]

# Quick filter to ensure we get a solid list
print(f"Loaded {len(COMPANIES)} target domains.")

def get_db():
    return SessionLocal()

def ensure_company(db, comp):
    domain = comp["domain"]
    name = comp["name"]
    city = comp["city"]
    
    # Check if exists by domain or name
    existing = db.query(Company).filter(
        (Company.website.ilike(f"%{domain}%")) | (Company.official_name.ilike(f"%{name}%"))
    ).first()
    
    if existing:
        # update city if missing
        if not existing.city or not existing.headquarters:
            existing.city = city
            existing.headquarters = city
            db.commit()
        return existing
        
    c = Company(
        official_name=name,
        display_name=name,
        website=domain,
        city=city,
        headquarters=city,
        country="India"
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return c

def process_company(comp):
    db = get_db()
    try:
        c = ensure_company(db, comp)
        # Avoid re-crawling if we crawled very recently and it succeeded
        # We want maximum scale, but don't double-crawl if it was just done 1 min ago
        # Force crawl to ignore 24hr cache
        hist = CrawlerService.run_crawl(db, c.company_id, force_run=True)
        
        return {
            "name": c.display_name,
            "status": hist.status,
            "jobs_found": hist.jobs_found,
            "jobs_added": hist.jobs_added,
            "error": str(hist.errors) if hist.errors else None
        }
    except Exception as e:
        return {
            "name": comp["name"],
            "status": "EXCEPTION",
            "jobs_found": 0,
            "jobs_added": 0,
            "error": str(e)
        }
    finally:
        db.close()

if __name__ == "__main__":
    db = get_db()
    for c in COMPANIES:
        ensure_company(db, c)
    db.close()
    
    results = []
    start_time = time.time()
    
    # Run with 5 workers for concurrency to prevent IPC crashes
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(process_company, c) for c in COMPANIES]
        for idx, future in enumerate(concurrent.futures.as_completed(futures)):
            res = future.result()
            results.append(res)
            print(f"[{idx+1}/{len(COMPANIES)}] {res['name']} -> {res['status']} | Jobs: {res['jobs_found']}")
            
    dur = time.time() - start_time
    print(f"\nCompleted in {dur:.2f} seconds.")
    
    with open("batch_run_results.json", "w") as f:
        json.dump(results, f, indent=2)
