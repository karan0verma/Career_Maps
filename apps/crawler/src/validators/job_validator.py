import logging
import re
import hashlib
from typing import List, Tuple, Dict, Any
from src.discovery.models import Target
from src.dto.job_normalized_dto import JobNormalizedDTO

logger = logging.getLogger(__name__)

class JobValidator:
    def __init__(self):
        self.non_job_keywords = {
            'about us', 'contact us', 'privacy policy', 'terms of service', 'terms & conditions',
            'terms and conditions', 'blog', 'news', 'investors', 'login', 'sign up', 'home', 
            'careers', 'meet our team', 'life at', 'our culture', 'events', 'press', 'cookie policy'
        }
        
    def process(self, target: Target, jobs: List[JobNormalizedDTO]) -> Tuple[List[JobNormalizedDTO], List[Dict], int]:
        accepted = []
        rejected = []
        
        # 1. Validation & Scoring
        for job in jobs:
            score, reasons = self._calculate_score(target, job)
            
            # Determine threshold based on strategy
            threshold = self._get_threshold(target.extraction_strategy)
            
            if score >= threshold:
                # Normalization
                job = self._normalize(job)
                accepted.append(job)
            else:
                rejected.append({
                    "title": job.title,
                    "url": job.applyUrl,
                    "score": score,
                    "reasons": reasons
                })
                
        # 2. Deduplication
        deduplicated, duplicates_count = self._deduplicate(accepted)
        
        return deduplicated, rejected, duplicates_count

    def _get_threshold(self, strategy: str) -> int:
        if strategy == "KNOWN_ATS":
            return 1 # Highly trusted
        elif strategy == "STRUCTURED_JSON_LD":
            return 2 # Trusted but requires basic checks
        elif strategy == "GENERIC_API":
            return 3 # Requires moderate evidence
        elif strategy == "GENERIC_DOM":
            return 4 # Requires strong independent signals
        return 5

    def _calculate_score(self, target: Target, job: JobNormalizedDTO) -> Tuple[int, List[str]]:
        score = 0
        reasons = []
        
        title = (job.title or "").strip()
        if not title:
            return 0, ["Empty title"]
            
        title_lower = title.lower()
        if any(title_lower == kw for kw in self.non_job_keywords):
            return 0, ["Title exactly matches non-job keyword blacklist"]
            
        if any(kw in title_lower for kw in ['blog', 'privacy', 'cookie policy']):
            return 0, ["Title contains strong non-job keywords"]
            
        # Basic requirements
        if not job.applyUrl and not job.externalJobId:
            return 0, ["Missing both applyUrl and externalJobId"]
            
        score += 1
        
        # Positive signals
        if job.externalJobId:
            score += 1
            
        if job.description and len(job.description.strip()) > 50:
            score += 1
            
        if job.location and len(job.location.strip()) > 2:
            score += 1
            
        if job.employmentType:
            score += 1
            
        # URL patterns
        if job.applyUrl:
            url_lower = job.applyUrl.lower()
            if any(part in url_lower for part in ['/job/', '/jobs/', '/careers/', '/position/', '/req/', 'requisition']):
                score += 1
                
        # Title heuristics (e.g. Engineer, Developer)
        job_title_keywords = ['engineer', 'developer', 'analyst', 'manager', 'intern', 'consultant', 'designer', 'specialist', 'recruiter', 'associate', 'director', 'lead']
        if any(kw in title_lower for kw in job_title_keywords):
            score += 1
            
        # Generic DOM specific safety checks
        if target.extraction_strategy == "GENERIC_DOM":
            if "day in the life" in title_lower or "meet our" in title_lower:
                return 0, ["Matches 'Day in the life' / 'Meet our' blog heuristic"]
                
        if score < self._get_threshold(target.extraction_strategy):
            reasons.append(f"Score {score} is below threshold {self._get_threshold(target.extraction_strategy)}")
            
        return score, reasons

    def _normalize(self, job: JobNormalizedDTO) -> JobNormalizedDTO:
        # Whitespace normalization
        if job.title:
            job.title = re.sub(r'\s+', ' ', job.title).strip()
        if job.location:
            job.location = re.sub(r'\s+', ' ', job.location).strip()
        if job.externalJobId:
            job.externalJobId = job.externalJobId.strip()
        if job.applyUrl:
            job.applyUrl = job.applyUrl.strip()
        return job

    def _deduplicate(self, jobs: List[JobNormalizedDTO]) -> Tuple[List[JobNormalizedDTO], int]:
        seen_ids = set()
        seen_urls = set()
        seen_fingerprints = set()
        
        unique = []
        duplicates = 0
        
        for job in jobs:
            is_duplicate = False
            
            # 1. By external ID
            if job.externalJobId:
                if job.externalJobId in seen_ids:
                    is_duplicate = True
                else:
                    seen_ids.add(job.externalJobId)
                    
            # 2. By Apply URL
            if not is_duplicate and job.applyUrl:
                normalized_url = job.applyUrl.split('?')[0].rstrip('/')
                if normalized_url in seen_urls:
                    is_duplicate = True
                else:
                    seen_urls.add(normalized_url)
                    
            # 3. Deterministic Fingerprint
            if not is_duplicate:
                fp_str = f"{job.companyName}|{job.title.lower()}|{(job.location or '').lower()}"
                fingerprint = hashlib.md5(fp_str.encode('utf-8')).hexdigest()
                if fingerprint in seen_fingerprints:
                    is_duplicate = True
                else:
                    seen_fingerprints.add(fingerprint)
                    
            if not is_duplicate:
                unique.append(job)
            else:
                duplicates += 1
                
        return unique, duplicates
