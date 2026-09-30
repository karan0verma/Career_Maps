import requests

companies = ['plaid', 'outreach', 'kraken', 'spotify', 'kpmg', 'palantir', 'gopuff', 'ro', 'lyrahealth', 'carbonhealth']
valid = 0

for test_company in companies:
    print(f"\n--- Inspecting {test_company} ---")
    url = f"https://api.lever.co/v0/postings/{test_company}?mode=json"
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            print(f"Total jobs: {len(data)}")
            if len(data) > 0:
                print("Job Keys:")
                print(list(data[0].keys()))
                print("Sample locations:")
                print(data[0].get("categories", {}).get("location"))
                valid += 1
        else:
            print(f"Error: {resp.status_code}")
    except Exception as e:
        print(f"Request failed: {e}")

print(f"\nCompanies with jobs: {valid}/{len(companies)}")
