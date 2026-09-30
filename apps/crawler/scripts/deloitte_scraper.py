import json
import requests
import time
import os

OUTPUT_FILE = r"C:\Users\Ahana Singh\.gemini\antigravity\brain\b2157c5e-32e9-4e58-993a-3a6a43a0d53a\deloitte_jobs.json"

def fetch_jobs():
    # Attempting to fetch jobs from the suspected Phenom People API endpoint
    url = "https://jobs2.deloitte.com/api/jobs"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    all_jobs = []
    offset = 0
    limit = 100
    
    while True:
        payload = {
            "query": "",
            "location": ["India"],
            "from": offset,
            "size": limit
        }
        
        try:
            print(f"Fetching jobs from offset {offset}...")
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code != 200:
                print(f"Failed POST with status {response.status_code}. Trying GET fallback...")
                response = requests.get(
                    f"https://jobs2.deloitte.com/api/jobs?location=India&limit={limit}&offset={offset}",
                    headers=headers
                )
                if response.status_code != 200:
                    print("GET fallback also failed. Breaking.")
                    break
                    
            data = response.json()
            
            # Phenom people API structures vary; handling a few common ones
            jobs_list = []
            if isinstance(data, dict):
                jobs_list = data.get("jobs", [])
                if not jobs_list and "data" in data:
                    jobs_list = data["data"].get("jobs", [])
            elif isinstance(data, list):
                jobs_list = data
                
            if not jobs_list:
                print("No more jobs found.")
                break
                
            added_this_batch = 0
            for job_item in jobs_list:
                # Sometimes the job data is wrapped in a 'job' object
                job = job_item.get("job", job_item)
                
                title = job.get("title", "")
                location = job.get("location", "")
                # Different APIs use different keys for ID
                job_id = job.get("reqId") or job.get("jobSeqNo") or job.get("jobId") or ""
                
                apply_url = job.get("applyUrl") or f"https://jobs2.deloitte.com/ui/en/job/{job_id}"
                
                # Check location string to ensure it's in India
                loc_str = str(location).lower()
                if "india" in loc_str or " in " in f" {loc_str} ":
                    all_jobs.append({
                        "title": title,
                        "location": location,
                        "apply_url": apply_url
                    })
                    added_this_batch += 1
                    
            if added_this_batch == 0 and len(jobs_list) > 0:
                print("Jobs found but none matched the India location filter.")
            
            # Stop if we fetched fewer than requested (end of pagination)
            if len(jobs_list) < limit:
                break
                
            offset += limit
            time.sleep(1) # Be polite
            
        except Exception as e:
            print(f"Exception occurred: {e}")
            break
            
    return all_jobs

def save_jobs(jobs):
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(jobs, f, indent=4, ensure_ascii=False)
    print(f"Successfully saved {len(jobs)} jobs to {OUTPUT_FILE}")

if __name__ == "__main__":
    jobs = fetch_jobs()
    save_jobs(jobs)
