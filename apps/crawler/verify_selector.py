import sys
import json
import subprocess
import os

# We will supply the direct career URL so it doesn't fail at the finder stage
targets = [
    ("wipro.com", None),
    ("tcs.com", "https://www.tcs.com/careers"),
    ("globallogic.com", "https://www.globallogic.com/careers/"),
    ("maqsoftware.com", "https://maqsoftware.com/careers")
]

results = []
for domain, url in targets:
    print(f"Testing {domain}...")
    try:
        # Instead of calling run_single directly, let's write a small inline runner that sets the URL
        code = f"""
import json
from src.discovery.models import Target
from src.discovery.detection import StrategySelector
target = Target(company_name="{domain}", domain="{domain}", career_url="{url}" if "{url}" != "None" else "https://{domain}/careers")
selector = StrategySelector()
target = selector.process(target)
print(json.dumps(target.to_dict()))
"""
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True, text=True, cwd=os.getcwd()
        )
        
        lines = result.stdout.strip().split('\n')
        json_output = None
        for line in reversed(lines):
            if line.startswith('{'):
                try:
                    json_output = json.loads(line)
                    break
                except:
                    pass
        if json_output:
            res = {
                "company": domain,
                "strategy": json_output.get("extraction_strategy"),
                "ats_type": json_output.get("ats_type"),
                "status": json_output.get("status")
            }
            results.append(res)
            print(res)
        else:
            print("Failed:", result.stdout, result.stderr)
    except Exception as e:
        print("Error:", e)

print("--- SUMMARY ---")
for r in results:
    print(r)
