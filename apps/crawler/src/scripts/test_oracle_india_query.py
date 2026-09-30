import urllib.request
import json

url = "https://eeho.fa.us2.oraclecloud.com/hcmRestApi/resources/latest/recruitingCEJobRequisitions?onlyData=true&expand=requisitionList.workLocation,requisitionList.otherWorkLocations,requisitionList.secondaryLocations,flexFieldsFacet.values,requisitionList.requisitionFlexFields&finder=findReqs;siteNumber=CX_45001,facetsList=LOCATIONS%3BTITLES,limit=25,selectedLocationsFacet=300000000106947,sortBy=POSTING_DATES_DESC"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://careers.oracle.com/'
}

req = urllib.request.Request(url, headers=headers)
res = urllib.request.urlopen(req)
d = json.loads(res.read().decode())
item0 = d['items'][0]
print("TotalJobsCount for India:", item0.get('TotalJobsCount'))
req_list = item0.get('requisitionList', [])
print(f"Fetched {len(req_list)} Oracle India requisitions in page 1!")
if req_list:
    for idx, r in enumerate(req_list[:5]):
        print(f"  [{idx+1}] {r.get('Title')} | Location: {r.get('PrimaryLocation')} | Id: {r.get('Id')}")
