import os
import sys
import json
import urllib.request

def verify_user_numbers():
    print("=" * 80)
    print("PRECISE LIVE VERIFICATION FOR USER'S EXACT NUMBERS")
    print("=" * 80)

    # 1. Amazon India Bengaluru Breakdown
    print("\n1. Amazon India Location Breakdown:")
    amz_url = "https://www.amazon.jobs/en/search.json?country=IND&facets%5B%5D=normalized_location&offset=0&result_limit=1"
    req = urllib.request.Request(amz_url, headers={'User-Agent': 'Mozilla/5.0'})
    res = urllib.request.urlopen(req)
    amz_data = json.loads(res.read().decode())
    print("   Total Amazon India Jobs:", amz_data.get('hits'))
    locs = amz_data.get('facets', {}).get('normalized_location', {})
    
    blr_jobs = 0
    for k, v in locs.items():
        if 'bengaluru' in k.lower() or 'bangalore' in k.lower():
            print(f"   -> {k}: {v}")
            blr_jobs += v
    print(f"   Total Amazon Bengaluru Jobs: {blr_jobs}")
    print("   Other Major Amazon India Locations:")
    for k, v in list(locs.items())[:10]:
        if 'bengaluru' not in k.lower() and 'bangalore' not in k.lower():
            print(f"   -> {k}: {v}")

    # 2. Oracle India Exact Count
    print("\n2. Oracle Exact Count (CX_45001 India Location):")
    try:
        # India locationId in Oracle Cloud CX: 300000000106965
        ora_url = "https://eeho.fa.us2.oraclecloud.com/hcmRestApi/resources/latest/recruitingCEJobRequisitions?onlyData=true&finder=findReqs;siteNumber=CX_45001,facetsList=LOCATIONS,limit=1,locationId=300000000106965"
        req = urllib.request.Request(ora_url, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://careers.oracle.com/'})
        res = urllib.request.urlopen(req)
        ora_data = json.loads(res.read().decode())
        print("   Oracle India Requisitions:", ora_data.get('count'))
    except Exception as e:
        print("   Oracle error:", e)

if __name__ == "__main__":
    verify_user_numbers()
