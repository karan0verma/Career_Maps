import requests
import re
import time

def generate_slugs(domain, company_name=None):
    slugs = []
    
    # Base from domain (e.g. openai.com -> openai)
    base = domain.lower().replace(".com", "").replace(".org", "").replace(".net", "").replace(".co", "").replace(".io", "").replace("www.", "")
    slugs.append(base)
    
    # Try removing non-alphanumeric chars
    clean_base = re.sub(r'[^a-z0-9]', '', base)
    if clean_base != base:
        slugs.append(clean_base)
        
    # Common suffixes
    slugs.append(f"{clean_base}inc")
    slugs.append(f"{clean_base}llc")
    slugs.append(f"{clean_base}corp")
    slugs.append(f"join{clean_base}")
    
    if company_name:
        c_slug = company_name.lower().replace(" ", "")
        if c_slug not in slugs:
            slugs.append(c_slug)
            
    # De-duplicate preserving order
    unique_slugs = []
    for s in slugs:
        if s not in unique_slugs and len(s) >= 3:
            unique_slugs.append(s)
            
    return unique_slugs[:5] # Max 5 guesses per ATS

def probe_greenhouse(domain, company_name=None):
    slugs = generate_slugs(domain, company_name)
    print(f"\n[{domain}] Testing Greenhouse slugs: {slugs}")
    
    start = time.time()
    req_count = 0
    
    for slug in slugs:
        req_count += 1
        url = f"https://boards-api.greenhouse.io/v1/boards/{slug}"
        try:
            r = requests.get(url, timeout=3)
            if r.status_code == 200:
                data = r.json()
                
                # VALIDATION
                board_name = data.get("name", "").lower()
                domain_base = domain.split(".")[0].lower().replace("www.", "")
                
                if domain_base in board_name or slug in board_name:
                    latency = time.time() - start
                    print(f"  -> SUCCESS: '{slug}' valid. Board Name: '{data.get('name')}'")
                    return True, req_count, latency
                else:
                    print(f"  -> REJECTED: '{slug}' valid API, but name mismatch: '{data.get('name')}' != '{domain_base}'")
            else:
                print(f"  -> FAIL: '{slug}' (HTTP {r.status_code})")
        except Exception as e:
            print(f"  -> ERROR: '{slug}' ({e})")
            
    latency = time.time() - start
    return False, req_count, latency

def main():
    domains = ["openai.com", "cloudflare.com", "canva.com", "pinterest.com", "coinbase.com", "hubspot.com"]
    
    total_reqs = 0
    total_time = 0
    
    for d in domains:
        found, reqs, lat = probe_greenhouse(d)
        total_reqs += reqs
        total_time += lat
        
    print("\n--- METRICS ---")
    print(f"Average requests per company: {total_reqs / len(domains):.1f}")
    print(f"Average probe latency per company: {total_time / len(domains):.2f}s")
    print(f"Max requests per company per ATS: 5")

if __name__ == "__main__":
    main()
