import urllib.request
import csv

print("Downloading Majestic Top 1M list (streaming)...")
url = "http://downloads.majestic.com/majestic_million.csv"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

valid_tlds = ('.com', '.io', '.ai', '.co', '.net')
companies = []

with urllib.request.urlopen(req) as response:
    # Read line by line
    header = response.readline()
    for _ in range(1000000):
        line = response.readline()
        if not line:
            break
            
        try:
            line_str = line.decode('utf-8').strip()
            if not line_str:
                continue
            parts = line_str.split(',')
            if len(parts) > 2:
                domain = parts[2]
                if any(domain.endswith(tld) for tld in valid_tlds):
                    if domain not in ('wikipedia.org', 'wordpress.org', 'w3.org'):
                        companies.append(domain)
                        
                        if len(companies) % 1000 == 0:
                            print(f"Collected {len(companies)} domains...")
                            
            if len(companies) >= 5000:
                break
        except Exception:
            continue

print(f"Collected {len(companies)} domains.")

# Write to companies_5000.csv
csv_path = "companies_5000.csv"
with open(csv_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(["company_name"])
    for c in companies:
        writer.writerow([c])

print(f"Saved to {csv_path}")
