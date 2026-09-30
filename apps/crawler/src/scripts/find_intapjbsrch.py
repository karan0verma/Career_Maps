import os
import sys
import re
import urllib.request

def search_intapjbsrch():
    html = urllib.request.urlopen("https://career.infosys.com/joblist").read().decode()
    js_files = re.findall(r'src="([^"]+\.js)"', html)
    print("Found JS files:", js_files)
    
    for js in js_files:
        url = js if js.startswith('http') else f"https://career.infosys.com/{js.lstrip('/')}"
        try:
            content = urllib.request.urlopen(url).read().decode('utf-8', errors='ignore')
            matches = re.findall(r'intapjbsrch/[a-zA-Z0-9_\-/]+', content)
            if matches:
                print(f"\nIn {url}:")
                for m in set(matches):
                    print("  ->", m)
                    
            # Also search for 'search' or 'joblist'
            routes = re.findall(r'/[a-zA-Z0-9_\-]+/search[a-zA-Z0-9_\-/]*', content)
            if routes:
                print("  Routes:", set(routes[:10]))
        except Exception as e:
            print(f"Error on {url}: {e}")

if __name__ == "__main__":
    search_intapjbsrch()
