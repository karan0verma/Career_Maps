import urllib.request
import json

# Test Oracle Cloud HCM endpoint with different country queries
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://careers.oracle.com/'
}

urls = [
    ("With country keyword", "https://eeho.fa.us2.oraclecloud.com/hcmRestApi/resources/latest/recruitingCEJobRequisitions?onlyData=true&finder=findReqs;siteNumber=CX_45001,facetsList=LOCATIONS%3BTITLES,limit=25,keyword=India"),
    ("With location query", "https://eeho.fa.us2.oraclecloud.com/hcmRestApi/resources/latest/recruitingCEJobRequisitions?onlyData=true&finder=findReqs;siteNumber=CX_45001,facetsList=LOCATIONS%3BTITLES,limit=25,location=India"),
    ("Default site without locationId", "https://eeho.fa.us2.oraclecloud.com/hcmRestApi/resources/latest/recruitingCEJobRequisitions?onlyData=true&finder=findReqs;siteNumber=CX_45001,facetsList=LOCATIONS%3BTITLES,limit=25")
]

for label, u in urls:
    print(f"\nTesting: {label}")
    try:
        req = urllib.request.Request(u, headers=headers)
        res = urllib.request.urlopen(req)
        d = json.loads(res.read().decode())
        print(f"  Count: {d.get('count')}, Items: {len(d.get('items', []))}")
        if d.get('items'):
            print(f"  Sample Item Location: {d.get('items')[0].get('PrimaryLocation')}")
    except Exception as e:
        print(f"  Error: {e}")
