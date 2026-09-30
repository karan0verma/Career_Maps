import os
import sys
from dotenv import load_dotenv

# Add parent directory to path so we can import src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
import meilisearch
from src.db.session import SessionLocal
from src.models.job import Job

# Load .env manually for scripts if needed
load_dotenv()

def sync_meilisearch():
    print("Connecting to Meilisearch...")
    # Default local Meilisearch without master key
    client = meilisearch.Client('http://127.0.0.1:7700')
    
    print("Creating/updating index 'jobs'...")
    index = client.index('jobs')
    index.update(primary_key='id')
    
    print("Updating index settings...")
    index.update_settings({
        'searchableAttributes': [
            'title',
            'company_name',
            'location',
            'description'
        ],
        'filterableAttributes': [
            'location',
            'work_mode',
            'company_id',
            'is_active',
            'is_deleted'
        ],
        'sortableAttributes': [
            'first_seen_at'
        ]
    })
    
    print("Fetching jobs from database...")
    db: Session = SessionLocal()
    try:
        jobs = db.query(Job).filter(Job.is_active == True, Job.is_deleted == False).all()
        
        print(f"Found {len(jobs)} active jobs. Preparing documents...")
        documents = []
        for job in jobs:
            documents.append({
                'id': str(job.job_id),
                'job_id': str(job.job_id),
                'title': job.title,
                'company_name': job.company.display_name if job.company else '',
                'company_id': str(job.company_id) if job.company_id else None,
                'location': job.location,
                'work_mode': job.work_mode,
                'description': job.description,
                'is_active': job.is_active,
                'is_deleted': job.is_deleted,
                'first_seen_at': job.first_seen_at.timestamp() if job.first_seen_at else 0
            })
            
        print("Uploading to Meilisearch in batches...")
        # Meilisearch can handle large batches, let's use the SDK's add_documents
        task = index.add_documents(documents)
        print(f"Task enqueued: {task.task_uid}")
        
        print(f"Uploaded {len(jobs)} jobs in batches.")
        
        # --- COMPANIES SYNC ---
        print("\nCreating/updating index 'companies'...")
        comp_index = client.index('companies')
        comp_index.update(primary_key='id')
        
        comp_index.update_settings({
            'searchableAttributes': [
                'display_name',
                'industry'
            ],
            'filterableAttributes': [
                'is_active',
                'is_deleted'
            ]
        })
        
        from src.models.company import Company
        print("Fetching companies from database...")
        companies = db.query(Company).filter(Company.is_active == True, Company.is_deleted == False).all()
        
        print(f"Found {len(companies)} active companies. Preparing documents...")
        comp_documents = []
        for comp in companies:
            comp_documents.append({
                'id': str(comp.company_id),
                'display_name': comp.display_name,
                'industry': comp.industry,
                'is_active': comp.is_active,
                'is_deleted': comp.is_deleted
            })
            
        print("Uploading companies to Meilisearch in batches...")
        batch_size = 500
        for i in range(0, len(comp_documents), batch_size):
            batch = comp_documents[i:i + batch_size]
            comp_index.add_documents(batch)
            
        print("Waiting for tasks to complete (this happens async)...")
        print("Sync complete!")
        
    except Exception as e:
        print(f"Error during sync: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    sync_meilisearch()
