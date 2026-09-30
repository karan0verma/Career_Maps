import requests
import json

url = "https://boards-api.greenhouse.io/v1/boards/airbnb/jobs?content=true"
resp = requests.get(url)
data = resp.json()

jobs = data.get("jobs", [])
print(f"Total jobs: {len(jobs)}")

if jobs:
    print("\nSample Job:")
    print(json.dumps(jobs[0], indent=2))
    
    print("\nKeys in job:")
    print(jobs[0].keys())
