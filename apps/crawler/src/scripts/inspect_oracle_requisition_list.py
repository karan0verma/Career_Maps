import os
import sys
import json
import urllib.request

url = "https://eeho.fa.us2.oraclecloud.com/hcmRestApi/resources/latest/recruitingCEJobRequisitions?onlyData=true&expand=requisitionList.workLocation,requisitionList.otherWorkLocations,requisitionList.secondaryLocations,flexFieldsFacet.values,requisitionList.requisitionFlexFields&finder=findReqs;siteNumber=CX_45001,facetsList=LOCATIONS%3BWORK_LOCATIONS%3BWORKPLACE_TYPES%3BTITLES%3BCATEGORIES%3BORGANIZATIONS%3BPOSTING_DATES%3BFLEX_FIELDS,limit=25,locationId=300000000106965,sortBy=POSTING_DATES_DESC"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://careers.oracle.com/'
}

req = urllib.request.Request(url, headers=headers)
res = urllib.request.urlopen(req)
data = json.loads(res.read().decode())

print("Top Level Keys:", list(data.keys()))
items = data.get('items', [])
if items:
    print("Item 0 Keys:", list(items[0].keys()))
    req_list = items[0].get('requisitionList', [])
    print(f"requisitionList Length: {len(req_list)}")
    if req_list:
        print("\nSample Oracle Requisition:")
        print("  Id:", req_list[0].get('Id'))
        print("  Title:", req_list[0].get('Title'))
        print("  Primary Location:", req_list[0].get('PrimaryLocation'))
        print("  Workplace Type:", req_list[0].get('WorkplaceType'))
        print("  Posting Date:", req_list[0].get('PostedDate'))
