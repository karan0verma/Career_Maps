import os
import sys
import time
import datetime
from typing import List, Dict, Any

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend')))

from dotenv import load_dotenv
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend', '.env')))

from src.db.session import SessionLocal
from src.models.company import Company
from src.models.job import Job

class JobSyncScheduler:
    """
    Automated Background Delta Sync Scheduler for all integrated career portals.
    Can be run continuously on a configurable interval (e.g., every 12 hours) 
    or triggered on-demand.
    """

    DEFAULT_INTERVAL_HOURS = 12

    @staticmethod
    def sync_all_companies():
        print("=" * 75)
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] STARTING AUTOMATED JOB SYNC CYCLE")
        print("=" * 75)
        
        # 1. TCS iBegin Sync
        try:
            print("\n[1/3] Syncing Tata Consultancy Services (TCS)...")
            from src.scripts.import_all_tcs_jobs import import_tcs_jobs
            import_tcs_jobs()
        except Exception as e:
            print(f"Error syncing TCS: {e}")

        # 2. Tech Mahindra Sync
        try:
            print("\n[2/3] Syncing Tech Mahindra...")
            from src.scripts.import_all_tech_mahindra_jobs import import_all_jobs as import_techm
            import_techm()
        except Exception as e:
            print(f"Error syncing Tech Mahindra: {e}")

        # 3. Coforge Sync
        try:
            print("\n[3/3] Syncing Coforge...")
            from src.scripts.import_all_coforge_jobs import import_all_coforge_jobs
            import_all_coforge_jobs()
        except Exception as e:
            print(f"Error syncing Coforge: {e}")

        print("\n" + "=" * 75)
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] AUTOMATED SYNC CYCLE COMPLETED!")
        print("=" * 75)

    @classmethod
    def start_daemon(cls, interval_hours: int = 12):
        print(f"Starting Career Maps Job Sync Daemon (Interval: Every {interval_hours} Hours)...")
        while True:
            cls.sync_all_companies()
            sleep_seconds = interval_hours * 3600
            print(f"\nNext automated sync scheduled in {interval_hours} hours. Sleeping...\n")
            time.sleep(sleep_seconds)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Job Sync Scheduler")
    parser.add_argument("--daemon", action="store_true", help="Run continuously as background daemon")
    parser.add_argument("--interval", type=int, default=12, help="Sync interval in hours (default: 12)")
    args = parser.parse_args()

    if args.daemon:
        JobSyncScheduler.start_daemon(args.interval)
    else:
        JobSyncScheduler.sync_all_companies()
