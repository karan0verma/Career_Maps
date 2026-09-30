import requests
import json
import logging

logging.basicConfig(level=logging.INFO)

companies = {
    "openai": ["openai"],
    "cloudflare": ["cloudflare", "cloudflareinc"],
    "canva": ["canva"],
    "pinterest": ["pinterest"],
    "coinbase": ["coinbase"],
    "hubspot": ["hubspot"]
}

def probe_greenhouse(slug):
    url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            # Verify it's not a completely empty/invalid board, though 200 is strong
            if "jobs" in data:
                return True
    except Exception:
        pass
    return False

def probe_workday(slug):
    # Try different tenant nodes wd1, wd3, wd5
    nodes = ["wd1", "wd3", "wd5", "wd12"]
    for node in nodes:
        url = f"https://{slug}.{node}.myworkdayjobs.com/{slug.capitalize()}"
        try:
            # Just do a HEAD to see if domain exists
            r = requests.head(url, timeout=3, allow_redirects=True)
            if r.status_code == 200:
                return True
        except requests.RequestException:
            pass
    return False

def main():
    results = {}
    for company, slugs in companies.items():
        found = None
        for slug in slugs:
            print(f"Probing {company} with slug '{slug}'...")
            
            # Greenhouse
            if probe_greenhouse(slug):
                found = f"GREENHOUSE (slug: {slug})"
                break
                
            # Workday
            if probe_workday(slug):
                found = f"WORKDAY (slug: {slug})"
                break
                
        results[company] = found if found else "NOT_FOUND"

    print("\n--- RESULTS ---")
    for company, res in results.items():
        print(f"{company}: {res}")

if __name__ == "__main__":
    main()
