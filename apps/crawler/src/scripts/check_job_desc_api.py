import urllib.request
import json

def check_job_desc():
    codes = ['INFSYS-EXTERNAL-249251', 'INFSYS-EXTERNAL-251345', 'INFSYS-EXTERNAL-251326']
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://career.infosys.com/joblist',
        'Origin': 'https://career.infosys.com'
    }

    for c in codes:
        url = f"https://intapgateway.infosysapps.com/careersci/search/intapjbsrch/getJobDesc?referenceCode={c}"
        try:
            req = urllib.request.Request(url, headers=headers)
            res = urllib.request.urlopen(req)
            data = json.loads(res.read().decode())
            print(f"\n--- {c} ---", flush=True)
            print("Status:", res.status, flush=True)
            print("Response:", json.dumps(data, indent=2)[:300], flush=True)
        except Exception as e:
            print(f"Error on {c}: {e}", flush=True)

if __name__ == "__main__":
    check_job_desc()
