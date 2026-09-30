import urllib.request
import json

def test_j2w():
    # Test jobmap API
    base = "https://rmk-map-55.jobs2web.com/services/jobmap/jobs/?siteid=z8Q1GFVoohxx92Df1GPWZw%3D%3D&locale=en_US"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://careers.wipro.com/'
    }
    
    # Test facets
    facet_url = "https://rmk-map-55.jobs2web.com/services/jobmap/jobs/facets?siteid=z8Q1GFVoohxx92Df1GPWZw%3D%3D&mapType=GOOGLE_MAP&jobTitle=&locale=en_US&brand=&limittobrand=true"
    req_f = urllib.request.Request(facet_url, headers=headers)
    facets = json.loads(urllib.request.urlopen(req_f).read().decode())
    print(f"Total Facets (Clusters): {len(facets)}")
    total_facets_jobs = sum(f.get('total', 0) for f in facets)
    print(f"Total jobs represented across all clusters: {total_facets_jobs}")
    
    for f in facets[:5]:
        print(f"  Lat: {f.get('latitude')}, Lng: {f.get('longitude')}, Total: {f.get('total')}")

    # Test fetching jobs for a specific cluster or bounding box
    # Let's test bounding box or location queries
    lat, lng = facets[0].get('latitude'), facets[0].get('longitude')
    url_cluster = f"https://rmk-map-55.jobs2web.com/services/jobmap/jobs/?siteid=z8Q1GFVoohxx92Df1GPWZw%3D%3D&locale=en_US&latitude={lat}&longitude={lng}"
    req_c = urllib.request.Request(url_cluster, headers=headers)
    res_c = json.loads(urllib.request.urlopen(req_c).read().decode())
    print(f"\nCluster ({lat}, {lng}) returned: {len(res_c)} jobs")
    if len(res_c) > 0:
        print("Sample job:", json.dumps(res_c[0], indent=2))

if __name__ == "__main__":
    test_j2w()
