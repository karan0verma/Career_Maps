import requests
from bs4 import BeautifulSoup
try:
    res = requests.get("https://jobs.pwc.com/search-jobs/India")
    print(res.status_code)
    soup = BeautifulSoup(res.text, 'html.parser')
    for a in soup.select('a[href*="/job/"]')[:5]:
        print(a.text.strip(), a.get('href'))
except Exception as e:
    print(e)
