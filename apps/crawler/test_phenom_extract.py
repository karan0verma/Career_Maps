import requests
import re
import urllib.parse

def extract_config(url):
    resp = requests.get(url)
    html = resp.text
    
    pcs_domain = None
    domain_param = None
    
    match = re.search(r'"pcsDomain"\s*:\s*"([^"]+)"', html)
    if match:
        pcs_domain = match.group(1)
        
    # the domain is often the base domain of the url itself, e.g. "microsoft.com"
    parsed = urllib.parse.urlparse(url)
    parts = parsed.netloc.split('.')
    domain_param = ".".join(parts[-2:])
    
    print("pcsDomain:", pcs_domain)
    print("domain_param:", domain_param)
    
extract_config("https://jobs.careers.microsoft.com/global/en/search")
