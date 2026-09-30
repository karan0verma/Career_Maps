import urllib.request
import json

base = "https://eeho.fa.us2.oraclecloud.com/hcmRestApi/resources/latest/recruitingCEJobRequisitions?onlyData=true&expand=requisitionList.workLocation,requisitionList.otherWorkLocations,requisitionList.secondaryLocations,requisitionList.requisitionFlexFields&finder=findReqs;siteNumber=CX_45001,facetsList=LOCATIONS%3BTITLES,limit=25,"

queries = [
    ("SelectedLocationsFacet", "selectedLocationsFacet=300000000106965"),
    ("Keyword India", "keyword=India"),
    ("No filter limit=25", "")
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://careers.oracle.com/'
}

for name, q in queries:
    url = f"{base}{q}"
    print(f"\n--- Testing Oracle Query: {name} ---")
    try:
        req = urllib.request.Request(url, headers=headers)
        res = urllib.request.urlopen(req)
        d = json.loads(res.read().decode())
        item0 = d['items'][0]
        print("  TotalJobsCount:", item0.get('TotalJobsCount'))
        r_list = item0.get('requisitionList', [])
        print("  requisitionList len:", len(r_list))
        if r_list:
            print("  Sample 1:", r_list[0].get('Title'), "| Location:", r_list[0].get('PrimaryLocation'))
    except Exception as e:
        print("  Error:", e)
