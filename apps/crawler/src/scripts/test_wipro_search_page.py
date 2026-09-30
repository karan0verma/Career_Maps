import urllib.request
import json
from bs4 import BeautifulSoup

def test_wipro_search():
    url = "https://careers.wipro.com/search/?createNewAlert=false&q=&locationsearch=India"
    headers = {'User-Agent': 'Mozilla/5.0'}
    req = urllib.request.Request(url, headers=headers)
    html = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')
    soup = BeautifulSoup(html, 'html.parser')
    
    rows = soup.select('tr.data-row')
    print(f"Rows found on search page: {len(rows)}")
    
    for r in rows[:5]:
        title_tag = r.select_one('a.jobTitle-link')
        loc_tag = r.select_one('.jobLocation')
        date_tag = r.select_one('.jobDate')
        facility_tag = r.select_one('.jobFacility')
        
        title = title_tag.get_text(strip=True) if title_tag else ""
        href = title_tag.get('href') if title_tag else ""
        loc = loc_tag.get_text(strip=True) if loc_tag else ""
        facility = facility_tag.get_text(strip=True) if facility_tag else ""
        date = date_tag.get_text(strip=True) if date_tag else ""
        
        print(f"• Title: {title} | Loc: {loc} | Dept: {facility} | Date: {date} | Link: https://careers.wipro.com{href}")

    # Check total count in pagination header
    total_tag = soup.select_one('.paginationLabel, .search-results-indicator, .pagination-results')
    if total_tag:
        print("Pagination text:", total_tag.get_text(strip=True))

if __name__ == "__main__":
    test_wipro_search()
