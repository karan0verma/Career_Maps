import requests

url = "https://careers.wipro.com/feed"
resp = requests.get(url)
print(resp.text[:1000])
