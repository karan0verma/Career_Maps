import requests
from bs4 import BeautifulSoup
import json
import math
import os
import time

def scrape_ey_jobs():
    base_url = 'https://careers.ey.com/search/'
    jobs = []
    
    startrow = 0
    batch_size = 25
    total_pages = 1
    current_page = 0
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    while current_page < total_pages:
        params = {
            'q': '',
            'locationsearch': 'India',
            'startrow': startrow
        }
        
        try:
            response = requests.get(base_url, params=params, headers=headers)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching page {current_page}: {e}")
            break
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        if current_page == 0:
            pagination = soup.find('span', class_='paginationLabel')
            if pagination:
                text = pagination.get_text(strip=True)
                try:
                    # Example: "1-25 of 1200 Results"
                    total_jobs_str = text.split('of')[-1].replace('Jobs', '').replace('Results', '').strip()
                    total_jobs_str = ''.join(c for c in total_jobs_str if c.isdigit())
                    if total_jobs_str:
                        total_jobs = int(total_jobs_str)
                        total_pages = math.ceil(total_jobs / batch_size)
                except Exception as e:
                    print(f"Could not parse pagination: {e}")
                    total_pages = 100 # Fallback
            else:
                total_pages = 100 # fallback if no pagination found
                
        job_rows = soup.find_all('tr', class_='data-row')
        
        if not job_rows:
            # Alternative layout for SuccessFactors
            job_rows = soup.find_all('li', class_='job-tile')

        if not job_rows:
            print(f"No more jobs found on page {current_page}. Stopping.")
            break
            
        for row in job_rows:
            title_tag = row.find('a', class_='jobTitle-link') or row.find('a', class_='job-title') or row.find('a')
            location_tag = row.find('span', class_='jobLocation') or row.find('span', class_='job-location') or row.find('div', class_='job-location')
            
            if title_tag:
                title = title_tag.get_text(strip=True)
                link = title_tag.get('href', '')
                if link.startswith('/'):
                    link = 'https://careers.ey.com' + link
                    
                location = location_tag.get_text(strip=True) if location_tag else 'India'
                
                if 'India' in location or 'IN' in location or 'Bengaluru' in location or 'Gurugram' in location or 'Noida' in location or 'Delhi' in location or 'Mumbai' in location or 'Pune' in location or 'Chennai' in location or 'Hyderabad' in location or 'Kolkata' in location:
                    jobs.append({
                        'title': title,
                        'location': location,
                        'apply_url': link
                    })
        
        startrow += batch_size
        current_page += 1
        time.sleep(1) # Polite scraping
        
    output_file = r'C:\Users\Ahana Singh\.gemini\antigravity\brain\b2157c5e-32e9-4e58-993a-3a6a43a0d53a\ey_jobs.json'
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(jobs, f, indent=4)
        
    print(f"Scraped {len(jobs)} jobs and saved to {output_file}")

if __name__ == '__main__':
    scrape_ey_jobs()
