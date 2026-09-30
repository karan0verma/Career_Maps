import os
import sys
import re
import urllib.request
from bs4 import BeautifulSoup

def find_bundle_apis():
    print("=" * 75)
    print("INSPECTING INFOSYS ANGULAR JS BUNDLES")
    print("=" * 75)

    html = urllib.request.urlopen("https://career.infosys.com/joblist").read().decode()
    soup = BeautifulSoup(html, 'html.parser')
    scripts = [s.get('src') for s in soup.find_all('script') if s.get('src')]
    
    print(f"Found scripts: {scripts}")

    for s in scripts:
        if s.startswith('http'):
            s_url = s
        else:
            s_url = f"https://career.infosys.com/{s.lstrip('/')}"
        
        print(f"\nScanning: {s_url}")
        try:
            content = urllib.request.urlopen(s_url).read().decode('utf-8', errors='ignore')
            # Look for careersci endpoints
            matches = re.findall(r'careersci[a-zA-Z0-9_\-/]+', content)
            unique_matches = sorted(set(matches))
            print(f"Found {len(unique_matches)} careersci endpoints:")
            for m in unique_matches[:15]:
                print(f"  • {m}")
        except Exception as e:
            print(f"Error scanning {s_url}: {e}")

if __name__ == "__main__":
    find_bundle_apis()
