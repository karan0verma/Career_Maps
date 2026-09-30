import requests
import concurrent.futures

companies = [
    # General Tech
    "roblox", "epicgames", "ea", "ubisoft", "zynga", "scopely", "niantic", "unity", 
    "unreal", "autodesk", "adobe", "salesforce", "workday", "servicenow", "atlassian", 
    "hubspot", "zendesk", "shopify", "bigcommerce", "magento", "wix", "squarespace", 
    "weebly", "mailchimp", "klaviyo", "sendinblue", "hootsuite", "buffer", "sproutsocial", 
    "sprinklr", "meltwater", "brandwatch", "pitch", "superhuman", "linear", "arc", "raycast",
    "kustomer", "intercom", "front", "drift", "gong", "salesloft", "ycombinator", "openai",
    "anthropic", "cohere", "huggingface", "scaleapi", "scale", "snackpass", "faire",
    "niantic", "pokemon", "nintendo", "xbox", "playstation", "sony", "samsung", "apple",
    "google", "meta", "amazon", "netflix", "yelp", "twitter", "x", "tesla", "spacex",
    "anduril", "rippling", "deel", "remote", "oyster", "gem", "ashby", "lever", "greenhouse",
    "workable", "bamboohr", "hibob", "gusto", "justworks", "paycom", "paylocity", "adp"
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
print("Starting concurrent checks for more companies...")
with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
    results = executor.map(check_lever, companies)
    for result in results:
        if result:
            found.append(result[0])
            print(f"Found Lever with jobs: {result[0]} ({result[1]} jobs)")
            if len(found) >= 20:
                break

print(f"\nTotal Lever companies found with jobs: {len(found)}")
print(found)
