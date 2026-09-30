import requests
import json

def check_eightfold(domain):
    print(f"\n--- Eightfold AI: {domain} ---")
    url = f"https://{domain}.eightfold.ai/api/apply/v2/jobs"
    try:
        resp = requests.get(url, timeout=5)
        print(f"GET {url}: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            jobs = data.get('positions', [])
            print(f"Found {len(jobs)} jobs. Keys: {list(jobs[0].keys()) if jobs else 'None'}")
    except Exception as e:
        print(e)

def check_bamboohr(domain):
    print(f"\n--- BambooHR: {domain} ---")
    url = f"https://{domain}.bamboohr.com/careers/list"
    try:
        resp = requests.get(url, timeout=5)
        print(f"GET {url}: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            jobs = data.get('result', [])
            print(f"Found {len(jobs)} jobs. Keys: {list(jobs[0].keys()) if jobs else 'None'}")
    except Exception as e:
        print(e)
        
    xml_url = f"https://{domain}.bamboohr.com/jobs/embed2.php"
    try:
        resp = requests.get(xml_url, timeout=5)
        print(f"GET {xml_url}: {resp.status_code}")
        if resp.status_code == 200:
            print(f"XML length: {len(resp.text)}")
    except Exception as e:
        print(e)

def check_jobvite(domain):
    print(f"\n--- Jobvite: {domain} ---")
    url = f"https://jobs.jobvite.com/{domain}/api/v1/jobs"
    try:
        resp = requests.get(url, timeout=5)
        print(f"GET {url}: {resp.status_code}")
        if resp.status_code == 200:
            # Jobvite XML usually
            text = resp.text
            print(f"Length: {len(text)}. Snippet: {text[:100]}")
    except Exception as e:
        print(e)

def check_zoho(domain):
    print(f"\n--- Zoho Recruit: {domain} ---")
    url = f"https://{domain}.zohorecruit.com/recruit/v2/public/Job_Openings"
    try:
        resp = requests.get(url, timeout=5)
        print(f"GET {url}: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            jobs = data.get('data', [])
            print(f"Found {len(jobs)} jobs. Keys: {list(jobs[0].keys()) if jobs else 'None'}")
    except Exception as e:
        print(e)

if __name__ == "__main__":
    check_eightfold("dexcom")
    check_eightfold("cognizant")
    
    check_bamboohr("soundcloud")
    check_bamboohr("canva")
    
    check_jobvite("fivetran")
    check_jobvite("universalmusicgroup")
    
    check_zoho("zylker")
    check_zoho("demo")
