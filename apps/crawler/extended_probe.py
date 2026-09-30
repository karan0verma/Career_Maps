import requests

session = requests.Session()
def probe(slug):
    # GH
    r = session.get(f"https://boards-api.greenhouse.io/v1/boards/{slug}", timeout=5)
    print(f"GH {slug}: {r.status_code}")
    
    # Ashby
    r = session.get(f"https://api.ashbyhq.com/posting-api/job-board/{slug}", timeout=5)
    print(f"Ashby API {slug}: {r.status_code}")
    
    # Lever
    r = session.get(f"https://api.lever.co/v0/postings/{slug}", timeout=5)
    print(f"Lever API {slug}: {r.status_code}")
    
    # SmartRecruiters
    r = session.get(f"https://api.smartrecruiters.com/v1/companies/{slug}/postings", timeout=5)
    print(f"SmartRecruiters API {slug}: {r.status_code}")

for s in ["openai", "plaid", "canva", "framer", "shopify", "doordash"]:
    print(f"--- {s} ---")
    probe(s)
