import urllib.request
import json
import time

def extract_wipro_all():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://careers.wipro.com/'
    }
    
    facet_url = "https://rmk-map-55.jobs2web.com/services/jobmap/jobs/facets?siteid=z8Q1GFVoohxx92Df1GPWZw%3D%3D&mapType=GOOGLE_MAP&jobTitle=&locale=en_US&brand=&limittobrand=true"
    req_f = urllib.request.Request(facet_url, headers=headers)
    facets = json.loads(urllib.request.urlopen(req_f).read().decode())
    
    print(f"Total Clusters: {len(facets)}")
    all_jobs = {}
    
    # Prioritize clusters with jobs >= 1
    sorted_facets = sorted(facets, key=lambda x: x.get('total', 0), reverse=True)
    
    for idx, f in enumerate(sorted_facets):
        lat = f.get('latitude')
        lng = f.get('longitude')
        total = f.get('total', 0)
        
        if total == 0:
            continue
            
        url_cluster = f"https://rmk-map-55.jobs2web.com/services/jobmap/jobs/?siteid=z8Q1GFVoohxx92Df1GPWZw%3D%3D&locale=en_US&latitude={lat}&longitude={lng}"
        try:
            req_c = urllib.request.Request(url_cluster, headers=headers)
            res_c = json.loads(urllib.request.urlopen(req_c, timeout=10).read().decode())
            for j in res_c:
                jid = j.get('id')
                if jid and jid not in all_jobs:
                    all_jobs[jid] = j
        except Exception as e:
            print(f"Cluster ({lat}, {lng}) err: {e}")
            
        if (idx + 1) % 20 == 0 or idx == len(sorted_facets) - 1:
            print(f"Processed {idx+1}/{len(sorted_facets)} clusters -> Collected {len(all_jobs)} unique Wipro jobs")

    print(f"\nFinal Total Unique Wipro Jobs Extracted: {len(all_jobs)}")
    if all_jobs:
        sample = list(all_jobs.values())[0]
        print("Sample:", json.dumps(sample, indent=2))

if __name__ == "__main__":
    extract_wipro_all()
