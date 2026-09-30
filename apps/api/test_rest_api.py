import requests
resp = requests.get('http://localhost:3000/api/v1/opportunities?limit=5')
print(resp.json())
