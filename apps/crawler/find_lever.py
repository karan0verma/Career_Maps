import requests
import concurrent.futures

companies = [
    # YC companies
    "stripe", "airbnb", "cruise", "instacart", "doordash", "coinbase", "twitch", 
    "reddit", "pagerduty", "gusto", "flexport", "scaleapi", "amplitude", "segment", 
    "plaid", "zapier", "brex", "rippling", "fivetran", "checkr", "benchling",
    "gocardless", "matterport", "webflow", "retreiver", "algolia", "figma", 
    "canva", "notion", "airtable", "miro", "framer", "invision", "loom", 
    "vanta", "lattice", "ramp", "deel", "remote", "oyster", "gem", "ashby",
    "kustomer", "intercom", "front", "drift", "gong", "outreach", "salesloft",
    # Crypto/Web3
    "alchemy", "opensea", "chainlink", "uniswap", "kraken", "gemini", "blockfi", 
    "celsius", "dapperlabs", "consensys", "polygon", "solana", "avalanche",
    # Dev tools
    "vercel", "netlify", "heroku", "fly", "render", "supabase", "planetscale", 
    "cockroachlabs", "elastic", "mongodb", "neo4j", "redis", "confluent", "databricks",
    "snowflake", "datadog", "newrelic", "dynatrace", "sentry", "logdna", "honeycomb",
    "launchdarkly", "split", "optimizely", "cypress", "postman", "insomnia", "swagger",
    # General Tech
    "spotify", "kpmg", "palantir", "gopuff", "roblox", "epicgames", "ea", "ubisoft",
    "zynga", "scopely", "niantic", "unity", "unreal", "autodesk", "adobe", "salesforce",
    "workday", "servicenow", "atlassian", "hubspot", "zendesk", "shopify", "bigcommerce",
    "magento", "wix", "squarespace", "weebly", "mailchimp", "klaviyo", "sendinblue",
    "hootsuite", "buffer", "sproutsocial", "sprinklr", "meltwater", "brandwatch",
    # Health/Bio
    "oscarhealth", "color", "23andme", "ro", "hims", "numin", "calm", "headspace",
    "springhealth", "lyrahealth", "modernhealth", "one-medical", "forward", "carbonhealth"
]

def check_lever(company):
    url = f"https://api.lever.co/v0/postings/{company}?mode=json"
    try:
        resp = requests.head(url, timeout=3)
        if resp.status_code == 200:
            return company
    except Exception:
        pass
    return None

found = []
print("Starting concurrent checks...")
with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
    results = executor.map(check_lever, companies)
    for result in results:
        if result:
            found.append(result)
            print(f"Found Lever: {result}")
        if len(found) >= 20:
            # Note: Executor might continue running other tasks, but that's fine
            break

print(f"\nTotal Lever companies found: {len(found)}")
print(found)

if found:
    # Let's inspect the first one
    test_company = found[0]
    print(f"\nInspecting schema for {test_company}")
    url = f"https://api.lever.co/v0/postings/{test_company}?mode=json"
    resp = requests.get(url).json()
    print(f"Total jobs for {test_company}: {len(resp)}")
    if resp:
        print("\nJob Keys:")
        print(list(resp[0].keys()))
