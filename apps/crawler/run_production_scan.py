import os
import sys
import subprocess
import json
import csv
import time
import shutil
import concurrent.futures

def run_cli_for_target(domain):
    # Run the CLI as a subprocess to completely isolate Playwright and memory
    cmd = [sys.executable, "-m", "src.discovery.cli", "company", domain]
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60)
        return True
    except subprocess.TimeoutExpired:
        return False
    except Exception:
        return False

def fast_scan():
    with open("companies_5000.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        domains = [row.get("domain", "").strip() for row in reader if row.get("domain", "").strip()]
        
    print(f"Loaded {len(domains)} targets.")
    
    # Restored to a safer concurrency limit (10) for Playwright headless chromium memory overhead.
    print("Executing with 10 isolated worker processes...")
    with concurrent.futures.ProcessPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(run_cli_for_target, d) for d in domains]
        for idx, f in enumerate(concurrent.futures.as_completed(futures)):
            if idx > 0 and idx % 20 == 0:
                print(f"Processed {idx}/{len(domains)}...")

def generate_reports():
    print("Generating Analytics and CSV Reports...")
    ats_inventory = []
    unsupported = []
    failures = []
    
    total_companies = 0
    ats_detected_count = 0
    crawl_success_count = 0
    total_jobs = 0
    ats_market = {}
    unsupported_market = {}
    
    with open("output/execution_report.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip(): continue
            record = json.loads(line)
            total_companies += 1
            
            if record.get("ats_type"):
                ats_detected_count += 1
                ats = record["ats_type"]
                ats_market[ats] = ats_market.get(ats, 0) + 1
            else:
                reason = "No matching ATS signature found." if "No matching ATS signature found." in record.get("errors", []) else "Other"
                unsupported_market[reason] = unsupported_market.get(reason, 0) + 1
                
            status = record.get("status")
            if status == "SUCCESS":
                crawl_success_count += 1
                
            jobs = record.get("jobs_discovered", 0)
            total_jobs += jobs
            
            row = [
                record.get("company_name", ""),
                record.get("domain", ""),
                record.get("career_url", ""),
                record.get("ats_type", ""),
                record.get("detection_confidence", ""),
                record.get("status", ""),
                jobs,
                " | ".join(record.get("errors", []))
            ]
            
            if status == "SUCCESS":
                ats_inventory.append(row)
            elif status == "UNSUPPORTED_ATS" or not record.get("ats_type"):
                unsupported.append(row)
            elif status == "CRAWL_FAILED" or status == "FAILED":
                failures.append(row)

    headers = ["Company Name", "Domain", "Career URL", "ATS Vendor", "Detection Confidence", "Crawl Status", "Jobs Found", "Failure Reason"]
    
    with open("output/ats_inventory.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(headers)
        w.writerows(ats_inventory)
        
    with open("output/unsupported_companies.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(headers)
        w.writerows(unsupported)
        
    with open("output/crawl_failures.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(headers)
        w.writerows(failures)
        
    with open("output/companies.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(headers)
        w.writerows(ats_inventory + unsupported + failures)

    print("\n=========================================")
    print("FINAL ANALYTICS SUMMARY")
    print("=========================================")
    print(f"Total companies scanned: {total_companies}")
    print(f"Total successful career page discoveries: {total_companies - len(failures)}") 
    print(f"Total ATS detections: {ats_detected_count}")
    print(f"Total successful crawls: {crawl_success_count}")
    print(f"Total jobs discovered: {total_jobs}")
    print(f"Total failures: {len(failures)}")
    print(f"Total unsupported ATS: {len(unsupported)}")
    
    print("\nTOP 20 ATS VENDORS (By Company Count):")
    for ats, count in sorted(ats_market.items(), key=lambda x: x[1], reverse=True)[:20]:
        print(f" - {ats}: {count}")
        
    print("\nTOP 20 UNSUPPORTED REASONS:")
    for reason, count in sorted(unsupported_market.items(), key=lambda x: x[1], reverse=True)[:20]:
        print(f" - {reason}: {count}")

    print("\nTOP 20 COMPANIES WITH HIGHEST JOBS:")
    top_companies = sorted(ats_inventory, key=lambda x: x[6], reverse=True)[:20]
    for c in top_companies:
        print(f" - {c[0]} ({c[1]}): {c[6]} jobs")

if __name__ == "__main__":
    if os.path.exists("output"):
        shutil.rmtree("output", ignore_errors=True)
    os.makedirs("output", exist_ok=True)
    fast_scan()
    generate_reports()
