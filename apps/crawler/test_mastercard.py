import requests
import json

url = "https://mastercard.wd1.myworkdayjobs.com/wday/cxs/mastercard/CorporateCareers/jobs"
payload = {"limit": 20, "offset": 0}
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0"
}

resp = requests.post(url, json=payload, headers=headers)
print(resp.status_code)
print(resp.text[:500])
