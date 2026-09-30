import requests
import json

session = requests.Session()

def check_gh(slug):
    try:
        r = session.get(f"https://boards-api.greenhouse.io/v1/boards/{slug}", timeout=5)
        print(f"GH {slug}: {r.status_code}")
        if r.status_code == 200:
            print("  Name:", r.json().get('name'))
    except Exception as e:
        print(f"GH {slug}: Error {e}")

check_gh("openai")
check_gh("plaid")

def check_wd(slug, node):
    try:
        r = session.head(f"https://{slug}.{node}.myworkdayjobs.com/{slug.capitalize()}", timeout=5, allow_redirects=True)
        print(f"WD {slug} on {node}: {r.status_code} - {r.url}")
    except Exception as e:
        pass

for node in ["wd1", "wd3", "wd5", "wd12"]:
    check_wd("zoom", node)
    check_wd("canva", node)
