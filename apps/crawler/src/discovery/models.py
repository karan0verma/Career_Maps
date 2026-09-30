from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List

@dataclass
class Target:
    company_name: str
    domain: str
    career_url: Optional[str] = None
    ats_type: Optional[str] = None
    extraction_strategy: Optional[str] = None
    detection_confidence: float = 0.0
    status: str = "PENDING"
    jobs_discovered: int = 0
    execution_time_ms: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "company_name": self.company_name,
            "domain": self.domain,
            "career_url": self.career_url,
            "ats_type": self.ats_type,
            "extraction_strategy": self.extraction_strategy,
            "detection_confidence": self.detection_confidence,
            "status": self.status,
            "jobs_discovered": self.jobs_discovered,
            "execution_time_ms": self.execution_time_ms,
            "metadata": self.metadata,
            "errors": self.errors
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Target':
        return cls(
            company_name=data["company_name"],
            domain=data["domain"],
            career_url=data.get("career_url"),
            ats_type=data.get("ats_type"),
            extraction_strategy=data.get("extraction_strategy"),
            detection_confidence=data.get("detection_confidence", 0.0),
            status=data.get("status", "PENDING"),
            jobs_discovered=data.get("jobs_discovered", 0),
            execution_time_ms=data.get("execution_time_ms", 0),
            metadata=data.get("metadata", {}),
            errors=data.get("errors", [])
        )
