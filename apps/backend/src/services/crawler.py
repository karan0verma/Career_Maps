import os
import subprocess
import json
from datetime import datetime, timezone
from uuid import UUID, uuid4
from sqlalchemy.orm import Session
from src.models.company import Company
from src.models.job import Job
from src.models.scheduler import CrawlHistory

class CrawlerService:
    @staticmethod
    def _run_crawler_subprocess(domain: str, source_url: str = None, strategy: str = None, ats_type: str = None, extraction_config: dict = None) -> dict:
        # Determine paths
        backend_src = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        backend_dir = os.path.dirname(backend_src)
        crawler_dir = os.path.abspath(os.path.join(backend_dir, "..", "crawler"))
        
        import sys
        python_exe = sys.executable
            
        script = os.path.join(crawler_dir, "run_single.py")
        
        args = [python_exe, script, domain]
        if source_url:
            args.extend(["--url", source_url])
        if strategy:
            args.extend(["--strategy", strategy])
        if ats_type:
            args.extend(["--ats", ats_type])
        if extraction_config:
            args.extend(["--config", json.dumps(extraction_config)])
            
        result = subprocess.run(
            args, 
            capture_output=True, 
            text=True, 
            cwd=crawler_dir,
            timeout=300 # 5 minutes timeout to prevent indefinite hangs
        )
        
        if result.returncode != 0:
            raise Exception(f"Crawler subprocess failed: {result.stderr}\n{result.stdout}")
            
        try:
            # The stdout might have some logging if we aren't careful, but run_single.py only prints json at the end
            # Find the last line that is valid JSON
            lines = result.stdout.strip().split('\n')
            for line in reversed(lines):
                if line.startswith('{'):
                    return json.loads(line)
            raise ValueError("No JSON payload found in stdout")
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse crawler output: {e}\nOutput: {result.stdout}")

    @staticmethod
    def run_crawl(db: Session, company_id: UUID, trigger_type: str = "MANUAL", force_run: bool = False) -> CrawlHistory:
        from src.models.company import CompanySource, CompanyATSHistory
        
        company = db.query(Company).filter(Company.company_id == company_id).first()
        if not company:
            raise ValueError(f"Company {company_id} not found")
            
        domain = company.website.replace("https://", "").replace("http://", "").replace("www.", "").strip("/")
        
        # Phase E: Look up active CompanySource
        cached_source = db.query(CompanySource).filter(
            CompanySource.company_id == company.company_id,
            CompanySource.health_status == 'ACTIVE'
        ).order_by(CompanySource.last_verified_at.desc()).first()
        
        source_url = None
        strategy = None
        ats_type = None
        extraction_config = None
        
        if cached_source:
            source_url = cached_source.source_url
            strategy = cached_source.extraction_strategy
            extraction_config = cached_source.extraction_config
            
            # Find the known ATS type if it's KNOWN_ATS
            if strategy == "KNOWN_ATS":
                ats_history = db.query(CompanyATSHistory).filter(
                    CompanyATSHistory.company_id == company.company_id,
                    CompanyATSHistory.is_current == True
                ).first()
                if ats_history:
                    ats_type = ats_history.ats_provider
        
        crawl_history = CrawlHistory(
            company_id=company.company_id,
            trigger_type=trigger_type,
            status="IN_PROGRESS",
            started_at=datetime.utcnow()
        )
        db.add(crawl_history)
        db.commit()
        
        try:
            output = CrawlerService._run_crawler_subprocess(domain, source_url, strategy, ats_type, extraction_config)
            
            target_data = output.get("target", {})
            jobs_data = output.get("jobs", [])
            
            # Update company ATS type if detected
            detected_ats = target_data.get("ats_type")
            if detected_ats and (company.ats_platform is None or company.ats_platform == "Unknown"):
                company.ats_platform = detected_ats
                
                # Update CompanySource strategy if we detected it
                if cached_source and not cached_source.extraction_strategy:
                    cached_source.extraction_strategy = "KNOWN_ATS"
                    
                # Add ATS History
                db.query(CompanyATSHistory).filter(CompanyATSHistory.company_id == company.company_id).update({"is_current": False})
                db.add(CompanyATSHistory(company_id=company.company_id, ats_provider=detected_ats, is_current=True))
            
            # Deduplicate jobs_data before DB operations
            unique_jobs = []
            seen_identifiers = set()
            seen_apply_urls = set()
            
            for job_dto in jobs_data:
                external_id = job_dto.get("externalJobId") or job_dto.get("id")
                apply_url = job_dto.get("applyUrl")
                
                if not external_id and not apply_url:
                    continue
                    
                identifier = external_id if external_id else apply_url
                
                # Check if we already saw this identifier or this exact apply_url in this payload
                if identifier in seen_identifiers:
                    continue
                if apply_url and apply_url in seen_apply_urls:
                    continue
                    
                seen_identifiers.add(identifier)
                if apply_url:
                    seen_apply_urls.add(apply_url)
                unique_jobs.append(job_dto)
            
            # Upsert jobs
            jobs_added = 0
            jobs_updated = 0
            
            # Keep track of external IDs or generated slugs to find missing ones
            seen_external_ids = set()
            
            for job_dto in unique_jobs:
                external_id = job_dto.get("externalJobId") or job_dto.get("id")
                if not external_id:
                    # fallback to URL if no external ID provided by ATS
                    external_id = job_dto.get("applyUrl")
                    
                if not external_id:
                    continue
                    
                seen_external_ids.add(external_id)
                
                existing_job = db.query(Job).filter(
                    Job.company_id == company.company_id,
                    Job.external_job_id == external_id
                ).first()
                
                if existing_job:
                    existing_job.title = job_dto.get("title", existing_job.title)
                    existing_job.department = job_dto.get("department", existing_job.department)
                    existing_job.location = job_dto.get("location", existing_job.location)
                    existing_job.city = job_dto.get("city", existing_job.city)
                    existing_job.state = job_dto.get("state", existing_job.state)
                    existing_job.country = job_dto.get("country", existing_job.country)
                    existing_job.description = job_dto.get("description", existing_job.description)
                    existing_job.apply_url = job_dto.get("applyUrl", existing_job.apply_url)
                    existing_job.raw_data = job_dto
                    existing_job.last_seen_at = datetime.utcnow()
                    existing_job.is_active = True
                    jobs_updated += 1
                else:
                    new_job = Job(
                        company_id=company.company_id,
                        external_job_id=external_id,
                        title=job_dto.get("title"),
                        department=job_dto.get("department"),
                        location=job_dto.get("location"),
                        city=job_dto.get("city"),
                        state=job_dto.get("state"),
                        country=job_dto.get("country"),
                        work_mode=job_dto.get("workplaceType"),
                        employment_type=job_dto.get("employmentType"),
                        description=job_dto.get("description"),
                        apply_url=job_dto.get("applyUrl"),
                        source_url=job_dto.get("applyUrl"),
                        raw_data=job_dto,
                        is_active=True,
                        first_seen_at=datetime.utcnow(),
                        last_seen_at=datetime.utcnow()
                    )
                    db.add(new_job)
                    jobs_added += 1
                    
            # Mark missing jobs as inactive
            missing_jobs = db.query(Job).filter(
                Job.company_id == company.company_id,
                Job.is_active == True,
                Job.external_job_id.not_in(seen_external_ids)
            ).all()
            
            jobs_deactivated = 0
            for mj in missing_jobs:
                mj.is_active = False
                jobs_deactivated += 1
                
            db.commit()
            
            crawl_history.status = target_data.get("status", "SUCCESS")
            crawl_history.jobs_found = len(jobs_data)
            crawl_history.jobs_added = jobs_added
            crawl_history.jobs_deactivated = jobs_deactivated
            crawl_history.completed_at = datetime.utcnow()
            crawl_history.errors = {"crawler_errors": target_data.get("errors", [])}
            
            # Phase E: Update or create CompanySource
            ext_strategy = target_data.get("extraction_strategy")
            c_url = target_data.get("career_url")
            
            if ext_strategy and c_url:
                # Use discovered API url if GENERIC_API
                if ext_strategy == "GENERIC_API" and target_data.get("metadata", {}).get("discovered_api_url"):
                    c_url = target_data.get("metadata").get("discovered_api_url")
                    
                existing_source = db.query(CompanySource).filter(
                    CompanySource.company_id == company.company_id,
                    CompanySource.source_url == c_url,
                    CompanySource.extraction_strategy == ext_strategy
                ).first()
                
                health = "ACTIVE" if crawl_history.jobs_found > 0 else "DEGRADED"
                
                if existing_source:
                    existing_source.health_status = health
                    existing_source.last_verified_at = datetime.utcnow()
                    if target_data.get("metadata", {}).get("extraction_config"):
                        existing_source.extraction_config = target_data["metadata"]["extraction_config"]
                else:
                    new_source = CompanySource(
                        company_id=company.company_id,
                        source_url=c_url,
                        extraction_strategy=ext_strategy,
                        health_status=health,
                        extraction_config=target_data.get("metadata", {}).get("extraction_config"),
                        last_verified_at=datetime.utcnow()
                    )
                    db.add(new_source)
                    
                # Ensure CompanyATSHistory is updated so cache hits can find the ats_type
                if ext_strategy == "KNOWN_ATS" and target_data.get("ats_type") and health == "ACTIVE":
                    # Mark existing as not current
                    db.query(CompanyATSHistory).filter(
                        CompanyATSHistory.company_id == company.company_id
                    ).update({"is_current": False})
                    
                    new_ats = CompanyATSHistory(
                        company_id=company.company_id,
                        ats_provider=target_data.get("ats_type"),
                        confidence_score=1.0,
                        is_current=True,
                        last_verified_at=datetime.utcnow()
                    )
                    db.add(new_ats)
            
            db.commit()
            return crawl_history
            
        except Exception as e:
            db.rollback()
            crawl_history.status = "FAILED"
            crawl_history.errors = {"exception": str(e)}
            crawl_history.completed_at = datetime.utcnow()
            
            # Transition cached source to broken if it permanently failed
            if source_url and strategy:
                db_source = db.query(CompanySource).filter(
                    CompanySource.company_id == company.company_id,
                    CompanySource.source_url == source_url,
                    CompanySource.extraction_strategy == strategy
                ).first()
                if db_source:
                    # Very simple logic: if we tried to use it and it crashed, mark DEGRADED or BROKEN
                    # For safety, let's mark it BROKEN so the next crawl triggers a fresh discovery
                    db_source.health_status = "BROKEN"
                    db_source.last_verified_at = datetime.utcnow()
                    
            db.commit()
            return crawl_history
