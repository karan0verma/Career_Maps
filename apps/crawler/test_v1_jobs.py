import requests

domains = [
    "https://career.benteler.jobs",
    "https://career.elm.sa",
    "https://career.hipp.com",
    "https://careers.wipro.com"
]

endpoint = "/services/recruiting/v1/jobs"

for d in domains:
    url = d + endpoint
    try:
        r = requests.get(url, timeout=5)
        print(f"{d}: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            if "content" in data:
                print(f"  Found {len(data['content'])} jobs in JSON!")
            else:
                print(f"  Keys: {data.keys()}")
    except Exception as e:
        print(f"{d}: Error {e}")
