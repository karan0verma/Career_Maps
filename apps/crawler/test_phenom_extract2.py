import requests
import re
import urllib.parse

def extract_config(url):
    resp = requests.get(url)
    html = resp.text
    
    # Sometimes it's HTML encoded like &#34;pcsDomain&#34;: &#34;apply.careers.microsoft.com&#34;
    # Let's decode HTML entities first!
    import html as html_lib
    decoded_html = html_lib.unescape(html)
    
    pcs_domain = None
    match = re.search(r'"pcsDomain"\s*:\s*"([^"]+)"', decoded_html)
    if match:
        pcs_domain = match.group(1)
        
    print("pcsDomain:", pcs_domain)

extract_config("https://jobs.careers.microsoft.com/global/en/search")
