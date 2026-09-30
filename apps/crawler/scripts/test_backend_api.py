import requests

try:
    res = requests.get("http://localhost:8000/api/v1/jobs?company_type=Government")
    print("Status:", res.status_code)
    if res.status_code != 200:
        print(res.text)
    else:
        print("Jobs found:", len(res.json().get('items', res.json())))
except Exception as e:
    print("Error:", e)
