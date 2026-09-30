import csv
import json
import os
from datetime import datetime

def load_master_inventory(csv_path: str) -> dict:
    inventory = {}
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            inventory[row['domain']] = row
    return inventory

def main():
    master_inventory = load_master_inventory('india_companies_master.csv')
    
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)
    
    companies_seed = []
    unsupported_companies = []
    crawl_failures = []
    
    ats_counts = {}
    city_counts = {}
    total_jobs = 0
    jobs_by_city = {}
    jobs_by_ats = {}
    state_counts = {}
    
    execution_report_path = os.path.join(output_dir, 'execution_report.jsonl')
    
    if not os.path.exists(execution_report_path):
        print("execution_report.jsonl not found!")
        return
        
    with open(execution_report_path, 'r', encoding='utf-8') as f:
        for line in f:
            target = json.loads(line)
            domain = target.get('domain')
            master_data = master_inventory.get(domain, {})
            
            # Combine static data with dynamic result
            company_record = {
                "Company Name": master_data.get('company_name', target.get('company_name')),
                "Country": master_data.get('country', 'India'),
                "State": master_data.get('state', 'Unknown'),
                "City": master_data.get('city', 'Unknown'),
                "Industry": master_data.get('industry', 'Unknown'),
                "Company Type": master_data.get('company_type', 'Unknown'),
                "Company Website": f"https://{domain}",
                "Career Page URL": target.get('career_url', ''),
                "ATS Provider": target.get('ats_type') or 'UNKNOWN',
                "ATS Confidence Score": target.get('detection_confidence', 0.0),
                "Hiring Status": "HIRING" if target.get('jobs_discovered', 0) > 0 else "NO_JOBS",
                "Company Size": "Unknown",  # We don't have this yet, but needed per schema
                "Source": "CareerMaps Pipeline",
                "Last Verified Timestamp": datetime.utcnow().isoformat() + "Z"
            }
            
            status = target.get('status')
            
            if status in ("SUCCESS", "COMPLETED_EMPTY"):
                companies_seed.append(company_record)
                
                # Analytics tracking
                ats = company_record["ATS Provider"]
                city = company_record["City"]
                state = company_record["State"]
                jobs = target.get('jobs_discovered', 0)
                
                ats_counts[ats] = ats_counts.get(ats, 0) + 1
                city_counts[city] = city_counts.get(city, 0) + 1
                state_counts[state] = state_counts.get(state, 0) + 1
                total_jobs += jobs
                
                jobs_by_city[city] = jobs_by_city.get(city, 0) + jobs
                jobs_by_ats[ats] = jobs_by_ats.get(ats, 0) + jobs
                
            elif status == "FAILED" and not target.get('ats_type'):
                unsupported_companies.append(company_record)
            else:
                company_record["Failure Reason"] = " | ".join(target.get('errors', []))
                crawl_failures.append(company_record)
                
    # Write companies_seed.csv
    if companies_seed:
        with open('companies_seed.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=list(companies_seed[0].keys()))
            writer.writeheader()
            writer.writerows(companies_seed)
            
    # Write unsupported_companies.csv
    if unsupported_companies:
        with open('unsupported_companies.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=list(unsupported_companies[0].keys()))
            writer.writeheader()
            writer.writerows(unsupported_companies)
            
    # Write crawl_failures.csv
    if crawl_failures:
        with open('crawl_failures.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=list(crawl_failures[0].keys()))
            writer.writeheader()
            writer.writerows(crawl_failures)
            
    # Note: jobs_seed.jsonl is created by joining the output/jobs.jsonl with metadata
    jobs_seed = []
    jobs_file_path = os.path.join(output_dir, 'jobs.jsonl')
    if os.path.exists(jobs_file_path):
        with open(jobs_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                job = json.loads(line)
                domain = job.get('domain')
                master_data = master_inventory.get(domain, {})
                job['Country'] = master_data.get('country', 'India')
                job['State'] = master_data.get('state', 'Unknown')
                job['City'] = master_data.get('city', 'Unknown')
                job['Industry'] = master_data.get('industry', 'Unknown')
                jobs_seed.append(job)
                
        with open('jobs_seed.jsonl', 'w', encoding='utf-8') as f:
            for job in jobs_seed:
                f.write(json.dumps(job) + "\n")
                
    # Generate Analytics Markdown Reports
    
    with open('production_summary.md', 'w', encoding='utf-8') as f:
        f.write("# Production Summary\n\n")
        f.write(f"- **Total companies discovered:** {len(master_inventory)}\n")
        f.write(f"- **Successfully validated companies:** {len(companies_seed)}\n")
        f.write(f"- **Reachable career pages:** {len(companies_seed) + len(unsupported_companies)}\n")
        f.write(f"- **Unsupported ATS count:** {len(unsupported_companies)}\n")
        f.write(f"- **Crawl failures:** {len(crawl_failures)}\n")
        f.write(f"- **Total jobs extracted:** {total_jobs}\n")
        f.write("\n## ATS Distribution\n")
        for ats, count in sorted(ats_counts.items(), key=lambda x: -x[1]):
            f.write(f"- {ats}: {count}\n")
        f.write("\n## Companies per City\n")
        for city, count in sorted(city_counts.items(), key=lambda x: -x[1]):
            f.write(f"- {city}: {count}\n")
        f.write("\n## Companies per State\n")
        for state, count in sorted(state_counts.items(), key=lambda x: -x[1]):
            f.write(f"- {state}: {count}\n")
            
    with open('ats_distribution.md', 'w', encoding='utf-8') as f:
        f.write("# ATS Distribution Report\n\n")
        f.write("| ATS Provider | Companies | Jobs Extracted |\n")
        f.write("|--------------|-----------|----------------|\n")
        for ats in sorted(ats_counts.keys()):
            f.write(f"| {ats} | {ats_counts.get(ats, 0)} | {jobs_by_ats.get(ats, 0)} |\n")
            
    with open('city_statistics.md', 'w', encoding='utf-8') as f:
        f.write("# City Statistics Report\n\n")
        f.write("| City | Companies | Jobs Extracted |\n")
        f.write("|------|-----------|----------------|\n")
        for city in sorted(city_counts.keys()):
            f.write(f"| {city} | {city_counts.get(city, 0)} | {jobs_by_city.get(city, 0)} |\n")
            
    with open('company_inventory_report.md', 'w', encoding='utf-8') as f:
        f.write("# Company Inventory Report\n\n")
        f.write("| Company | City | Industry | ATS | Jobs |\n")
        f.write("|---------|------|----------|-----|------|\n")
        for c in companies_seed:
            f.write(f"| {c['Company Name']} | {c['City']} | {c['Industry']} | {c['ATS Provider']} | {c['Hiring Status']} |\n")

if __name__ == '__main__':
    main()
