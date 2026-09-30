import requests

url = "https://boards-api.greenhouse.io/v1/boards/spacex/jobs?content=true"
resp = requests.head(url)
print("HEAD Headers:")
for k, v in resp.headers.items():
    print(f"{k}: {v}")
    
resp2 = requests.get(url)
print("\nGET Headers:")
for k, v in resp2.headers.items():
    if k.lower() != 'x-amz-cf-id':
        print(f"{k}: {v}")
        
print(f"\nNumber of jobs: {len(resp2.json().get('jobs', []))}")
