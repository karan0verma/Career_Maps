import os
import sys
import uuid
import datetime
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from uuid import UUID

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend')))

from dotenv import load_dotenv
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend', '.env')))

from src.db.session import SessionLocal
from src.models.company import Company
from src.models.job import Job
from playwright.sync_api import sync_playwright, BrowserContext, Page
from .normalizer import JobNormalizer

class BasePortalPipeline(ABC):
    """
    Standard Locked Base Pipeline for Reverse-Engineered Enterprise Career Portals.
    Provides session initialization, WAF bypassing via real Chrome context, 
    batch ingestion, and automatic PostgreSQL synchronization.
    """

    def __init__(self, company_id: str, company_name: str, portal_url: str):
        self.company_id = UUID(company_id)
        self.company_name = company_name
        self.portal_url = portal_url
        self.normalizer = JobNormalizer()

    @abstractmethod
    def extract_jobs_from_session(self, page: Page, context: BrowserContext) -> List[Dict[str, Any]]:
        """
        Subclasses implement portal-specific API/network extraction within the active Chrome context.
        """
        pass

    def run(self) -> int:
        print("=" * 75)
        print(f"EXECUTING PORTAL PIPELINE: {self.company_name}")
        print(f"Portal URL: {self.portal_url}")
        print("=" * 75)

        raw_jobs = []

        with sync_playwright() as p:
            browser = p.chromium.launch(
                channel='chrome',
                headless=True,
                args=['--no-sandbox', '--disable-blink-features=AutomationControlled']
            )
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
                viewport={'width': 1440, 'height': 900}
            )
            page = context.new_page()
            
            print("1. Initializing real browser session context...", flush=True)
            raw_jobs = self.extract_jobs_from_session(page, context)
            browser.close()

        print(f"\n2. Extracted {len(raw_jobs)} raw jobs from portal.", flush=True)
        return self._ingest_to_db(raw_jobs)

    def _ingest_to_db(self, raw_jobs: List[Dict[str, Any]]) -> int:
        db = SessionLocal()
        company = db.query(Company).filter(Company.company_id == self.company_id).first()
        if not company:
            company = db.query(Company).filter(Company.display_name.ilike(f"%{self.company_name}%")).first()

        if not company:
            print(f"Error: Company {self.company_name} not found in database!")
            db.close()
            return 0

        # Clean existing jobs
        db.query(Job).filter(Job.company_id == company.company_id).delete()
        db.commit()

        seen_urls = set()
        inserted = 0

        for item in raw_jobs:
            apply_url = item.get('apply_url')
            if not apply_url or apply_url in seen_urls:
                continue
            seen_urls.add(apply_url)

            title = (item.get('title') or "Software Engineer").strip()
            city = (item.get('city') or item.get('location') or "Pan India").strip()
            country = item.get('country') or "India"
            location = f"{city}, {country}" if country and country.lower() not in city.lower() else city

            exp_level = self.normalizer.normalize_experience(item.get('experience'))
            skills = self.normalizer.extract_skills(item.get('skills'))
            domain = item.get('domain') or "Technology"

            description = item.get('description') or (
                f"{self.company_name} is hiring for the position of {title}.\n\n"
                f"Key Details:\n"
                f"• Role: {title}\n"
                f"• Domain / Function: {domain}\n"
                f"• Location: {location}\n"
                f"• Experience: {exp_level}\n"
                f"• Required Skills: {', '.join(skills)}\n\n"
                f"Apply directly through the official career portal link below."
            )

            job = Job(
                job_id=uuid.uuid4(),
                company_id=company.company_id,
                title=title,
                location=location,
                city=city,
                country=country,
                work_mode=item.get('work_mode') or "On-site / Hybrid",
                employment_type=item.get('employment_type') or "Full-time",
                experience_level=exp_level,
                required_skills=skills,
                description=description,
                requirements=f"Experience: {exp_level} | Domain: {domain} | Skills: {', '.join(skills)}",
                apply_url=apply_url,
                is_active=True,
                is_deleted=False,
                first_seen_at=datetime.datetime.now(datetime.timezone.utc),
                last_seen_at=datetime.datetime.now(datetime.timezone.utc)
            )
            db.add(job)
            inserted += 1

        db.commit()
        db.close()
        print(f"3. Ingested {inserted} verified jobs into PostgreSQL for {self.company_name}!")
        return inserted
