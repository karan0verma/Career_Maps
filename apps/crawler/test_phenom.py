import requests

url = "https://apply.careers.microsoft.com/api/pcsx/search?domain=microsoft.com&query=&location=&start=0&"
resp = requests.get(url)
print(resp.status_code)
if resp.status_code == 200:
    print(list(resp.json().keys()) if isinstance(resp.json(), dict) else "Not dict")
