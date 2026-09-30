import requests
from bs4 import BeautifulSoup
import re

def extract_phenom_html():
    url = "https://careers.cognizant.com/global-en/jobs/?location=India"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/115.0.0.0 Safari/537.36'
    }
    res = requests.get(url, headers=headers)
    
    soup = BeautifulSoup(res.text, 'html.parser')
    
    scripts = soup.find_all('script')
    for s in scripts:
        if s.string:
            if 'phApp.ddo' in s.string or 'window.phApp' in s.string or 'jobs' in s.string.lower():
                if 'jobListing' in s.string or 'total' in s.string:
                    print("Found potential job JSON script!")
                
    jobs = soup.find_all('li', class_='jobs-list-item')
    if not jobs:
        jobs = soup.find_all('div', class_='job-innerwrap')
    print("Found jobs in HTML elements:", len(jobs))
    
    if len(jobs) > 0:
        a = jobs[0].find('a')
        if a:
            print("Sample link:", a.get('href'))

if __name__ == "__main__":
    extract_phenom_html()
