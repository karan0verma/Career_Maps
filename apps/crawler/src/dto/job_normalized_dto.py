import datetime
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class JobNormalizedDTO:
    companyId: str
    companyName: str
    externalJobId: str
    title: str
    description: Optional[str]
    location: Optional[str]
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]
    employmentType: Optional[str]
    experience: Optional[str]
    applyUrl: str
    sourceATS: str
    
    # Newly added fields (Hardening Phase)
    department: Optional[str] = None
    team: Optional[str] = None
    workplaceType: Optional[str] = None
    publishedAt: Optional[str] = None
    
    discoveredAt: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat())
