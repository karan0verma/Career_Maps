import requests

url = "https://asana.bamboohr.com/careers/list"
resp = requests.get(url, timeout=5)
try:
    data = resp.json()
    print("SUCCESS! JSON returned.")
    print(data)
except Exception as e:
    print("FAILED JSON PARSE:", e)
    
# Let's search the full html of https://asana.bamboohr.com/careers
resp = requests.get("https://asana.bamboohr.com/careers")
import re
jobs = re.findall(r'jobTitle', resp.text)
print(f"Found 'jobTitle' {len(jobs)} times in HTML.")
