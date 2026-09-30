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
print(json.dumps(data['data']['positions'][0], indent=2))
