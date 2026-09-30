import os
import sys
import json
import urllib.request

def inspect_env():
    print("=" * 75)
    print("INSPECTING INFOSYS ENVIRONMENT & CONFIG")
    print("=" * 75)

    urls = [
        "https://career.infosys.com/assets/environments/environment.json",
        "https://career.infosys.com/assets/json/Company.json",
        "https://career.infosys.com/assets/json/sourcelist.json"
    ]

    for u in urls:
        try:
            req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
            res = urllib.request.urlopen(req, timeout=10)
            data = json.loads(res.read().decode())
            print(f"\n--- {u} ---")
            print(json.dumps(data, indent=2)[:500])
        except Exception as e:
            print(f"Error on {u}: {e}")

if __name__ == "__main__":
    inspect_env()
