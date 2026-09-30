import urllib.request
import re
import json

def get_lever_companies():
    companies = set()
    url = "https://html.duckduckgo.com/html/?q=site:jobs.lever.co"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        html = urllib.request.urlopen(req).read().decode('utf-8')
        # Extract names from URLs like jobs.lever.co/companyname
        matches = re.findall(r'jobs\.lever\.co/([^/"\?]+)', html)
        for m in matches:
            if m not in ['cookie-policy', 'privacy-policy', 'terms']:
                companies.add(m)
    except Exception as e:
        print(e)
    return list(companies)

c = get_lever_companies()
print("Found via search:", c)
