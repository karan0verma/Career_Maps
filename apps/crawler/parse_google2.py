from bs4 import BeautifulSoup

def parse():
    with open("google_jobs.html", "r", encoding="utf-8") as f:
        html = f.read()
        
    soup = BeautifulSoup(html, 'html.parser')
    li = soup.find('li', class_='lLd3Je')
    if li:
        print(li.prettify())
            
if __name__ == "__main__":
    parse()
