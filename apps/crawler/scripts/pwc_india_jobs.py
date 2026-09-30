import json
import urllib.request
import os
import time

def get_jobs():
    url = "https://pwc.wd3.myworkdayjobs.com/wday/cxs/pwc/Global_Experienced_Careers/jobs"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    all_jobs = []
    limit = 20
    offset = 0
    total = None
    
    # Common Indian keywords and cities to verify location
    indian_cities = ['bangalore', 'bengaluru', 'mumbai', 'delhi', 'new delhi', 'gurgaon', 'gurugram', 'noida', 'hyderabad', 'pune', 'kolkata', 'chennai', 'ahmedabad', 'india', 'ind']
    
    while True:
        payload = {
            "appliedFacets": {},
            "limit": limit,
            "offset": offset,
            "searchText": "India"
        }
        
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers=headers)
        
        try:
            with urllib.request.urlopen(req) as response:
                res_data = json.loads(response.read().decode('utf-8'))
        except Exception as e:
            print(f"Error fetching data at offset {offset}: {e}")
            break
            
        if total is None:
            total = res_data.get('total', 0)
            print(f"Total jobs found matching 'India': {total}")
            
        job_postings = res_data.get('jobPostings', [])
        if not job_postings:
            break
            
        for job in job_postings:
            locations = job.get('locationsText', '')
            locations_lower = locations.lower()
            
            # Check if it's actually an India location
            is_india = any(city in locations_lower for city in indian_cities)
            
            if is_india:
                apply_url = f"https://pwc.wd3.myworkdayjobs.com/en-US/Global_Experienced_Careers{job.get('externalPath', '')}"
                extracted_job = {
                    'title': job.get('title', ''),
                    'location': locations,
                    'apply_url': apply_url
                }
                all_jobs.append(extracted_job)
                
        offset += limit
        print(f"Processed {offset} jobs...")
        
        if offset >= total:
            break
            
        time.sleep(1) # Be polite to the server
            
    return all_jobs

def main():
    print("Starting extraction of PwC India jobs...")
    jobs = get_jobs()
    print(f"Finished extraction. Found {len(jobs)} actual jobs in India.")
    
    output_path = r"C:\Users\Ahana Singh\.gemini\antigravity\brain\b2157c5e-32e9-4e58-993a-3a6a43a0d53a\pwc_jobs.json"
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(jobs, f, indent=4, ensure_ascii=False)
        
    print(f"Saved extracted jobs to {output_path}")

if __name__ == "__main__":
    main()
