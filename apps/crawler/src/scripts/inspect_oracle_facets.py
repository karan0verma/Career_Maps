import urllib.request
import json

url = "https://eeho.fa.us2.oraclecloud.com/hcmRestApi/resources/latest/recruitingCEJobRequisitions?onlyData=true&expand=requisitionList.workLocation,requisitionList.otherWorkLocations,requisitionList.secondaryLocations,flexFieldsFacet.values,requisitionList.requisitionFlexFields&finder=findReqs;siteNumber=CX_45001,facetsList=LOCATIONS%3BTITLES,limit=25"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://careers.oracle.com/'
}

req = urllib.request.Request(url, headers=headers)
res = urllib.request.urlopen(req)
d = json.loads(res.read().decode())
item0 = d['items'][0]
loc_facet = item0.get('locationsFacet', [])

print(f"Found {len(loc_facet)} Location Facets in Oracle:")
for f in loc_facet:
    name = f.get('Name') or f.get('name') or f.get('FacetValue')
    cnt = f.get('Count') or f.get('count')
    code = f.get('Id') or f.get('Code') or f.get('FacetId')
    print(f"  • {name} (Count: {cnt}, Code/ID: {code})")
    if 'india' in str(name).lower():
        print(f"    ===> MATCHED INDIA FACET: {f}")
