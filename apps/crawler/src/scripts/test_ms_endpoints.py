import urllib.request
import json
import time

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Referer': 'https://jobs.careers.microsoft.com/global/en/search'
}

# Test 1: GCSServices
url1 = "https://gcsservices.careers.microsoft.com/search/api/v1/search?lc=India&l=en_us&pg=1&pgSz=20&o=Recent"
print("Testing GCSServices API...")
try:
    req = urllib.request.Request(url1, headers=headers)
    res = urllib.request.urlopen(req)
    d = json.loads(res.read().decode())
    print("GCSServices Result count:", d.get('operationResult', {}).get('result', {}).get('totalJobs'))
    print("Sample Job:", d.get('operationResult', {}).get('result', {}).get('jobs', [])[0].get('title'))
except Exception as e:
    print("GCSServices Error:", e)

# Test 2: PCSX with delay
time.sleep(1.5)
print("\nTesting PCSX API with proper delay...")
url2 = "https://apply.careers.microsoft.com/api/pcsx/search?domain=microsoft.com&query=&location=India&start=0&num=20"
try:
    req = urllib.request.Request(url2, headers=headers)
    res = urllib.request.urlopen(req)
    d = json.loads(res.read().decode())
    print("PCSX Result count:", d.get('data', {}).get('count'))
    print("Sample Job:", d.get('data', {}).get('positions', [])[0].get('name'))
except Exception as e:
    print("PCSX Error:", e)
