import urllib.request
import json

def fetch_jobs():
    base_url = 'https://ejgk.fa.em2.oraclecloud.com/hcmRestApi/resources/latest/recruitingCEJobRequisitions?onlyData=true&expand=requisitionList&finder=findReqs;siteNumber=CX_1'
    limit = 25
    offset = 0
    all_jobs = []
    
    req = urllib.request.Request(f"{base_url}&limit={limit}&offset={offset}")
    req.add_header('User-Agent', 'Mozilla/5.0')
    response = urllib.request.urlopen(req)
    data = json.loads(response.read())
    
    if not data['items']:
        return all_jobs
        
    total_jobs = data['items'][0]['TotalJobsCount']
    print(f"Total jobs found: {total_jobs}")
    
    while offset < total_jobs:
        print(f"Fetching offset {offset}...")
        req = urllib.request.Request(f"{base_url}&limit={limit}&offset={offset}")
        req.add_header('User-Agent', 'Mozilla/5.0')
        response = urllib.request.urlopen(req)
        data = json.loads(response.read())
        
        req_list = data['items'][0].get('requisitionList', [])
        for job in req_list:
            if job.get('PrimaryLocationCountry') == 'IN' or (job.get('PrimaryLocation') and 'India' in job.get('PrimaryLocation')):
                extracted = {
                    'title': job.get('Title'),
                    'location': job.get('PrimaryLocation'),
                    'apply_url': f"https://ejgk.fa.em2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1/job/{job.get('Id')}"
                }
                all_jobs.append(extracted)
        
        offset += limit
        
    return all_jobs

if __name__ == '__main__':
    jobs = fetch_jobs()
    output_path = r'C:\Users\Ahana Singh\.gemini\antigravity\brain\b2157c5e-32e9-4e58-993a-3a6a43a0d53a\kpmg_jobs.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(jobs, f, indent=4)
    print(f"Saved {len(jobs)} jobs to {output_path}")
