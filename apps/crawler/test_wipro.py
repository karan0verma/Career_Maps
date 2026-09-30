import requests

url = "https://careers.wipro.com/search-jobs"
resp = requests.get(url)
print("Wipro search-jobs:", resp.status_code)

url2 = "https://jobs.wipro.com/search/?q="
try:
    resp2 = requests.get(url2)
    print("Wipro jobs.wipro.com:", resp2.status_code)
except Exception as e:
    print("Wipro jobs.wipro.com:", e)
