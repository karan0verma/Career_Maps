import re
from typing import Dict, List, Any, Optional

class JobNormalizer:
    """
    Standard Locked Normalization Engine for Enterprise Career Portals.
    Provides uniform mapping for domains, experience levels, skills, and deep apply URLs.
    """
    
    DOMAIN_KEYWORDS = {
        "Technology": ["technology", "software", "developer", "engineer", "architect", "lead", "frontend", "backend", "fullstack", "java", "python", "react", "angular", "node"],
        "IT Infrastructure & Cloud": ["infrastructure", "itis", "cloud", "devops", "aws", "azure", "gcp", "network", "system admin", "database admin", "dba", "sre"],
        "Business Process Services (BPS)": ["business process", "bps", "operations", "process associate", "customer support", "voice", "non-voice", "bpo", "back office"],
        "Consulting & Enterprise Solutions": ["consultant", "consulting", "sap", "oracle", "infor", "salesforce", "erp", "crm", "advisory", "functional"],
        "Quality Assurance & Testing": ["quality assurance", "qa", "testing", "tester", "sdet", "automation", "tosca", "selenium", "cypress", "playwright"],
        "Finance & Accounting": ["finance", "accounting", "accounts", "receivables", "payables", "ledger", "taxation", "audit", "payroll"],
        "Human Resources": ["human resources", "hr", "talent acquisition", "recruiter", "people operations", "staffing"]
    }

    @staticmethod
    def normalize_experience(raw_exp: Optional[str]) -> str:
        if not raw_exp:
            return "2-8 Years"
        raw = str(raw_exp).strip()
        if not raw.lower().endswith("years") and not raw.lower().endswith("yrs"):
            raw = f"{raw} Years"
        return raw

    @staticmethod
    def infer_domains(title: str, requirements: str, skills: List[str]) -> List[str]:
        combined_text = f"{title} {requirements} {' '.join(skills)}".lower()
        matched_domains = []
        
        for domain, keywords in JobNormalizer.DOMAIN_KEYWORDS.items():
            if any(kw in combined_text for kw in keywords):
                matched_domains.append(domain)
                
        if not matched_domains:
            matched_domains.append("Technology")
        return matched_domains

    @staticmethod
    def extract_skills(raw_skills: Optional[str], default_domain: str = "Technology") -> List[str]:
        if not raw_skills:
            return [default_domain]
        skills = [s.strip() for s in re.split(r'[,|/•\n]', str(raw_skills)) if s.strip() and len(s.strip()) > 1]
        return skills if skills else [default_domain]
