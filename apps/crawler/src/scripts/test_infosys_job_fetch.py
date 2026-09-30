import os
import sys
import json
import urllib.request
import urllib.parse

def test_fetch():
    locations = ['BANGALORE', 'HYDERABAD', 'PUNE', 'CHENNAI', 'MYSORE', 'CHANDIGARH', 'BHUBANESWAR', 'JAIPUR', 'MANGALORE', 'TRIVANDRUM', 'NAGPUR']
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://career.infosys.com/',
        'Origin': 'https://career.infosys.com'
    }

    # Let's test getHotJobsDetails with locations
    for loc in locations[:3]:
        url = f"https://intapgateway.infosysapps.com/careersci/search/intapjbsrch/getHotJobsDetails?location={urllib.parse.quote(loc)}&sourceId=1,21"
        try:
            req = urllib.request.Request(url, headers=headers)
            res = urllib.request.urlopen(req)
            data = json.loads(res.read().decode())
            jobs = data.get('hotJobsLists', [])
            print(f"Location {loc} -> returned {len(jobs)} jobs")
            if jobs:
                print("  Sample title:", jobs[0].get('postingTitle'), "| RefCode:", jobs[0].get('referenceCode'), "| Exp:", jobs[0].get('minExperienceLevel'), "-", jobs[0].get('maxExperienceLevel'))
        except Exception as e:
            print(f"Error on {loc}: {e}")

if __name__ == "__main__":
    test_fetch()
