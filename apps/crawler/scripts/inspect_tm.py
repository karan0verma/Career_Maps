import requests
from bs4 import BeautifulSoup

def inspect_tm():
    url = "https://careers.techmahindra.com/CurrentOpportunity.aspx"
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers)
    print("Status:", res.status_code)
    
    soup = BeautifulSoup(res.text, 'html.parser')
    jobs = soup.find_all('a', href=True)
    for j in jobs[:20]:
        if 'CurrentOpportunity' in j['href'] or 'JobDetails' in j['href']:
            print(j.text.strip(), "->", j['href'])

if __name__ == "__main__":
    inspect_tm()
