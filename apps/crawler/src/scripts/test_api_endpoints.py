import urllib.request
import json

def test_api():
    res = json.loads(urllib.request.urlopen("http://localhost:8000/api/v1/companies").read().decode())
    print("=" * 70)
    print("LIVE COMPANIES & OPEN POSITIONS ON PLATFORM")
    print("=" * 70)
    total = 0
    for c in res:
        name = c.get('display_name')
        jobs = c.get('total_active_jobs', 0)
        total += jobs
        print(f"• {name:<35} : {jobs:>6} Open Positions")
    print("-" * 70)
    print(f"TOTAL ACTIVE JOBS AVAILABLE        : {total:>6} Open Positions")
    print("=" * 70)

if __name__ == "__main__":
    test_api()
