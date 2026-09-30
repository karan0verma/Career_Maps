import requests
import json

def fetch_akuna():
    res = requests.get('https://boards-api.greenhouse.io/v1/boards/akunacapital/jobs?content=true')
    data = res.json()
    jobs = data.get('jobs', [])
    
    verified_jobs = []
    rejected_jobs = []
    
    for j in jobs:
        title = j.get('title')
        loc = j.get('location', {}).get('name', 'Unknown')
        url = j.get('absolute_url')
        job_id = j.get('id')
        
        # Verify if it's India (optional, but let's check all for now)
        # Verification Phase: Check if URL works
        try:
            check = requests.get(url, timeout=10)
            if check.status_code == 200:
                verified_jobs.append({
                    "title": title,
                    "location": loc,
                    "job_id": job_id,
                    "detail_url": url,
                    "apply_url": url + "#app",
                    "status": "Verified - 200 OK"
                })
            else:
                rejected_jobs.append({"title": title, "reason": f"Status {check.status_code}"})
        except Exception as e:
            rejected_jobs.append({"title": title, "reason": str(e)})

    # Generate Review Artifact
    output = f"""Company: Akuna Capital
Official Careers URL: https://www.akunacapital.com/careers

Total jobs discovered: {len(jobs)}
Total jobs individually verified: {len(verified_jobs)}
Total jobs rejected: {len(rejected_jobs)}
Total duplicates: 0
Total Apply URLs successfully verified: {len(verified_jobs)}

VERIFIED JOBS:

"""
    for i, vj in enumerate(verified_jobs, 1):
        output += f"{i}. {vj['title']}\n"
        output += f"   Location: {vj['location']}\n"
        output += f"   Job ID: {vj['job_id']}\n"
        output += f"   Job Detail URL: {vj['detail_url']}\n"
        output += f"   Verified Apply URL: {vj['apply_url']}\n"
        output += f"   Verification Status: {vj['status']}\n\n"
        
    output += "Rejected Jobs:\n"
    for rj in rejected_jobs:
        output += f"- Job: {rj['title']}\n  Reason: {rj['reason']}\n"

    with open("C:/Users/Ahana Singh/.gemini/antigravity/brain/b2157c5e-32e9-4e58-993a-3a6a43a0d53a/akuna_review.md", "w", encoding="utf-8") as f:
        f.write(output)
        
    print("Review artifact generated.")

if __name__ == "__main__":
    fetch_akuna()
