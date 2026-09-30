import sys
import json
import subprocess
import os

domains = ["wipro.com", "hcltech.com", "paytm.com", "barco.com", "tcs.com", "globallogic.com"]

results = []

for domain in domains:
    print(f"Testing {domain}...")
    try:
        result = subprocess.run(
            [sys.executable, "run_single.py", domain],
            capture_output=True, text=True, cwd=os.getcwd()
        )
        
        # Parse the JSON output from stdout
        lines = result.stdout.strip().split('\n')
        json_output = None
        for line in reversed(lines):
            if line.startswith('{'):
                try:
                    json_output = json.loads(line)
                    break
                except:
                    pass
                    
        if json_output and 'target' in json_output:
            target = json_output['target']
            res = {
                "company": domain,
                "strategy": target.get("extraction_strategy"),
                "ats_type": target.get("ats_type"),
                "status": target.get("status")
            }
            print(res)
            results.append(res)
        else:
            print(f"Failed to parse JSON for {domain}: {result.stdout}")
            results.append({"company": domain, "error": "No JSON output"})
    except Exception as e:
        print(f"Error testing {domain}: {e}")

print("\n--- FINAL SUMMARY ---")
for r in results:
    print(r)
