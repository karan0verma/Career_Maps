import requests

def extract_infosys_api():
    url = "https://intapgateway.infosysapps.com/careersci/search/intapjbsrch/getHotJobsDetails"
    params = {
        "location": "All locations",
        "sourceId": "1,21"
    }
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }
    res = requests.get(url, params=params, headers=headers)
    print("Status:", res.status_code)
    
    if res.status_code == 200:
        data = res.json()
        jobs = data.get('hotJobsLists', [])
        print("Found jobs:", len(jobs))
        if jobs:
            print(jobs[0])

if __name__ == "__main__":
    extract_infosys_api()
