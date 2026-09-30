import requests
import json

def fetch_acko():
    url = "https://careers.kula.ai/api/internal/ats_job_posts?accountName=acko&page=1&type=ats_job_post.index&items=99"
    res = requests.get(url)
    if res.status_code == 200:
        data = res.json()
        print(data.keys())
        # Let's inspect data
        print("Data type:", type(data))
        if isinstance(data, dict):
            items = data.get('data', [])
            print(f"Found {len(items)} jobs.")
            for job in items[:5]:
                print(job.get('title'), job.get('location'), job.get('hostedUrl'))

if __name__ == "__main__":
    fetch_acko()
