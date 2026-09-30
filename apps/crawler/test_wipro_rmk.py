import requests

url = "https://careers.wipro.com/services/rmk/search"
resp = requests.post(url, json={})
print("Wipro rmk search:", resp.status_code)
print(resp.text[:500])
