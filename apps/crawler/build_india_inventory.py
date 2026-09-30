import csv
import sys

def main():
    companies = [
        # Bengaluru
        {"company_name": "Flipkart", "domain": "flipkart.com", "country": "India", "state": "Karnataka", "city": "Bengaluru", "industry": "E-commerce", "company_type": "Product"},
        {"company_name": "Swiggy", "domain": "swiggy.com", "country": "India", "state": "Karnataka", "city": "Bengaluru", "industry": "FoodTech", "company_type": "Product"},
        {"company_name": "Zerodha", "domain": "zerodha.com", "country": "India", "state": "Karnataka", "city": "Bengaluru", "industry": "FinTech", "company_type": "Product"},
        {"company_name": "Razorpay", "domain": "razorpay.com", "country": "India", "state": "Karnataka", "city": "Bengaluru", "industry": "FinTech", "company_type": "Product"},
        {"company_name": "Cred", "domain": "cred.club", "country": "India", "state": "Karnataka", "city": "Bengaluru", "industry": "FinTech", "company_type": "Product"},
        {"company_name": "Postman", "domain": "postman.com", "country": "India", "state": "Karnataka", "city": "Bengaluru", "industry": "DevTools", "company_type": "SaaS"},
        {"company_name": "BrowserStack", "domain": "browserstack.com", "country": "India", "state": "Karnataka", "city": "Bengaluru", "industry": "DevTools", "company_type": "SaaS"},
        {"company_name": "Ola", "domain": "olacabs.com", "country": "India", "state": "Karnataka", "city": "Bengaluru", "industry": "Mobility", "company_type": "Product"},
        {"company_name": "Unacademy", "domain": "unacademy.com", "country": "India", "state": "Karnataka", "city": "Bengaluru", "industry": "EdTech", "company_type": "Product"},
        {"company_name": "Byjus", "domain": "byjus.com", "country": "India", "state": "Karnataka", "city": "Bengaluru", "industry": "EdTech", "company_type": "Product"},
        {"company_name": "Udaan", "domain": "udaan.com", "country": "India", "state": "Karnataka", "city": "Bengaluru", "industry": "B2B E-commerce", "company_type": "Product"},
        {"company_name": "ShareChat", "domain": "sharechat.com", "country": "India", "state": "Karnataka", "city": "Bengaluru", "industry": "Social Media", "company_type": "Product"},
        {"company_name": "Meesho", "domain": "meesho.com", "country": "India", "state": "Karnataka", "city": "Bengaluru", "industry": "E-commerce", "company_type": "Product"},
        {"company_name": "PhonePe", "domain": "phonepe.com", "country": "India", "state": "Karnataka", "city": "Bengaluru", "industry": "FinTech", "company_type": "Product"},
        {"company_name": "Groww", "domain": "groww.in", "country": "India", "state": "Karnataka", "city": "Bengaluru", "industry": "FinTech", "company_type": "Product"},
        {"company_name": "CureFit", "domain": "cure.fit", "country": "India", "state": "Karnataka", "city": "Bengaluru", "industry": "HealthTech", "company_type": "Product"},
        {"company_name": "Kite", "domain": "kite.zerodha.com", "country": "India", "state": "Karnataka", "city": "Bengaluru", "industry": "FinTech", "company_type": "Product"},
        {"company_name": "Licious", "domain": "licious.in", "country": "India", "state": "Karnataka", "city": "Bengaluru", "industry": "FoodTech", "company_type": "Product"},
        {"company_name": "Myntra", "domain": "myntra.com", "country": "India", "state": "Karnataka", "city": "Bengaluru", "industry": "E-commerce", "company_type": "Product"},
        {"company_name": "ClearTax", "domain": "cleartax.in", "country": "India", "state": "Karnataka", "city": "Bengaluru", "industry": "FinTech", "company_type": "SaaS"},
        {"company_name": "Khatabook", "domain": "khatabook.com", "country": "India", "state": "Karnataka", "city": "Bengaluru", "industry": "FinTech", "company_type": "Product"},
        {"company_name": "Dunzo", "domain": "dunzo.com", "country": "India", "state": "Karnataka", "city": "Bengaluru", "industry": "Logistics", "company_type": "Product"},
        {"company_name": "Ather Energy", "domain": "atherenergy.com", "country": "India", "state": "Karnataka", "city": "Bengaluru", "industry": "EV", "company_type": "Product"},
        {"company_name": "Infosys", "domain": "infosys.com", "country": "India", "state": "Karnataka", "city": "Bengaluru", "industry": "IT Services", "company_type": "IT Service"},
        {"company_name": "Wipro", "domain": "wipro.com", "country": "India", "state": "Karnataka", "city": "Bengaluru", "industry": "IT Services", "company_type": "IT Service"},
        {"company_name": "Tesco Bengaluru", "domain": "tescobengaluru.com", "country": "India", "state": "Karnataka", "city": "Bengaluru", "industry": "Retail Tech", "company_type": "MNC Engineering Center"},
        {"company_name": "Target India", "domain": "target.com", "country": "India", "state": "Karnataka", "city": "Bengaluru", "industry": "Retail Tech", "company_type": "MNC Engineering Center"},
        {"company_name": "Walmart Global Tech", "domain": "walmartglobaltech.com", "country": "India", "state": "Karnataka", "city": "Bengaluru", "industry": "Retail Tech", "company_type": "MNC Engineering Center"},
        {"company_name": "Amazon India", "domain": "amazon.jobs", "country": "India", "state": "Karnataka", "city": "Bengaluru", "industry": "E-commerce", "company_type": "MNC Engineering Center"},
        {"company_name": "Google India", "domain": "careers.google.com", "country": "India", "state": "Karnataka", "city": "Bengaluru", "industry": "Tech", "company_type": "MNC Engineering Center"},
        {"company_name": "Microsoft India", "domain": "careers.microsoft.com", "country": "India", "state": "Karnataka", "city": "Bengaluru", "industry": "Tech", "company_type": "MNC Engineering Center"},
        {"company_name": "HackerEarth", "domain": "hackerearth.com", "country": "India", "state": "Karnataka", "city": "Bengaluru", "industry": "HR Tech", "company_type": "SaaS"},

        # Hyderabad
        {"company_name": "Darwinbox", "domain": "darwinbox.com", "country": "India", "state": "Telangana", "city": "Hyderabad", "industry": "HR Tech", "company_type": "SaaS"},
        {"company_name": "HighRadius", "domain": "highradius.com", "country": "India", "state": "Telangana", "city": "Hyderabad", "industry": "FinTech", "company_type": "SaaS"},
        {"company_name": "Zenoti", "domain": "zenoti.com", "country": "India", "state": "Telangana", "city": "Hyderabad", "industry": "SaaS", "company_type": "SaaS"},
        {"company_name": "Keka", "domain": "keka.com", "country": "India", "state": "Telangana", "city": "Hyderabad", "industry": "HR Tech", "company_type": "SaaS"},
        {"company_name": "Cyient", "domain": "cyient.com", "country": "India", "state": "Telangana", "city": "Hyderabad", "industry": "Engineering Services", "company_type": "IT Service"},
        {"company_name": "Pramati Technologies", "domain": "pramati.com", "country": "India", "state": "Telangana", "city": "Hyderabad", "industry": "Software", "company_type": "Product"},
        {"company_name": "Salesforce India", "domain": "salesforce.com", "country": "India", "state": "Telangana", "city": "Hyderabad", "industry": "SaaS", "company_type": "MNC Engineering Center"},
        {"company_name": "ServiceNow India", "domain": "servicenow.com", "country": "India", "state": "Telangana", "city": "Hyderabad", "industry": "SaaS", "company_type": "MNC Engineering Center"},
        {"company_name": "Oracle India", "domain": "oracle.com", "country": "India", "state": "Telangana", "city": "Hyderabad", "industry": "Enterprise Software", "company_type": "MNC Engineering Center"},
        {"company_name": "D. E. Shaw India", "domain": "deshawindia.com", "country": "India", "state": "Telangana", "city": "Hyderabad", "industry": "FinTech", "company_type": "MNC Engineering Center"},
        
        # Pune
        {"company_name": "Icertis", "domain": "icertis.com", "country": "India", "state": "Maharashtra", "city": "Pune", "industry": "SaaS", "company_type": "SaaS"},
        {"company_name": "Mindtickle", "domain": "mindtickle.com", "country": "India", "state": "Maharashtra", "city": "Pune", "industry": "Sales Tech", "company_type": "SaaS"},
        {"company_name": "Firstcry", "domain": "firstcry.com", "country": "India", "state": "Maharashtra", "city": "Pune", "industry": "E-commerce", "company_type": "Product"},
        {"company_name": "Druva", "domain": "druva.com", "country": "India", "state": "Maharashtra", "city": "Pune", "industry": "Cloud Security", "company_type": "SaaS"},
        {"company_name": "PubMatic", "domain": "pubmatic.com", "country": "India", "state": "Maharashtra", "city": "Pune", "industry": "AdTech", "company_type": "SaaS"},
        {"company_name": "Xpressbees", "domain": "xpressbees.com", "country": "India", "state": "Maharashtra", "city": "Pune", "industry": "Logistics", "company_type": "Product"},
        {"company_name": "Tech Mahindra", "domain": "techmahindra.com", "country": "India", "state": "Maharashtra", "city": "Pune", "industry": "IT Services", "company_type": "IT Service"},
        {"company_name": "Persistent Systems", "domain": "persistent.com", "country": "India", "state": "Maharashtra", "city": "Pune", "industry": "IT Services", "company_type": "IT Service"},
        {"company_name": "Zensar Technologies", "domain": "zensar.com", "country": "India", "state": "Maharashtra", "city": "Pune", "industry": "IT Services", "company_type": "IT Service"},
        {"company_name": "Cvent India", "domain": "cvent.com", "country": "India", "state": "Maharashtra", "city": "Pune", "industry": "Event Tech", "company_type": "MNC Engineering Center"},

        # Gurugram
        {"company_name": "Zomato", "domain": "zomato.com", "country": "India", "state": "Haryana", "city": "Gurugram", "industry": "FoodTech", "company_type": "Product"},
        {"company_name": "Delhivery", "domain": "delhivery.com", "country": "India", "state": "Haryana", "city": "Gurugram", "industry": "Logistics", "company_type": "Product"},
        {"company_name": "Oyo", "domain": "oyorooms.com", "country": "India", "state": "Haryana", "city": "Gurugram", "industry": "Travel Tech", "company_type": "Product"},
        {"company_name": "MakeMyTrip", "domain": "makemytrip.com", "country": "India", "state": "Haryana", "city": "Gurugram", "industry": "Travel Tech", "company_type": "Product"},
        {"company_name": "PolicyBazaar", "domain": "policybazaar.com", "country": "India", "state": "Haryana", "city": "Gurugram", "industry": "InsurTech", "company_type": "Product"},
        {"company_name": "Urban Company", "domain": "urbancompany.com", "country": "India", "state": "Haryana", "city": "Gurugram", "industry": "Home Services", "company_type": "Product"},
        {"company_name": "OfBusiness", "domain": "ofbusiness.com", "country": "India", "state": "Haryana", "city": "Gurugram", "industry": "B2B E-commerce", "company_type": "Product"},
        {"company_name": "Spinny", "domain": "spinny.com", "country": "India", "state": "Haryana", "city": "Gurugram", "industry": "AutoTech", "company_type": "Product"},
        {"company_name": "Pristyn Care", "domain": "pristyncare.com", "country": "India", "state": "Haryana", "city": "Gurugram", "industry": "HealthTech", "company_type": "Product"},
        {"company_name": "Blinkit", "domain": "blinkit.com", "country": "India", "state": "Haryana", "city": "Gurugram", "industry": "Quick Commerce", "company_type": "Product"},

        # Noida
        {"company_name": "Paytm", "domain": "paytm.com", "country": "India", "state": "Uttar Pradesh", "city": "Noida", "industry": "FinTech", "company_type": "Product"},
        {"company_name": "Pine Labs", "domain": "pinelabs.com", "country": "India", "state": "Uttar Pradesh", "city": "Noida", "industry": "FinTech", "company_type": "Product"},
        {"company_name": "Info Edge", "domain": "infoedge.in", "country": "India", "state": "Uttar Pradesh", "city": "Noida", "industry": "Internet", "company_type": "Product"},
        {"company_name": "HCL Technologies", "domain": "hcltech.com", "country": "India", "state": "Uttar Pradesh", "city": "Noida", "industry": "IT Services", "company_type": "IT Service"},
        {"company_name": "RateGain", "domain": "rategain.com", "country": "India", "state": "Uttar Pradesh", "city": "Noida", "industry": "Travel Tech", "company_type": "SaaS"},
        {"company_name": "Moglix", "domain": "moglix.com", "country": "India", "state": "Uttar Pradesh", "city": "Noida", "industry": "B2B E-commerce", "company_type": "Product"},
        
        # Delhi
        {"company_name": "BharatPe", "domain": "bharatpe.com", "country": "India", "state": "Delhi", "city": "Delhi", "industry": "FinTech", "company_type": "Product"},
        {"company_name": "Lenskart", "domain": "lenskart.com", "country": "India", "state": "Delhi", "city": "Delhi", "industry": "E-commerce", "company_type": "Product"},
        {"company_name": "Snapdeal", "domain": "snapdeal.com", "country": "India", "state": "Delhi", "city": "Delhi", "industry": "E-commerce", "company_type": "Product"},
        
        # Chennai
        {"company_name": "Freshworks", "domain": "freshworks.com", "country": "India", "state": "Tamil Nadu", "city": "Chennai", "industry": "SaaS", "company_type": "SaaS"},
        {"company_name": "Zoho", "domain": "zoho.com", "country": "India", "state": "Tamil Nadu", "city": "Chennai", "industry": "SaaS", "company_type": "SaaS"},
        {"company_name": "Chargebee", "domain": "chargebee.com", "country": "India", "state": "Tamil Nadu", "city": "Chennai", "industry": "FinTech", "company_type": "SaaS"},
        {"company_name": "Kissflow", "domain": "kissflow.com", "country": "India", "state": "Tamil Nadu", "city": "Chennai", "industry": "SaaS", "company_type": "SaaS"},
        {"company_name": "TCS", "domain": "tcs.com", "country": "India", "state": "Maharashtra", "city": "Mumbai", "industry": "IT Services", "company_type": "IT Service"},
        
        # Mumbai
        {"company_name": "Dream11", "domain": "dream11.com", "country": "India", "state": "Maharashtra", "city": "Mumbai", "industry": "Gaming", "company_type": "Product"},
        {"company_name": "UpGrad", "domain": "upgrad.com", "country": "India", "state": "Maharashtra", "city": "Mumbai", "industry": "EdTech", "company_type": "Product"},
        {"company_name": "Pharmeasy", "domain": "pharmeasy.in", "country": "India", "state": "Maharashtra", "city": "Mumbai", "industry": "HealthTech", "company_type": "Product"},
        {"company_name": "Eruditus", "domain": "eruditus.com", "country": "India", "state": "Maharashtra", "city": "Mumbai", "industry": "EdTech", "company_type": "Product"},
        {"company_name": "Nykaa", "domain": "nykaa.com", "country": "India", "state": "Maharashtra", "city": "Mumbai", "industry": "E-commerce", "company_type": "Product"},
        {"company_name": "Zepto", "domain": "zeptonow.com", "country": "India", "state": "Maharashtra", "city": "Mumbai", "industry": "Quick Commerce", "company_type": "Product"},
        {"company_name": "CleverTap", "domain": "clevertap.com", "country": "India", "state": "Maharashtra", "city": "Mumbai", "industry": "MarTech", "company_type": "SaaS"},
        {"company_name": "Pepperfry", "domain": "pepperfry.com", "country": "India", "state": "Maharashtra", "city": "Mumbai", "industry": "E-commerce", "company_type": "Product"},
        
        # Kochi
        {"company_name": "Fingent", "domain": "fingent.com", "country": "India", "state": "Kerala", "city": "Kochi", "industry": "IT Services", "company_type": "IT Service"},
        {"company_name": "IBS Software", "domain": "ibsplc.com", "country": "India", "state": "Kerala", "city": "Kochi", "industry": "Travel Tech", "company_type": "Product"},
        
        # Ahmedabad / Gandhinagar
        {"company_name": "Lendingkart", "domain": "lendingkart.com", "country": "India", "state": "Gujarat", "city": "Ahmedabad", "industry": "FinTech", "company_type": "Product"},
        {"company_name": "Infibeam Avenues", "domain": "ia.ooo", "country": "India", "state": "Gujarat", "city": "Gandhinagar", "industry": "FinTech", "company_type": "Product"},
        {"company_name": "Hubilo", "domain": "hubilo.com", "country": "India", "state": "Gujarat", "city": "Ahmedabad", "industry": "Event Tech", "company_type": "SaaS"},
        
        # Chandigarh / Mohali
        {"company_name": "Jugnoo", "domain": "jugnoo.in", "country": "India", "state": "Punjab", "city": "Chandigarh", "industry": "Mobility", "company_type": "Product"},
        {"company_name": "Trigma", "domain": "trigma.com", "country": "India", "state": "Punjab", "city": "Chandigarh", "industry": "IT Services", "company_type": "IT Service"},
        
        # Jaipur
        {"company_name": "CarDekho", "domain": "cardekho.com", "country": "India", "state": "Rajasthan", "city": "Jaipur", "industry": "AutoTech", "company_type": "Product"},
        {"company_name": "GirnarSoft", "domain": "girnarsoft.com", "country": "India", "state": "Rajasthan", "city": "Jaipur", "industry": "IT Services", "company_type": "IT Service"},
        
        # Indore
        {"company_name": "Yash Technologies", "domain": "yash.com", "country": "India", "state": "Madhya Pradesh", "city": "Indore", "industry": "IT Services", "company_type": "IT Service"},
        {"company_name": "Systango", "domain": "systango.com", "country": "India", "state": "Madhya Pradesh", "city": "Indore", "industry": "IT Services", "company_type": "IT Service"},
        
        # Coimbatore
        {"company_name": "Kovai.co", "domain": "kovai.co", "country": "India", "state": "Tamil Nadu", "city": "Coimbatore", "industry": "SaaS", "company_type": "SaaS"},
        {"company_name": "Payoda", "domain": "payoda.com", "country": "India", "state": "Tamil Nadu", "city": "Coimbatore", "industry": "IT Services", "company_type": "IT Service"}
    ]
    
    with open('india_companies_master.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['company_name', 'domain', 'country', 'state', 'city', 'industry', 'company_type']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for company in companies:
            writer.writerow(company)

if __name__ == '__main__':
    main()
