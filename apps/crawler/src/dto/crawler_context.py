from dataclasses import dataclass, field
from typing import Optional, Any, Dict

@dataclass
class CrawlerContext:
    """
    Context passed to all adapter lifecycle methods (login, crawl).
    Contains execution environment state based on the crawler type.
    """
    page: Optional[Any] = None       # Playwright Page object
    session: Optional[Any] = None    # requests/httpx Session object
    headers: Dict[str, str] = field(default_factory=dict)
    cookies: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
