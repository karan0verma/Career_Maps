import time
from dotenv import load_dotenv
load_dotenv()

from src.utils.api_client import APIClient
from src.ats.registry import AtsRegistry

def main():
    print("Starting Career Maps Production Crawler Orchestrator")
    
    # Auto-discover and register all ATS crawler plugins
    AtsRegistry.load_adapters()
    
    api = APIClient()
    
    # 1. Fetch queue
    print("Fetching queue from API...")
    queue = api.get_queue(limit=50)
    
    if not queue:
        print("Queue is empty. Exiting.")
        return
        
    print(f"Found {len(queue)} companies in queue.")
    
    # 2. Process companies
    stats = {
        "total_processed": 0,
        "success": 0,
        "failed": 0
    }
    
    for company in queue:
        company_name = company.get("companyName")
        
        print(f"\n--- Processing {company_name} ---")
        
        crawler_class = AtsRegistry.get(company.get("atsType", "UNKNOWN"))
        if not crawler_class:
            print(f"No crawler implementation found for ATS type {company.get('atsType', 'UNKNOWN')}. Skipping.")
            continue
            
        crawler = crawler_class(company)
        
        try:
            # 3. Execute crawler logic (BaseCrawler handles resilient retry and playright init)
            result = crawler.execute()
            
            # 4. Submit results
            if result:
                success = api.submit_result(result)
                if success:
                    print(f"[{company_name}] Successfully submitted results to API.")
                    stats["success"] += 1
                else:
                    print(f"[{company_name}] Failed to submit results to API.")
                    stats["failed"] += 1
            else:
                print(f"[{company_name}] Execution returned no result.")
                stats["failed"] += 1
                
        except Exception as e:
            print(f"[{company_name}] Unhandled critical error: {e}")
            stats["failed"] += 1
            
        stats["total_processed"] += 1

    print("\n--- Crawler Orchestrator Summary ---")
    print(f"Total Processed: {stats['total_processed']}")
    print(f"Success        : {stats['success']}")
    print(f"Failed         : {stats['failed']}")

if __name__ == "__main__":
    main()
