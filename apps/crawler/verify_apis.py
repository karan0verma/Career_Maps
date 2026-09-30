import requests
import json

def verify_ashby(token):
    print(f"\n--- Testing Ashby: {token} ---")
    url = f"https://api.ashbyhq.com/jobBoard/{token}"
    try:
        resp = requests.get(url, timeout=5)
        print(f"GET {url}: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            jobs = data.get("jobs", [])
            print(f"Found {len(jobs)} jobs. First job keys: {list(jobs[0].keys()) if jobs else 'None'}")
            return
    except Exception as e:
        print(e)
        
    url2 = f"https://jobs.ashbyhq.com/api/non-user-graphql?op=ApiJobBoardWithTeams"
    payload = {
        "operationName": "ApiJobBoardWithTeams",
        "variables": {"organizationHostedJobsPageName": token},
        "query": "query ApiJobBoardWithTeams($organizationHostedJobsPageName: String!) { jobBoard: jobBoardWithTeams(organizationHostedJobsPageName: $organizationHostedJobsPageName) { teams { id name } jobPostings { id title locationName employmentType teamId } } }"
    }
    try:
        resp = requests.post(url2, json=payload, timeout=5)
        print(f"POST {url2}: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            if "errors" in data:
                print("GraphQL Errors:", json.dumps(data["errors"], indent=2))
            else:
                print("GraphQL response keys:", data.keys())
    except Exception as e:
        print(e)

def verify_smartrecruiters(token):
    print(f"\n--- Testing SmartRecruiters: {token} ---")
    url = f"https://api.smartrecruiters.com/v1/companies/{token}/postings"
    try:
        resp = requests.get(url, timeout=5)
        print(f"GET {url}: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            jobs = data.get("content", [])
            print(f"Found {len(jobs)} jobs. First job keys: {list(jobs[0].keys()) if jobs else 'None'}")
    except Exception as e:
        print(e)

def verify_workable(token):
    print(f"\n--- Testing Workable: {token} ---")
    url = f"https://apply.workable.com/api/v3/accounts/{token}/jobs"
    payload = {"token": "", "query": "", "location": [], "department": [], "worktype": [], "remote": []}
    try:
        resp = requests.post(url, json=payload, timeout=5)
        print(f"POST {url}: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            jobs = data.get("results", [])
            print(f"Found {len(jobs)} jobs. First job keys: {list(jobs[0].keys()) if jobs else 'None'}")
            print(f"Next token available: {data.get('nextPage') is not None}")
    except Exception as e:
        print(e)

if __name__ == "__main__":
    verify_ashby("reddit")
    verify_ashby("vanta")
    verify_smartrecruiters("visa")
    verify_smartrecruiters("roblox")
    verify_workable("turing")
    verify_workable("eurobank")
