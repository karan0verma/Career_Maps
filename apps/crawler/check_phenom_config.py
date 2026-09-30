import requests

url = "https://jobs.careers.microsoft.com/global/en/search"
resp = requests.get(url)
html = resp.text

# Look for phenom api config
for line in html.split('\n'):
    if 'api' in line.lower() and 'pcsx' in line.lower():
        print(line.strip())
