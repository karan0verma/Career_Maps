import requests

url = "https://careers.wipro.com/feed"
resp = requests.get(url)
print("Wipro /feed:", resp.status_code)

url2 = "https://careers.wipro.com/services/rss"
try:
    resp2 = requests.get(url2)
    print("Wipro /services/rss:", resp2.status_code)
except:
    pass
