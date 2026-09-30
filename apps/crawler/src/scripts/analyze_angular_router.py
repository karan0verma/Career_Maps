import os
import sys
import re
import urllib.request

def analyze_angular_router():
    content = urllib.request.urlopen("https://career.infosys.com/main.js").read().decode('utf-8', errors='ignore')
    
    # Search for jobdesc route definition
    matches = re.findall(r'path:\s*["\']jobdesc["\'][^}]+', content)
    print("Found jobdesc route definitions:", len(matches))
    for m in matches:
        print("  ->", m)

    # Search for getJobDesc or referenceCode or params in main.js
    param_matches = re.findall(r'getJobDesc[^\(]+\([^\)]*\)', content)
    print("\ngetJobDesc usage:", param_matches)

    # Search for queryParams mapping for jobdesc
    qp_matches = re.findall(r'queryParams[^{]+{[^}]+}', content)
    print("\nQuery params mappings:", qp_matches[:10])

if __name__ == "__main__":
    analyze_angular_router()
