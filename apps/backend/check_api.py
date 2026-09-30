import urllib.request
import json
try:
    with urllib.request.urlopen('http://127.0.0.1:8000/api/v1/jobs') as response:
        jobs = json.loads(response.read())
        print(f'Fetched {len(jobs)} jobs.')
        if jobs:
            print(f"First job title: {jobs[0].get('title')}")
            print(f"First job company: {jobs[0].get('company', {}).get('display_name')}")
except Exception as e:
    print('Error:', e)
