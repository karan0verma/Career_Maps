import os
import sys
import json
import urllib.request

def inspect_all():
    print("=" * 75)
    print("EXPLORING INFOSYS INTAP GATEWAY ENDPOINTS")
    print("=" * 75)

    urls = [
        "https://intapgateway.infosysapps.com/careersci/search/intapjbsrch//jobListingPage/locationCount?sourceId=1,21",
        "https://intapgateway.infosysapps.com/careersci/search/intapjbsrch//jobListingPage/functionalAreaCount?sourceId=1,21"
    ]

    for u in urls:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://career.infosys.com/'})
        res = urllib.request.urlopen(req)
        data = json.loads(res.read().decode())
        print(f"\n--- {u} ---")
        print(f"Count: {len(data)}")
        for item in data[:5]:
            print(" ", item)

if __name__ == "__main__":
    inspect_all()
