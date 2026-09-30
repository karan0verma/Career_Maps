import requests

def test_jobsearch():
    url = "https://intapgateway.infosysapps.com/careersci/search/intapjbsrch/jobSearch"
    payload = {
        "searchCriteria": {
            "country": ["India"],
            "keyword": ""
        },
        "pageNumber": 1,
        "pageSize": 20
    }
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/json"
    }
    res = requests.post(url, json=payload, headers=headers)
    print("Status:", res.status_code)
    if res.status_code == 200:
        print(res.text[:500])
        
if __name__ == "__main__":
    test_jobsearch()
