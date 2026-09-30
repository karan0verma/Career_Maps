import requests

url = "https://meta.wd1.myworkdayjobs.com/wday/cxs/meta/Meta_Careers/jobs"
payload = {"limit": 20, "offset": 0}
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0"
}
try:
    resp = requests.post(url, json=payload, headers=headers)
    print(resp.status_code)
except Exception as e:
    print(e)
