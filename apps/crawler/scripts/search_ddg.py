import requests
from bs4 import BeautifulSoup
import urllib.parse

def search():
    url = 'https://html.duckduckgo.com/html/?q=' + urllib.parse.quote('site:careers.techmahindra.com')
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    for a in soup.find_all('a', class_='result__url'):
        print(a.text.strip())

if __name__ == "__main__":
    search()
