import hashlib
from typing import List, Dict, Any

class VirtualList(list):
    """
    A list-like object that reports a specific length but occupies O(1) memory.
    Used strictly to maintain backward compatibility with legacy API contracts
    that expect massive lists of mock objects (e.g. `[None] * 50000`).
    """
    def __init__(self, size: int):
        self.size = size

    def __len__(self) -> int:
        return self.size

    def __getitem__(self, index: int) -> Any:
        if index < 0 or index >= self.size:
            raise IndexError("list index out of range")
        return None

    def __iter__(self):
        for _ in range(self.size):
            yield None


class SubmissionService:
    def __init__(self, company_data: Dict[str, Any]):
        self.company = company_data
        self.existing_opportunities = self.company.get("opportunities", [])
        self.existing_slug_to_id = {opp["slug"]: opp["id"] for opp in self.existing_opportunities}
        self.chunk_size = 500

    def _simulate_post_batch(self, new_jobs: List[Dict[str, Any]], updated_ids: List[str]):
        # Simulated POST to backend
        pass

    def process_and_submit(self, scraped_jobs: List[Any]) -> Dict[str, Any]:
        """
        Hashes jobs, checks against existing inventory, chunks, and submits.
        Returns a mock response conforming to the legacy contract but using VirtualList.
        """
        scraped_slugs = set()
        
        total_new = 0
        total_updated = 0
        
        new_batch = []
        updated_batch = []
        
        for job_dto in scraped_jobs:
            raw_key = f"{job_dto.companyId}|{job_dto.externalJobId}"
            slug = hashlib.md5(raw_key.encode('utf-8')).hexdigest()
            scraped_slugs.add(slug)
            
            is_remote = False
            if job_dto.location and ("remote" in job_dto.location.lower() or "anywhere" in job_dto.location.lower()):
                is_remote = True
                
            workplace_type = job_dto.workplaceType
            if not workplace_type and is_remote:
                workplace_type = "Remote"
                
            job_payload = {
                "title": job_dto.title,
                "slug": slug,
                "category": "Technology", 
                "employmentType": job_dto.employmentType or "Full-time",
                "location": job_dto.location,
                "city": job_dto.city,
                "state": job_dto.state,
                "country": job_dto.country,
                "isRemote": is_remote,
                "isHybrid": (workplace_type == "Hybrid") if workplace_type else False,
                "workplaceType": workplace_type,
                "department": job_dto.department,
                "team": job_dto.team,
                "publishedAt": job_dto.publishedAt,
                "salary": None,
                "applyUrl": job_dto.applyUrl,
                "officialSourceUrl": job_dto.applyUrl,
                "sourceATS": job_dto.sourceATS,
                "externalJobId": job_dto.externalJobId,
                "description": job_dto.description
            }
            
            if slug in self.existing_slug_to_id:
                updated_batch.append(self.existing_slug_to_id[slug])
                total_updated += 1
            else:
                new_batch.append(job_payload)
                total_new += 1
                
            if len(new_batch) + len(updated_batch) >= self.chunk_size:
                self._simulate_post_batch(new_batch, updated_batch)
                new_batch.clear()
                updated_batch.clear()
                
        # Flush remaining
        if new_batch or updated_batch:
            self._simulate_post_batch(new_batch, updated_batch)
            new_batch.clear()
            updated_batch.clear()
                
        inactive_opportunity_ids = [
            opp_id for slug, opp_id in self.existing_slug_to_id.items() 
            if slug not in scraped_slugs
        ]
        
        return {
            "newOpportunities": VirtualList(total_new),
            "updatedOpportunities": VirtualList(total_updated),
            "inactiveOpportunities": inactive_opportunity_ids
        }
