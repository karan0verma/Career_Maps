import requests
import json
import time

def scrape_hsbc_jobs():
    base_url = "https://mycareer.hsbc.com/api/apply/v2/jobs"
    jobs = []
    start = 0
    num = 50
    domain = "hsbc.com" # Typical Eightfold domain format

    while True:
        params = {
            "domain": domain,
            "start": start,
            "num": num,
            "location": "India", 
        }
        print(f"Fetching start={start}...")
        try:
            response = requests.get(base_url, params=params, headers={"User-Agent": "Mozilla/5.0"})
            if response.status_code != 200:
                print(f"Failed to fetch: {response.status_code} {response.text}")
                # Try without domain if hsbc.com fails
                if domain == "hsbc.com":
                    domain = "mycareer.hsbc.com"
                    continue
                break
            
            data = response.json()
            positions = data.get("positions", [])
            if not positions:
                break
            
            for pos in positions:
                title = pos.get("name", "")
                loc = pos.get("location", "")
                
                # Check if it's actually in India
                if "India" not in loc and "IND" not in loc:
                    continue
                    
                apply_url = pos.get("url", "")
                if apply_url and not apply_url.startswith("http"):
                    apply_url = "https://mycareer.hsbc.com" + apply_url
                
                jobs.append({
                    "title": title,
                    "location": loc,
                    "apply_url": apply_url
                })
            
            start += num
            time.sleep(1) # simple rate limit
        except Exception as e:
            print(f"Exception: {e}")
            break

    print(f"Total jobs extracted: {len(jobs)}")
    output_path = r"C:\Users\Ahana Singh\.gemini\antigravity\brain\b2157c5e-32e9-4e58-993a-3a6a43a0d53a\hsbc_jobs.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(jobs, f, indent=4)
    print(f"Saved to {output_path}")

if __name__ == "__main__":
    scrape_hsbc_jobs()
