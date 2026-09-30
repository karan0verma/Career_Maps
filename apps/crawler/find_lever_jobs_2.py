import requests
import concurrent.futures

# More common startup names
companies = [
    "fivetran", "gong", "lattice", "hopin", "events", "clear", "plaid", 
    "coursera", "udacity", "duolingo", "khanacademy", "quizlet", "masterclass",
    "kiva", "change", "wework", "industrious", "convene", "knotel", 
    "compass", "redfin", "zillow", "trulia", "opendoor", "offerpad",
    "affirm", "klarna", "afterpay", "sezzle", "quadpay", "splitit",
    "chime", "varomoney", "n26", "monzo", "revolut", "starling", 
    "robinhood", "webull", "etoro", "public", "stash", "acorns",
    "wealthfront", "betterment", "personalcapital", "mint", "ynab",
    "kabbage", "fundbox", "bluevine", "ondex", "lendingclub",
    "sofi", "upstart", "prosper", "avant", "marcus", "discover",
    "braintree", "adyen", "checkout", "worldpay", "fiserv", "globalpayments",
    "docusign", "hellosign", "pandadoc", "signnow", "rightsignature",
    "zoominfo", "clearbit", "discoverorg", "insideview", "hunter",
    "lucidchart", "mural", "whimsical", "figjam", "excalidraw"
]

def check_lever(company):
    url = f"https://api.lever.co/v0/postings/{company}?mode=json"
    try:
        resp = requests.get(url, timeout=3)
        if resp.status_code == 200:
            data = resp.json()
            if len(data) > 0:
                return company, len(data)
    except Exception:
        pass
    return None

found = []
print("Starting concurrent checks...")
with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
    results = executor.map(check_lever, companies)
    for result in results:
        if result:
            found.append(result[0])
            print(f"Found Lever with jobs: {result[0]} ({result[1]} jobs)")
            if len(found) >= 14:
                break

print(f"\nTotal Lever companies found with jobs: {len(found)}")
print(found)
