import requests

domains = [
    "https://careers.wipro.com",
    "https://career.benteler.jobs",
    "https://career.elm.sa",
    "https://career.hipp.com"
]

endpoints = [
    "/services/api/rmk/search",
    "/services/cas/search",
    "/search/?q=&format=json"
]

for d in domains:
    print(f"Testing {d}...")
    for e in endpoints:
        url = d + e
        try:
            r = requests.get(url, timeout=5)
            print(f"  {e}: {r.status_code}")
            if r.status_code == 200:
                print(f"    {r.text[:100]}")
        except Exception as err:
            print(f"  {e}: Error {err}")
