import os
import sys
import json
import urllib.request

def test_wipro_endpoints():
    print("=" * 75)
    print("TESTING WIPRO SUCCESSFACTORS / JOBS2WEB API")
    print("=" * 75)

    urls = [
        "https://rmk-map-55.jobs2web.com/services/jobmap/jobs/facets?siteid=z8Q1GFVoohxx92Df1GPWZw%3D%3D&mapType=GOOGLE_MAP&jobTitle=&locale=en_US&brand=&limittobrand=true",
        "https://careers.wipro.com/services/jobmap/jobs/facets?siteid=z8Q1GFVoohxx92Df1GPWZw%3D%3D&mapType=GOOGLE_MAP&jobTitle=&locale=en_US&brand=&limittobrand=true",
        "https://rmk-map-55.jobs2web.com/services/jobmap/jobs/?siteid=z8Q1GFVoohxx92Df1GPWZw%3D%3D&locale=en_US",
        "https://careers.wipro.com/search/?createNewAlert=false&q=&locationsearch=India",
        "https://careers.wipro.com/api/jobs"
    ]

    for u in urls:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://careers.wipro.com/careers-home/'
        }
        try:
            req = urllib.request.Request(u, headers=headers)
            res = urllib.request.urlopen(req, timeout=10)
            data = res.read().decode('utf-8', errors='ignore')
            print(f"\n[URL] {u} -> Status: {res.status} (Length: {len(data)})")
            try:
                js = json.loads(data)
                print("  Type:", type(js))
                if isinstance(js, list):
                    print("  List count:", len(js))
                    if len(js) > 0:
                        print("  Sample:", str(js[0])[:250])
                elif isinstance(js, dict):
                    print("  Dict keys:", list(js.keys()))
                    for k in list(js.keys())[:3]:
                        if isinstance(js[k], list):
                            print(f"    '{k}' count: {len(js[k])} | Sample: {str(js[k][0])[:200] if len(js[k]) > 0 else 'empty'}")
            except Exception:
                print("  HTML/Text snippet:", data[:300])
        except Exception as e:
            print(f"[ERR] {u} -> {e}")

if __name__ == "__main__":
    test_wipro_endpoints()
