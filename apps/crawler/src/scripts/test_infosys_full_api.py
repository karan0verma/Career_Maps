import os
import sys
import json
import urllib.request

def test_career_search():
    url = "https://intapgateway.infosysapps.com/careersci/search/intapjbsrch/getCareerSearchJobs?sourceId=1&searchText=ALL"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://career.infosys.com/joblist',
        'Origin': 'https://career.infosys.com'
    }
    
    req = urllib.request.Request(url, headers=headers)
    try:
        res = urllib.request.urlopen(req)
        data = json.loads(res.read().decode())
        print("Response Type:", type(data))
        if isinstance(data, list):
            print(f"Total Jobs Returned: {len(data)}")
            if len(data) > 0:
                print("First job keys:", list(data[0].keys()))
                print("First job sample:", json.dumps(data[0], indent=2))
        elif isinstance(data, dict):
            print("Dict keys:", list(data.keys()))
            for k in data.keys():
                if isinstance(data[k], list):
                    print(f"  List '{k}' count: {len(data[k])}")
                    if len(data[k]) > 0:
                        print("  Sample:", json.dumps(data[k][0], indent=2)[:400])
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test_career_search()
