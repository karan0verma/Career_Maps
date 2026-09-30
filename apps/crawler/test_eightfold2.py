import requests
import json

url = "https://apply.careers.microsoft.com/api/pcsx/search"
params = {
    "domain": "microsoft.com",
    "start": 0,
    "limit": 10
}
resp = requests.get(url, params=params)
data = resp.json()
print("Keys in data:", data.keys())
print("Keys in data['data']:", data['data'].keys() if isinstance(data['data'], dict) else type(data['data']))
if 'jobs' in data['data']:
    print("Jobs type:", type(data['data']['jobs']))
    print(json.dumps(data['data']['jobs'][0], indent=2))
