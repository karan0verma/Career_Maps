import requests

url = "https://careers.wipro.com/search-jobs"
resp = requests.get(url)
print(resp.text[:500])
with open("wipro.html", "w", encoding="utf-8") as f:
    f.write(resp.text)
