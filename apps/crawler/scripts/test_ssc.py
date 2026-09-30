import requests
from bs4 import BeautifulSoup

def test_ssc():
    url = "https://ssc.gov.in/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        res = requests.get(url, headers=headers, verify=False, timeout=10)
        print("Status:", res.status_code)
        
        soup = BeautifulSoup(res.text, 'html.parser')
        notices = soup.find_all('a', href=True)
        
        pdf_links = []
        for a in notices:
            href = a.get('href', '').lower()
            if '.pdf' in href:
                pdf_links.append((a.text.strip()[:50], a.get('href')))
                
        print(f"Found {len(pdf_links)} PDF links on homepage")
        for p in pdf_links[:5]:
            print(p)
            
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings()
    test_ssc()
